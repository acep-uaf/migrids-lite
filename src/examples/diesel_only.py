import migrids_lite as mlt
import pandas as pd

# QOL for printing
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# get all the data
all_data = pd.read_csv('example_data.tab', delimiter='\t')

# get the electric load from the data
electric_load = mlt.EnergyType.EnergyType('electric_load', all_data['load'])

# create a generator, this one is 400 kW
four_hund = mlt.Generator.Generator('four_hund', 400, 0.30, {0.50: 14, 1.00: 28})

# build the power house, this is required even if there's only 1 generator
power_house = mlt.Powerhouse.Powerhouse((four_hund,))

# calculate diesel only usage
diesel_src = mlt.System.System(electric_load, power_house, 'd')

# print some useful things
print(diesel_src.src.vitals)
print(diesel_src.fuel_usages.totals)
