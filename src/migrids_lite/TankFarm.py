from migrids_lite import Powerhouse as powhaus
import pandas as pd

class TankFarm:
    def __init__(self, power_house: powhaus, vitals: pd.DataFrame):
        self.kraftwerk = power_house
        self.frame = vitals
        self.usages = pd.DataFrame()
        self.totals = dict()
        self.inter = pd.DataFrame()

        # needs to be from index 1 since initialization from 0 happens at the zero index
        self.inter['gen_combo'] = self.frame['diesel_out'][1:].apply(self.kraftwerk.find_cap_combo)
        self.inter['diesel_out'] = self.frame['diesel_out'][1:]
        self.usages['gen_power'] = self.inter.apply(lambda x: self.kraftwerk.calc_gen_load(x['diesel_out'], x['gen_combo']), axis=1)
        self.usages['gen_fuel_used'] = self.usages.apply(lambda x: self.kraftwerk.calc_gen_fuel(x['gen_power']), axis=1)
        self.usages['timestep_fuel_used'] = self.usages.apply(lambda x: sum(x['gen_fuel_used'].values()), axis=1)

        self.frame = pd.concat([self.frame, self.usages], axis=1)

        self.totals['total_fuel_used'] = round(self.usages['timestep_fuel_used'].sum(), 3)
        self.totals['diesel_kwh_produced'] = round(self.frame['diesel_out'][1:].sum(), 3)
        self.totals['resource_kwh_curtailed'] = round(self.frame['resource_curtailed'][1:].sum(), 3)
        self.totals['diesel_excess'] = round(self.frame['diesel_excess'][1:].sum(), 3)

        # since the different have different numbers of columns & the resource kwh produced calculation depends on the
        # battery, they need to be calculated differently
        if len(self.frame.columns) > 3:
            self.totals['resource_kwh_produced'] = round(self.frame['resource'][1:].sum() -
                                                         self.frame['resource_curtailed'].sum(), 3)
        else:
            self.totals['resource_kwh_produced'] = round(self.frame['resource'][1:].sum(), 3)

        # get the total usages for each generator
        for generators in self.kraftwerk.gensets:
            gen_columns = self.usages['gen_fuel_used'].apply(lambda x: x[generators] if generators in x else 0)
            gen_hours = self.usages['gen_fuel_used'].apply(lambda x: 1 if generators in x else 0)
            self.totals['total_' + generators + '_fuel'] = round(gen_columns.sum(), 3)
            self.totals['total_' + generators + '_hours'] = round(gen_hours.sum(), 3)
