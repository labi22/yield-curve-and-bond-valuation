import numpy as np
from bond_engine.bond_pricer import price_bond, macaulay_duration, convexity

class BondPortfolio:
    def __init__(self, bonds, weights):
        """
        bonds   : list of Bond objects
        weights : portfolio weights (sum to 1)
        """
        self.bonds = bonds
        self.weights = np.array(weights)

    def price(self, yield_curve):
        prices = np.array([
            price_bond(b, yield_curve) for b in self.bonds
        ])
        return np.sum(self.weights * prices)

    def duration(self, yield_curve):
        prices = np.array([
            price_bond(b, yield_curve) for b in self.bonds
        ])
        durations = np.array([
            macaulay_duration(b, yield_curve) for b in self.bonds
        ])

        portfolio_value = np.sum(self.weights * prices)
        return np.sum(self.weights * prices * durations) / portfolio_value

    def convexity(self, yield_curve):
        convexities = np.array([
            convexity(b, yield_curve) for b in self.bonds
        ])
        return np.sum(self.weights * convexities)

    def future_value(self, yield_curve, horizon):
        fv = 0.0
        for bond, w in zip(self.bonds, self.weights):
            times, cashflows = bond.cashflows()
            for t, cf in zip(times, cashflows):
                if t <= horizon:
                    # reinvest to horizon
                    r = yield_curve.rate(horizon - t)
                    fv += w * cf * np.exp(r * (horizon - t))
        return fv
