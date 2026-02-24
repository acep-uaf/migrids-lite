# import Generator as dgs
from itertools import combinations, chain

import pandas as pd

from migrids_lite import EnergyInputs as Ein

def powerset(iterable):
    """
    find the combinations of all the generators
    :param iterable: an iterable
    :return: list of tuples with all the combinations of keys
    """
    s = iterable.keys()
    return list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))

class Powerhouse:
    def __init__(self, gensets: tuple):
        self.gensets = {item.ident: item for item in gensets}
        self.gendict_mol = {item.ident:item.mol for item in gensets}
        self.gencombos = powerset(self.gendict_mol)
        self.gendict_cap = {item.ident:item.capacity for item in gensets}
        self.min_mol = min(self.gendict_mol.values())
        self.capacity = max(self.gendict_cap.values())

        # for no loads
        self.gendict_cap['off'] = 0
        self.gendict_mol['off'] = 0

        # finding all the possible combinations of the minimum operating load
        self.combo_mol_caps = {}
        for combos in self.gencombos:
            if not combos:
                self.combo_mol_caps[('off',)] = 0
                # skipping 0 generation. let's see how this affects downstream behavior in the future
                # ^ bad developer. should have considered 0 load
                # adding zero makes finding the min combo act weird and messes up the battery
                continue
            else:
                gen_mol_sum = 0
                for gens in combos:
                    gen_mol_sum += self.gendict_mol[gens]
                self.combo_mol_caps[combos] = gen_mol_sum

        self.combo_caps = {}
        for combos in self.gencombos:
            if not combos:
                self.combo_caps[0] = ('off',)
            else:
                gen_sum = 0
                for gens in combos:
                    gen_sum += self.gendict_cap[gens]
                self.combo_caps[gen_sum] = combos

        # sorting by order of magnitude
        # self.combo_mol_caps = dict(sorted(self.combo_mol_caps.keys()))
        # self.gencombos = tuple(self.combo_mol_caps.keys())

    def calc_gen_fuel(self, gen_loads: dict):
        """
        calculate the fuel usage of the generator combo
        :param gen_loads: dictionary of the timestep loading of the generator. key is generator ID
        and the value is the loading
        :return: the dict of the fuel usage, keys are generators and values are pandas dataframes
        """
        pwrhouse_usage = {gen: round(self.gensets[gen].calc_diesel_usage(gen_loads[gen]), 3)
                          for gen in gen_loads}
        return pwrhouse_usage

    def calc_gen_load(self, eload: float, select_combo: tuple):
        """
        calculate the per generator load
        :param eload: the overall load
        :param select_combo: the selected combination of the generators
        :return:
        """
        if select_combo is None:
            return {'None': 0}

        sum = 0
        if len(select_combo) == 1:
            sum = self.gendict_cap[select_combo[0]]
        else:
            for generator in select_combo:
                sum += self.gendict_cap[generator]

        if sum != 0:
            ratios = {item:self.gendict_cap[item]/sum for item in select_combo}
        else:
            # if the generators are off there is nothing to return
            return 0

        pwrhouse_pow = {gen: round(eload*ratios[gen], 3) for gen in select_combo}
        return pwrhouse_pow


    def find_cap_combo(self, cap_need: int):
        """
        find the generator combination needed given capacity
        :param cap_need: generation capacity needed
        :return: generator combination
        """
        if pd.isna(cap_need):
            return None
        elif cap_need == 0:
            return ('off',)

        try:
            cap_above = {cap:combo for (cap, combo) in self.combo_caps.items() if cap >= cap_need}
            gen_combo = cap_above[min(cap_above.keys(), key = lambda key: abs(key-cap_need))]
            return gen_combo
        except:
            raise Exception('Invalid capacity: requested capacity is outside of powerhouse capacity') from None

    def find_mol(self, combo: tuple):
        """
        find the minimum operating load given a key
        :param combo: tuple key for the dictionary
        :return: mol
        """
        return self.combo_mol_caps[combo]



if __name__ == "__main__":
    import migrids_lite as mlt

    twohundy = mlt.Generator.generic_two_hundred('twohundy')
    tenfiddy = mlt.Generator.generic_ten_fifty('tenfiddy')
    fohundy = mlt.Generator.Generator('fohundy', 400, 0.30,  {0.50: 14, 1: 28})
    pwrhouse = mlt.Powerhouse.Powerhouse((twohundy, tenfiddy, fohundy))
    print(pwrhouse.combo_mol_caps)

# {('off',): 0, ('twohundy',): 50.0, ('tenfiddy',): 262.5, ('fohundy',): 120.0, ('twohundy', 'tenfiddy'): 312.5,
# ('twohundy', 'fohundy'): 170.0, ('tenfiddy', 'fohundy'): 382.5, ('twohundy', 'tenfiddy', 'fohundy'): 432.5}
