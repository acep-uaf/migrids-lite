import pandas as pd
from migrids_lite import EnergyType as EType
from migrids_lite import EnergyInputs as EIn
from migrids_lite import Powerhouse as powhouse
import warnings


class SrcLimits:
    def __init__(self, inputs: EIn.EnergyInputs, power_house: powhouse):
        self.elec_load = inputs.electric_load
        self.resource = inputs.resource
        self.calc_frame = pd.DataFrame()
        self.powerhouse = power_house

    def poss_res_import(self):
        """
        calculates the possible resource imports and creates 'poss_grid_import' column
        """
        self.calc_frame['poss_grid_import'] = pd.concat([self.elec_load['electric_load'],
                                                          self.resource['resource']], axis = 1).min(axis = 1)

    def load_src(self, src_multiplier: float = 0.1):
        """
        calculates the load spinning reserve capacity and creates 'load_src' column
        :param src_multiplier: the spinning reserve capacity in percentage as decimal
        """
        self.calc_frame['load_src'] = self.elec_load['electric_load'].multiply(src_multiplier+1)

    def diesel_src_req(self, ess_power_cap: float):
        """
        calculates the diesel generator spinning reserve capacity and creates 'diesel_src_req' column
        :param ess_power_cap: power output capacity of the energy storage system in kW
        """
        self.calc_frame['diesel_src_req'] = self.calc_frame['load_src'].subtract(ess_power_cap)

    def dummy_diesel(self):
        """
        calculates an intermediate variable later to be used stored in 'dummy diesel'...
        """
        self.calc_frame['dummy_diesel'] = self.elec_load['electric_load'] - self.resource['resource']

    def src_diesel_cap_need(self, resource_src_multi: float = 1):
        """
        calculates the diesel capacity required, which is the max between 'diesel_src_req' and 'dummy_diesel'
        :param resource_src_multi: spinning reserve multiplier in percent as decimal
        """
        unclip_diesel_cap = pd.concat([self.calc_frame['diesel_src_req'],
                                       resource_src_multi*self.calc_frame['dummy_diesel']], axis=1).max(axis=1)
        self.calc_frame['src_diesel_capacity'] = unclip_diesel_cap.clip(1, None)

    def src_diesel_cap_combo(self):
        self.calc_frame['src_diesel_combo'] = self.calc_frame['src_diesel_capacity'].apply(self.powerhouse.find_cap_combo)

    def src_diesel_out(self):
        """
        calculates the actual diesel output based on minimum operating load of the diesel
        :param min_operating_load: minimum operating load of the diesel in kW
        """
        if self.powerhouse.min_mol > self.elec_load['electric_load'][1:].min():
            warnings.warn('Electric load below powerhouse minimum operating load: the electric load has 1 or more '
                          'instances where its value is below the minimum output of the powerhouse. '
                          'Energy balance calculations may be invalid', stacklevel=4)

        self.calc_frame['src_diesel_output'] = self.calc_frame['dummy_diesel'].clip(self.powerhouse.min_mol, None)

    def dsrc_resource_out(self):
        """
        calculates the dummy src limited resource output to be used in future calculations
        """
        dummy_r_out = self.elec_load['electric_load'] - self.calc_frame['src_diesel_output']
        # limiting to 0 since there's some calcs downstream that accept negative values
        self.calc_frame['dsrc_resource_out'] = dummy_r_out.clip(0, None)


    def dsrc_resource_surplus(self):
        """
        calculates the dummy src limited resource excess used in future calculations in Timeshifting
        :return:
        """
        self.calc_frame['dsrc_surplus'] = self.resource['resource'] - self.calc_frame['dsrc_resource_out']

    def calc_all(self, ess_power_cap: float, src_multi: float = 0.1, re_src_multi: float = 1):
        """
        calculates all the parameters for the SRC limited case
        :param ess_power_cap:
        :param src_multi: src multiplier in percentage as decimal
        :param re_src_multi: resource spinning reserve multiplier in percentage as decimal
        :return:
        """
        self.poss_res_import()
        self.load_src(src_multi)
        self.diesel_src_req(ess_power_cap)
        self.dummy_diesel()
        self.src_diesel_cap_need(re_src_multi)
        self.src_diesel_cap_combo()
        self.src_diesel_out()
        self.dsrc_resource_out()
        self.dsrc_resource_surplus()