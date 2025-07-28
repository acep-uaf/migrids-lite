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
# the just 1 resource isn't enough to use the battery, so we make the resource bigger by a multiplier
solar_energy = mlt.EnergyType.EnergyType('resource', all_data['solar_energy'], multiplier=3)

# create a generator, this one is 400 kW
four_hund = mlt.Generator.Generator('four_hund', 400, 0.30, {0.50: 14, 1.00: 28})

# build the power house, this is required even if there's only 1 generator
power_house = mlt.Powerhouse.Powerhouse((four_hund,))

# build the battery called 'example_batt', rated input is 50 kW, output is 100 kW,
# and capacity is 100 kWh, minimum capacity percent is 30
battery = mlt.Storage.Storage('example_batt', 100, 50, 100, 0.3)

# calculate in storage time shifting mode
gen_shifting = mlt.System.System(electric_load, power_house, 's', storage=battery, resource_input=solar_energy)


print(gen_shifting.vitals.frame)