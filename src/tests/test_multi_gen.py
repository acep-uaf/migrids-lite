import migrids_lite as mlt
import pandas as pd
import numpy as np
import pytest

# QOL for printing
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# having one generator twice the size of the other makes things simple
four_hund = mlt.Generator.Generator('four_hund', 400, 0.30, {0.50: 14, 1.00: 28})
two_hund = mlt.Generator.Generator('two_hund', capacity=200, mol_percent=0.35, fuel_usage={0.5: 7, 1.00: 14})

power_house = mlt.Powerhouse.Powerhouse((four_hund, two_hund))

# one for big gen, one for both gen, one for small gen
load_df = pd.DataFrame([300, 500, 100])
electric_load = mlt.EnergyType.EnergyType('electric_load', load_df)

diesel_only = mlt.System.System(electric_load, power_house, calc_mode='d')
print(diesel_only)

def test_load_share():
    """
    make sure the loads are properly shared between generators
    :return:
    """
    verifyer = pd.Series([np.nan, {'four_hund': 300}, {'four_hund': 500*400/600, 'two_hund': 500*200/600}, {'two_hund': 100}])

    assert pd.testing.assert_series_equal(verifyer, diesel_only.vitals.frame['gen_power'], check_names=False) is None