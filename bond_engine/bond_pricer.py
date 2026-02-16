import numpy as np
from scipy.optimize import brentq


class Bond:
    def __init__(
        self,
        face_value: float,
        coupon_rate: float,
        maturity: float,
        frequency: int = 2
    ):
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.maturity = maturity
        self.frequency = frequency

    def cashflows(self):
        n_periods = int(self.maturity * self.frequency)
        times = np.array([(i + 1) / self.frequency for i in range(n_periods)])

        coupon = self.face_value * self.coupon_rate / self.frequency
        cashflows = np.full(n_periods, coupon)
        cashflows[-1] += self.face_value

        return times, cashflows


def price_bond(bond: "Bond", yield_curve):
    times, cashflows = bond.cashflows()

    price = 0.0
    for t, cf in zip(times, cashflows):
        price += cf * yield_curve.discount_factor(t)

    return price


def yield_to_maturity(bond: "Bond", market_price: float):
    times, cashflows = bond.cashflows()

    def price_diff(y):
        return sum(
            cf * np.exp(-y * t)
            for cf, t in zip(cashflows, times)
        ) - market_price

    return brentq(price_diff, 1e-6, 0.5)

def macaulay_duration(bond: "Bond", yield_curve):
    """
    Macaulay Duration using full yield curve
    """
    times, cashflows = bond.cashflows()
    price = price_bond(bond, yield_curve)

    weighted_sum = 0.0
    for t, cf in zip(times, cashflows):
        df = yield_curve.discount_factor(t)
        weighted_sum += t * cf * df

    return weighted_sum / price

def modified_duration(bond: "Bond", yield_curve):
    """
    Modified Duration from Macaulay Duration
    """
    D_mac = macaulay_duration(bond, yield_curve)

    # Use yield at bond maturity as approximation
    y = yield_curve.rate(bond.maturity)

    return D_mac / (1 + y)

def convexity(bond: "Bond", yield_curve):
    """
    Bond convexity using full yield curve
    """
    times, cashflows = bond.cashflows()
    price = price_bond(bond, yield_curve)

    conv = 0.0
    for t, cf in zip(times, cashflows):
        df = yield_curve.discount_factor(t)
        conv += cf * df * (t ** 2)

    return conv / price