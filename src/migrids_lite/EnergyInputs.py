from migrids_lite import EnergyType
import pandas as pd
class EnergyInputs:
    def __init__(self, first_input: EnergyType.EnergyType, second_input: EnergyType.EnergyType):
        self.resource = pd.DataFrame()
        self.electric_load = pd.DataFrame()
        if (first_input.energy_type == 'resource') and (second_input.energy_type == 'electric_load'):
            self.resource['resource'] = first_input.data
            self.electric_load['electric_load'] = second_input.data
        elif (first_input.energy_type == 'electric_load') and (second_input.energy_type == 'resource'):
            self.resource['resource'] = second_input.data
            self.electric_load['electric_load'] = first_input.data
        else:
            raise Exception('Error: one input must be of type \'resource\' and the other must be of type '
                            '\'electric_load\'')
