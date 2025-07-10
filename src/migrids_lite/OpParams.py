class OpParams:
    def __init__(self, src_mult: float = 0.1, resource_src_mult: float = 1, batt_reset: float = 0,
                 residual_cutoff: float = 0.005):
        """
        Define operational parameters for the System
        :param src_mult: spinning reserve capacity multiplier for the electrical load in percent as decimal.
        default is 10% or 0.1
        :param resource_src_mult: spinning reserver capacity multiplier for the resource in percent as decimal.
        default is 100% or 1
        :param batt_reset: battery reset percentage as decimal. default is 0% or minimum rated charge, depending on
        battery
        :param residual_cutoff: residual cutoff value for the iteration. default is 0.005 or 0.5% change from the
        previous iteration
        """
        self.src_mult = src_mult
        self.resource_src_mult = resource_src_mult
        self.batt_reset = batt_reset
        self.residual_cutoff = residual_cutoff