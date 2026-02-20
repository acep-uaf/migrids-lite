import pandas as pd

from migrids_lite import SrcLimits as srcl
from migrids_lite import EnergyInputs as e_inp
from migrids_lite import EnergyType as e_type
from migrids_lite import TankFarm as tanks
from migrids_lite import Powerhouse as powhaus
from migrids_lite import Timeshifting as tshift
from migrids_lite import Storage as stor
from migrids_lite import OpParams as opper



class System:
    def __init__(self, load_input: e_type.EnergyType, power_house: powhaus.Powerhouse, calc_mode: str, storage: stor.Storage = None,
                 resource_input: e_type.EnergyType = None, oper_params: opper.OpParams = None):
        """
        build and calculate fuel usage and/or fuel offset of the system according to the calculation mode. diesel only,
        resource offset, and storage time shifting modes.
        :param load_input: the electric load
        :param power_house: the built powerhouse of the system
        :param calc_mode: 'd' diesel only mode, calculates fuel usage without renewable energy resource.
        'r' resource offset mode, calculates system behavior with only resource and spinning reserve constraints.
        's' storage time shifting mode, calculates system behavior with battery and spinning reserve constraints.
        :param storage: the battery storage for the system. not required for diesel only and resource only modes;
        required for storage mode
        :param resource_input: the resource available. not required for diesel only mode, required for resource offset
        and storage timeshift mode.
        :param oper_params: operational parameters object, with items such as src multiplier and battery reset value
        """

        # get the default operational parameters if they are not defined
        if oper_params is None:
            oper_params = opper.OpParams()

        if calc_mode == 'd' or calc_mode == 'diesel only':
            print('calculating in diesel only mode')

            # create a 0 kW resource dataframe
            no_resource = e_type.EnergyType('resource')
            no_resource.zeros(len(load_input.data))

            # data object for calculating in SrcLimits
            data_in = e_inp.EnergyInputs(no_resource, load_input)

            self.src = srcl.SrcLimits(data_in, power_house)
            self.src.calc_all(0, src_multi = oper_params.src_mult,
                              re_src_multi = oper_params.resource_src_mult)

            # convert the column names to be compatible with TankFarm
            self.src.vitals = pd.DataFrame()
            self.src.vitals['diesel_out'] = self.src.calc_frame['src_diesel_output']
            self.src.vitals['resource'] = self.src.calc_frame['dsrc_resource_out']
            self.src.vitals['curtailed'] = self.src.calc_frame['dsrc_surplus']

            self.vitals = tanks.TankFarm(power_house, self.src.vitals)


        elif calc_mode == 'r' or calc_mode == 'resource offset':
            print('calculating in resource offset mode')

            try:
                data_in = e_inp.EnergyInputs(resource_input, load_input)
            except:
                raise Exception('resource input error, make sure that the resource input is properly imported')

            self.src = srcl.SrcLimits(data_in, power_house)
            self.src.calc_all(0, src_multi=oper_params.src_mult,
                            re_src_multi=oper_params.resource_src_mult)

            # convert the column names to be compatible with TankFarm
            self.src.vitals = pd.DataFrame()
            self.src.vitals['diesel_out'] = self.src.calc_frame['src_diesel_output']
            self.src.vitals['resource'] = self.src.calc_frame['dsrc_resource_out']
            self.src.vitals['curtailed'] = self.src.calc_frame['dsrc_surplus']

            self.vitals = tanks.TankFarm(power_house, self.src.vitals)


        elif calc_mode == 's' or calc_mode == 'storage timeshift':
            print('calculating in storage timeshift mode')

            if storage is None:
                raise Exception('battery not defined, make sure to define the battery before calling this function')

            try:
                data_in = e_inp.EnergyInputs(resource_input, load_input)
            except:
                raise Exception('resource input error, make sure that the resource input is properly imported')

            self.src = srcl.SrcLimits(data_in, power_house)
            self.src.calc_all(storage.rated_discharge, src_multi=oper_params.src_mult,
                              re_src_multi=oper_params.resource_src_mult)
            print(self.src.calc_frame)
            self.shift = tshift.Timeshift(storage, self.src, oper_params)
            self.shift.calc(residual_cutoff=oper_params.residual_cutoff, batt_reset=oper_params.batt_reset)
            self.shift.get_vitals()

            # self.vitals = tanks.TankFarm(power_house, self.shift.vitals)

        else: raise Exception('unrecognized mode')