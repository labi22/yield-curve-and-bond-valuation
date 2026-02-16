import numpy as np


class ShockedYieldCurve:
    def __init__(self, base_curve, shock_bp: float):
        """
        base_curve : original YieldCurve
        shock_bp   : parallel shock in basis points (e.g. +50, -100)
        """
        self.base_curve = base_curve
        self.shock = shock_bp / 10000  # bp → decimal

    def rate(self, maturity):
        return self.base_curve.rate(maturity) + self.shock

    def discount_factor(self, maturity):
        r = self.rate(maturity)
        return np.exp(-r * maturity)