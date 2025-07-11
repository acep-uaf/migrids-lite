import migrids_lite as mlt
import pandas as pd
from random import randrange
import timeit

# QOL for printing
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# epath = ['..', 'data', 'Jeremy', 'testbed_load.txt']
# rpath = ['..', 'data', 'nju', 'resource.txt']

# elec_load = mlt.GetElectricLoad(r'..\testbed_load.txt')
# print(elec_load.data)

testload = [randrange(120, 800) for x in range(0, 8760)]
testresource = [randrange(200, 800) if x < 4000 else 0 for x in range(0, 8760)]
#
#
e_loads = mlt.EnergyType.EnergyType('electric_load', pd.DataFrame(testload))
# e_loads = mlt.EnergyType.EnergyType('electric_load')
# e_loads.get_data(r'../testbed_load.txt')
# print(e_loads.data)
resources = mlt.EnergyType.EnergyType('resource', pd.DataFrame(testresource))

e_in = mlt.EnergyInputs.EnergyInputs(e_loads, resources)

fohundy = mlt.Generator.Generator('fohundy', 400, 0.30, {0.50: 14, 1.00: 28})
fotoo = mlt.Generator.Generator('fotoo', 400, 0.30, {0.50: 14, 1.00: 28})
pwrhouse = mlt.Powerhouse.Powerhouse((fohundy, fotoo))

vrla = mlt.Storage.Storage('vrla', 100, 100, 1000, 0.3)

t1 = timeit.default_timer()

src = mlt.SrcLimits.SrcLimits(e_in, pwrhouse)
# print(pwrhouse.combo_mol_caps)
src.calc_all(vrla.rated_discharge)

testshifting = mlt.Timeshifting.Timeshift(vrla, src)
testshifting.calc(batt_reset=0.3, residual_cutoff=0.1)
testshifting.get_vitals()

tanks = mlt.TankFarm.TankFarm(pwrhouse, testshifting.vitals)

t2 = timeit.default_timer()

print(t2-t1)
# print(tanks.usages)
print(testshifting.vitals)
# print(tanks.totals)
