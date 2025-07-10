import pandas as pd
from migrids_lite import SrcLimits as slim
from migrids_lite import Storage as stor


def residuals(old_soc: pd.Series, new_soc: pd.Series):
    """
    find the residuals in percent between the new and old iteration
    :param old_soc: old battery state of charge
    :param new_soc: new battery state of charge
    :return: residuals as an absolute percent of the old value
    """
    numerator = abs(old_soc - new_soc)
    # so the denominator isn't 0
    denom = old_soc.apply(lambda x: x if x > 0 else 1)
    resid = numerator.div(denom, fill_value=0)

    return resid


class Timeshift:
    def __init__(self, storage: stor, spinlims: slim):
        # initialize all the variables
        self.storage = storage
        self.init_frame = spinlims.calc_frame
        self.elec_load = spinlims.elec_load
        self.resource = spinlims.resource
        self.powerhouse = spinlims.powerhouse
        self.static_frame = pd.DataFrame()
        self.new_frame = pd.DataFrame()
        self.vitals = pd.DataFrame()

        # calculating the timeseries charge by the minimum between the resource surplus and rated charge
        # max(rated charge, resource surplus)
        self.init_frame['storage_charge_max'] = self.init_frame['dsrc_surplus'].clip(None, storage.rated_charge)

        # calculating the timeseries discharge by the minimum between load minus resource surplus and rated discharge
        # max(rated discharge, load-resource)
        self.init_frame['storage_discharge_max'] = (self.elec_load['electric_load'] -
                                                    self.init_frame['dsrc_resource_out']).clip(None, storage.rated_discharge)

        # get the charge or discharge
        charge_discharge = pd.concat([self.init_frame['storage_charge_max'], self.init_frame['storage_discharge_max']],
                                    axis=1)

        # find the requested charge or discharge, discharge is negative
        self.init_frame['storage_requested'] = charge_discharge.apply(lambda x: x['storage_charge_max'] if
                                                                    x['storage_charge_max'] > 0 else
                                                                    -1*x['storage_discharge_max'], axis=1)


    def iterate(self, batt_soc: pd.Series, batt_reset: float = 0):
        """
        iterate over the battery state of charge once
        :param batt_soc: pandas series of the battery state of charge to iterate from
        :param batt_reset: reset value for the battery
        :return: the converged dataframe or return an error if it doesn't converge.
        """
        iter_frame = pd.DataFrame()

        # charging battery
        charge = (batt_soc - self.storage.rated_min_percent).clip(0, self.storage.rated_charge)
        charge = charge.diff() * self.storage.rated_storage
        iter_frame['charge'] = charge.clip(0, self.storage.rated_charge)

        # possible discharge battery
        discharge_poss = pd.DataFrame()
        discharge_poss['soc_mag'] = (batt_soc.shift(1) - self.storage.rated_min_percent) * self.storage.rated_storage
        discharge_poss['poss'] = -1*discharge_poss['soc_mag'].clip(0, self.storage.rated_discharge)
        dummy_dis = pd.concat([iter_frame['charge'], discharge_poss['poss']], axis=1)
        dis_poss = dummy_dis.apply(lambda x: 0 if x['charge'] > 0 else x['poss'], axis=1)
        iter_frame['discharge_poss'] = dis_poss
        iter_frame['diesel_out_poss'] = (self.static_frame['electric_load'] - self.static_frame['resource'] +
                                         iter_frame['discharge_poss'])

        # diesel cap
        diesel_cap_req = pd.concat([self.init_frame['diesel_src_req'], iter_frame['diesel_out_poss']], axis=1)
        iter_frame['diesel_cap_req'] = diesel_cap_req.max(axis=1)

        min_mol = min(self.powerhouse.combo_mol_caps, key=self.powerhouse.combo_mol_caps.get)
        iter_frame['diesel_out'] = iter_frame['diesel_out_poss'].clip(self.powerhouse.combo_mol_caps[min_mol], None)

        iter_frame['discharge'] = -1 * (self.static_frame['electric_load'] - self.static_frame['resource_to_load'] -
                                        iter_frame['diesel_out'])

        charge_dis = pd.concat([iter_frame['charge'], iter_frame['discharge']], axis=1)
        iter_frame['charge_dis'] = charge_dis.apply(lambda x: x['charge'] if x['charge'] > 0 else x['discharge'], axis=1)

        # recalculating soc
        self.storage.reset(batt_reset)
        iter_frame['soc'] = iter_frame['charge_dis'].apply(self.storage.calc_soc)

        return iter_frame

    # calculate after all the parameters are initialized
    def calc(self, residual_cutoff: float = 0.005, batt_reset: float = 0):
        self.static_frame = pd.DataFrame()
        self.static_frame['electric_load'] = self.elec_load
        self.static_frame['resource'] = self.resource
        self.static_frame['resource_to_load'] = self.init_frame['dsrc_resource_out']

        init_soc = self.init_frame['storage_requested'].apply(self.storage.calc_soc)

        self.new_frame = self.iterate(init_soc)
        resid = residuals(init_soc, self.new_frame['soc'])

        resid_flag = (resid >= residual_cutoff).any()
        iter_number = 0
        while resid_flag and iter_number < len(init_soc):
            this_soc = self.new_frame['soc']
            self.new_frame = self.iterate(self.new_frame['soc'], batt_reset)
            resid = residuals(this_soc, self.new_frame['soc'])
            resid_flag = (resid >= residual_cutoff).any()
            iter_number += 1


        return self.new_frame, iter_number

    def get_vitals(self):
        """
        get the "vital" information columns from the static frame and the calculated frame
        :return:
        """
        self.vitals = pd.concat([self.static_frame[['electric_load', 'resource', 'resource_to_load']],
                            self.new_frame[['diesel_out', 'charge_dis', 'soc']]], axis=1)
        self.vitals['curtailed'] = (self.vitals['resource'] - self.vitals['resource_to_load'] -
                                    self.vitals['charge_dis'].clip(0, None))

        return self.vitals
