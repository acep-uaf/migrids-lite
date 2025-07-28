import migrids_lite as mlt
import pandas as pd

# QOL for printing
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# get all the data
all_data = pd.read_csv('example_data.tab', delimiter='\t')

# get the electric load from the data
electric_load = mlt.EnergyType.EnergyType('electric_load', all_data['load'])

# get the resource available
solar_energy = mlt.EnergyType.EnergyType('resource', all_data['solar_energy'])

# create a generator, this one is 400 kW
four_hund = mlt.Generator.Generator('four_hund', 400, 0.30, {0.50: 14, 1.00: 28})

# build the power house, this is required even if there's only 1 generator
power_house = mlt.Powerhouse.Powerhouse((four_hund,))

resource_offset = mlt.System.System(electric_load, power_house, 'r', resource_input=solar_energy)

# print some useful things
print(resource_offset.src.frame)
print(resource_offset.fuel_usages.totals)