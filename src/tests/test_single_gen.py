import migrids_lite as mlt
import pandas as pd
import numpy as np
import pytest

# QOL for printing
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


all_data = pd.read_csv('../examples/example_data.tab', delimiter='\t')

electric_load = mlt.EnergyType.EnergyType('electric_load', all_data['load'])

solar_energy = mlt.EnergyType.EnergyType('resource', all_data['solar_energy'], multiplier=3)

# create a generator, this one is 400 kW
four_hund = mlt.Generator.Generator('four_hund', 400, 0.30, {0.50: 14, 1.00: 28})
power_house = mlt.Powerhouse.Powerhouse((four_hund,))

battery = mlt.Storage.Storage('example_batt', 50, 100, 100, 0.3)

# calculate in storage time shifting mode
gen_shifting = mlt.System.System(electric_load, power_house, 's', storage=battery, resource_input=solar_energy)

def test_total_energy_timestep():
    """
    make sure the load is being met by the generator, resource, and battery for each timestep
    :return:
    """
    discharge = -1 * gen_shifting.vitals.frame['charge_dis'].mask(gen_shifting.vitals.frame['charge_dis'] > 0).fillna(0)
    resource_to_load = gen_shifting.vitals.frame['resource_to_load']
    diesel_out = gen_shifting.vitals.frame['diesel_out']

    energy_to_load = discharge + resource_to_load + diesel_out
    load = gen_shifting.vitals.frame['electric_load'].astype(np.float64)

    assert pd.testing.assert_series_equal(load, energy_to_load.fillna(0), check_names=False) is None

def test_total_gen_energy_run():
    """
    make sure the total gen kWh is the same as the vitals.totals
    :return:
    """
    frame_diesel_total = gen_shifting.vitals.frame['diesel_out'].sum()
    totals_diesel_total = gen_shifting.vitals.totals['diesel_kwh_produced']

    assert totals_diesel_total == pytest.approx(frame_diesel_total)

# def test_total_resource_run():
#     """
#     make the total resource kWh used is the same as the vitals.totals
#     :return:
#     """
#