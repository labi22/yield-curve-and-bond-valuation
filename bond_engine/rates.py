import numpy as np


def zero_rate(yield_curve, maturity):
    """
    Spot (zero-coupon) rate for maturity t
    """
    return yield_curve.rate(maturity)


def forward_rate(yield_curve, t1, t2):
    """
    Implied forward rate between t1 and t2
    (continuous compounding)
    """
    r1 = yield_curve.rate(t1)
    r2 = yield_curve.rate(t2)

    return (r2 * t2 - r1 * t1) / (t2 - t1)


def instantaneous_forward_rates(yield_curve, maturities):
    """
    Approximate instantaneous forward rates using
    numerical differentiation
    """
    dt = 1e-4
    forwards = []

    for t in maturities:
        r_plus = yield_curve.rate(t + dt)
        r_minus = yield_curve.rate(t - dt)
        fwd = (r_plus * (t + dt) - r_minus * (t - dt)) / (2 * dt)
        forwards.append(fwd)

    return np.array(forwards)