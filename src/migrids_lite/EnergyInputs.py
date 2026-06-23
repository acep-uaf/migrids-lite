from migrids_lite import EnergyType
import pandas as pd
class EnergyInputs:
    def __init__(self, first_input: EnergyType.EnergyType, second_input: EnergyType.EnergyType):
        self.resource = pd.DataFrame()
        self.electric_load = pd.DataFrame()
        if (first_input.energy_type == 'resource') and (second_input.energy_type == 'electric_load'):
            # if there is only one column, just use that column
            if first_input.data.shape[1] == 1:
                self.resource['resource'] = first_input.data
            else:
                # if there's multiple columns, try to find the resource column
                try:
                    self.resource['resource'] = first_input.data['resource']
                except: raise Exception("Error: no resource column found!")

            if second_input.data.shape[1] == 1:
                self.electric_load['electric_load'] = second_input.data
            else:
                try:
                    self.electric_load['electric_load'] = second_input.data['electric_load']
                except: raise Exception("Error: no load column found!")

        elif (first_input.energy_type == 'electric_load') and (second_input.energy_type == 'resource'):
            if first_input.data.shape[1] == 1:
                self.electric_load['electric_load'] = first_input.data
            else:
                try:
                    self.electric_load['electric_load'] = first_input.data['electric_load']
                except: raise Exception("Error: no load column found!")

            if second_input.data.shape[1] == 1:
                self.resource['resource'] = second_input.data
            else:
                try:
                    self.resource['resource'] = second_input.data['resource']
                except: raise Exception("Error: no resource column found!")
        else:
            raise Exception('Error: one input must be of type \'resource\' and the other must be of type '
                            '\'electric_load\'')
