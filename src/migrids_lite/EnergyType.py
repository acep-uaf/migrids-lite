import pandas as pd
# from os import path
# import warnings

# not needed
# def agnostic_joiner(input_path: list):
#     """
#     Joins paths agnostic of OS
#     :param input_path: list of directories from the current working directory to the file
#     :return: proper path as string
#     """
#
#     return str(path.join(*input_path))

class EnergyType:
    def __init__(self, energy_type: str, data: pd.DataFrame= None, multiplier: float = 1):
        if energy_type == 'electric_load' or energy_type == 'resource':
            self.energy_type = energy_type.lower()
        else:
            raise Exception('Invalid energy type. Must be \'electric_load\' or \'resource\'')
        # start everything from 0
        if data is not None:
            self.data = pd.concat([pd.DataFrame({0, 0}), data], ignore_index=True)
            self.data = self.data.multiply(multiplier)
        else:
            # empty dataframe to filled in later with get data
            self.data = pd.DataFrame()

        # not sure if useful for command line migrids lite
        # if len(self.data.index) != 8760:
        #     warnings.warn('Data length does not equal 8760 hours or 1 year!')

    def get_data(self, data_path: str, data_name: str = 'data', multiplier: float = 1):
        """
        gets the data with the option of custom names. expected units are kW
        :param data_path: path to file from current working directory
        :param data_name: name of the load
        :param multiplier: multiply the load by this much
        """
        raw_data = pd.read_csv(data_path, header=None, names=[data_name + '_' + str(self.energy_type)])
        raw_data = raw_data.multiply(multiplier)
        zero_init = pd.concat([pd.DataFrame([0], [0], [data_name + '_' + str(self.energy_type)]), raw_data],
                              ignore_index=True)
        self.data = pd.concat([self.data, zero_init], axis=1)

        # if len(self.data.index) != 8760:
        #     warnings.warn('Data length does not equal 8760 hours or 1 year!')

    def sum_data(self):
        """
        sum data
        :return: summed electrical load in kW as dataframe column
        """
        self.data[str(self.energy_type)] = self.data.sum(axis=1)

    def zeros(self, length = int):
        """
        generate a 0 valued dataframe
        :param length: length of the dataframe
        :return: set the dataframe
        """
        self.data = pd.DataFrame([0 for x in range(0, length)])