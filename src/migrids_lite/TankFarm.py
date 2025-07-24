from migrids_lite import Powerhouse as powhaus
import pandas as pd

class TankFarm:
    def __init__(self, power_house: powhaus, vitals: pd.DataFrame):
        self.kraftwerk = power_house
        self.vitals = vitals
        self.usages = pd.DataFrame()
        self.totals = dict()
        inter = pd.DataFrame()

        # needs to be from index 1 since initialization from 0 happens at the zero index
        inter['gen_combo'] = self.vitals['diesel_out'][1:].apply(self.kraftwerk.find_cap_combo)
        inter['diesel_out'] = self.vitals['diesel_out'][1:]
        self.usages['gen_power'] = inter.apply(lambda x: self.kraftwerk.calc_gen_load(x['diesel_out'], x['gen_combo']), axis=1)
        self.usages['gen_fuel_used'] = self.usages.apply(lambda x: self.kraftwerk.calc_gen_fuel(x['gen_power']), axis=1)
        self.usages['timestep_fuel_used'] = self.usages.apply(lambda x: sum(x['gen_fuel_used'].values()), axis=1)

        self.vitals = pd.concat([self.vitals, self.usages], axis=1)

        self.totals['total_fuel_used'] = round(self.usages['timestep_fuel_used'].sum(), 3)
        self.totals['diesel_kwh_produced'] = round(self.vitals['diesel_out'][1:].sum(), 3)
        self.totals['resource_kwh_curtailed'] = round(self.vitals['curtailed'][1:].sum(), 3)

        # since the different have different numbers of columns & the resource kwh produced calculation depends on the
        # battery, they need to be calculated differently
        if len(self.vitals.columns) > 3:
            self.totals['resource_kwh_produced'] = round(self.vitals['resource'][1:].sum() -
                                                         self.vitals['curtailed'].sum(), 3)
        else:
            self.totals['resource_kwh_produced'] = round(self.vitals['resource'][1:].sum(), 3)

        # get the total usages for each generator
        for generators in self.kraftwerk.gensets:
            gen_columns = self.usages['gen_fuel_used'].apply(lambda x: x[generators] if generators in x else 0)
            gen_hours = self.usages['gen_fuel_used'].apply(lambda x: 1 if generators in x else 0)
            self.totals['total_' + generators + '_fuel'] = round(gen_columns.sum(), 3)
            self.totals['total_' + generators + '_hours'] = round(gen_hours.sum(), 3)
