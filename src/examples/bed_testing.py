import migrids_lite as mlt
import pandas as pd
from random import randrange
# import timeit

# QOL for printing
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# epath = ['..', 'data', 'Jeremy', 'testbed_load.txt']
# rpath = ['..', 'data', 'nju', 'resource.txt']

# elec_load = mlt.GetElectricLoad(r'..\testbed_load.txt')
# print(elec_load.data)

testload = [randrange(300, 1000) for x in range(0, 40)]
testresource = [randrange(200, 300) if x < 4000 else 0 for x in range(0, 40)]
#
#
e_loads = mlt.EnergyType.EnergyType('electric_load', pd.DataFrame(testload))
# e_loads = mlt.EnergyType.EnergyType('electric_load')
# e_loads.get_data(r'../testbed_load.txt')
# print(e_loads.data)
resources = mlt.EnergyType.EnergyType('resource', pd.DataFrame(testresource))

e_in = mlt.EnergyInputs.EnergyInputs(e_loads, resources)

fohundy = mlt.Generator.Generator('fohundy', 400, 0.50, {0.50: 14, 1.00: 28})
sixhundy = mlt.Generator.Generator('sixhundy', 600, 0.50, {0.50: 21, 1.00: 42})
pwrhouse = mlt.Powerhouse.Powerhouse((fohundy, sixhundy))

vrla = mlt.Storage.Storage('vrla', 50, 100, 1000, 0.3)

gen_shifting = mlt.System.System(e_loads, pwrhouse, 's', vrla, resource_input=resources)

discharge = -1*gen_shifting.vitals.frame['charge_dis'].mask(gen_shifting.vitals.frame['charge_dis'] > 0).fillna(0)
resource_to_load = gen_shifting.vitals.frame['resource_to_load']
diesel_out = gen_shifting.vitals.frame['diesel_out']

energy_to_load = discharge + resource_to_load + diesel_out
print(gen_shifting.vitals.frame)
print(gen_shifting.vitals.totals)

# t1 = timeit.default_timer()

# src = mlt.SrcLimits.SrcLimits(e_in, pwrhouse)
# # print(pwrhouse.combo_mol_caps)
# src.calc_all(vrla.rated_discharge)
#
# testshifting = mlt.Timeshifting.Timeshift(vrla, src)
# testshifting.calc(batt_reset=0.3, residual_cutoff=0.005)
# testshifting.get_vitals()
#
# tanks = mlt.TankFarm.TankFarm(pwrhouse, testshifting.frame)
#
# t2 = timeit.default_timer()
#
# print(t2-t1)
# print(tanks.usages)
# print(testshifting.frame)
# print(tanks.totals)
