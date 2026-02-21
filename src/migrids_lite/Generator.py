from warnings import warn
from types import NoneType

from scipy.stats import linregress
import pandas as pd


class Generator:
    def __init__(self, ident: str, capacity: float=None, mol_percent: float= None,
                 fuel_usage: dict= None):
        """
        define the generator characteristics
        :param capacity: nameplate of the generator in kW
        :param mol_percent: minimum operating load in percentage as decimal
        :param fuel_usage: keys in percent as decimal of loading, vals in gallons per hour
        """
        self.ident = ident
        self.capacity = capacity
        self.mol_percent = mol_percent
        self.fuel_usage = fuel_usage
        self.mol = self.mol_percent*self.capacity

        # operating below 20% is generally a bad idea
        if type(mol_percent) != NoneType and mol_percent < 0.2:
            warn('Warning: minimum operating load is set less than or 0.2 or 20%!')

        self.fuel_curve = linregress(list(fuel_usage.keys()), list(fuel_usage.values()))

        # warn if the fuel curve R squared is less than 0.9
        if self.fuel_curve.rvalue**2 <= 0.9:
            warn('Warning: fuel curve R squared is less than 0.9! Unreliable outputs may occur!')
        # exception if the fuel curve has negative slope
        if self.fuel_curve.slope <= 0:
             raise Exception('Error: fuel curve slope in wrong direction!')

    def calc_diesel_usage(self, e_load: float):
        if e_load > self.capacity:
            raise Exception('Error: out of bounds of generator envelope. Must be below ' + str(self.capacity) +
                            'kW')
        elif e_load <= self.mol:
            load_normed = self.mol_percent
        else:
            load_normed = e_load/self.capacity

        fuel_usage = load_normed*self.fuel_curve.slope + self.fuel_curve.intercept

        return fuel_usage


def generic_two_hundred(ident: str):
    """
    declare a generic 200 kW generator
    :param ident: identity of the generator
    :return: generator object
    """
    # generic fuel curve values are from AEA emissions report
    return Generator(ident, 200, 0.25, {0.50: 7.19, 1: 13.96})

def generic_ten_fifty(ident: str):
    """
    declare a generic 1050 kW generator
    :param ident: identity of the generator
    :return: generator object
    """
    return Generator(ident, 1050, 0.25, {0.50: 35.16, 1: 68.03})