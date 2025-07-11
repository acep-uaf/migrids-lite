import pandas as pd

class Storage:
    def __init__(self, ident: str, rated_in: float, rated_out: float, rated_storage: float,
                 rated_min_percent: float):
        """
        create the battery characteristics
        :param ident: identifier
        :param rated_in: rated input/charge battery in kW
        :param rated_out: rated output/discharge battery in kW
        :param rated_storage: rated energy capacity in kWh
        :param rated_min_percent: rated minimum capacity in percent as decimal
        """
        self.ident = ident
        self.rated_charge = rated_in
        self.rated_discharge = rated_out
        self.rated_storage = rated_storage
        self.rated_min_percent = rated_min_percent
        if self.rated_min_percent >= 1:
            raise Exception('rated minimum percent is greater than capacity!')
        # state of charge. begins at 0 and maximum of 100%
        self.soc = self.rated_min_percent
        self.storage_frame = pd.DataFrame()


    def calc_soc(self, requested: float):
        """
        calculate state of charge. Negative is discharge, positive is charge
        :param requested: requested charge/discharge value in kW.
        :return: excess charge/discharge
        """
        # NaN case, just treat it as zero
        if pd.isna(requested): requested = 0

        # everything is normalized to rated storage
        normed = requested/self.rated_storage

        if normed == 0: return self.soc # trivial case, not asking for charge/discharge

        #discharge case
        elif normed < 0:
            if self.soc <= self.rated_min_percent:
                self.soc = self.rated_min_percent
                return self.soc # battery empty
            else:
                # state of charge minus the normed rated discharge
                dummy_soc = self.soc - min(abs(normed), self.rated_discharge/self.rated_storage)
                # if the dummy_soc is bigger than soc, then the battery has fully discharged or reached rated minimum
                self.soc = max(dummy_soc, self.rated_min_percent)
        # charge case
        else:
            if self.soc == 1: return 1 # battery full
            else:
                # state of charge plus the normed rated charge
                dummy_soc = self.soc + min(normed, self.rated_charge/self.rated_storage)
                # if the dummy_soc makes the soc greater than 1, then the battery is fully charged
                self.soc = min(dummy_soc, 1)

        return self.soc

    def reset(self, set_val: float= 0):
        """
        this function resets the battery to its lowest value by default of a set value
        :paramL set_val: the battery set value in percent
        :return: none
        """
        self.soc = min([1, max(set_val, self.rated_min_percent)])


def vrla(ident: str, rated_cap: float):
    """
    defines a vrla battery. rated input is 100% rated capacity, rated output is 100% rated capacity
    and min percent is 20. this can also act as a NiMH battery.
    :param ident: identifier
    :param rated_out: rated discharge in kW
    :param rated_cap: rated capacity in kWh
    :return: Storage object
    """
    return Storage(ident, 1*rated_cap, 1*rated_cap, rated_cap, 0)

def nicad(ident: str, rated_cap: float):
    """
    defines a nickel-cadmium battery. rated input is 40% rated capacity, rated output is 100% rated capacity
    and min percent is 0
    :param ident: identifier
    :param rated_cap: rated capacity in kWh
    :return: Storage object
    """
    return Storage(ident, 0.4*rated_cap, 1*rated_cap, rated_cap, 0)

def liion(ident: str, rated_cap: float):
    """
    defines a lithium-ion battery. rated input is 80% rated capacity, rated output is 100% rated capcity
    and min percent is 0
    :param ident: identifier
    :param rated_cap: rated capacity in kWh
    :return: Storage object
    """
    return Storage(ident, 0.8 * rated_cap, 1 * rated_cap, rated_cap, 20)