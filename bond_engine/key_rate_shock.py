import numpy as np
from bond_engine.bond_pricer import price_bond

class KeyRateShockedCurve:
    def __init__(self, base_curve, key_rate, shock_bp):
        self.base = base_curve
        self.key_rate = key_rate
        self.shock = shock_bp / 10000  # bp → decimal

    def rate(self, maturity):
        bump = np.exp(-((maturity - self.key_rate) ** 2) / 0.5)
        return self.base.rate(maturity) + self.shock * bump

    def discount_factor(self, maturity):
        r = self.rate(maturity)
        return np.exp(-r * maturity)


def key_rate_duration(bond, yc, key_rate, shock_bp=1):
    base_price = price_bond(bond, yc)

    shocked_curve = KeyRateShockedCurve(yc, key_rate, shock_bp)
    shocked_price = price_bond(bond, shocked_curve)

    krd = -(shocked_price - base_price) / base_price / (shock_bp / 10000)
    return krd
