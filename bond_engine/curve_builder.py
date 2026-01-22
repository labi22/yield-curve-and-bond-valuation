import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline


MATURITY_MAP = {
    "1M": 1/12,
    "3M": 0.25,
    "6M": 0.5,
    "1Y": 1.0,
    "2Y": 2.0,
    "5Y": 5.0,
    "10Y": 10.0,
    "30Y": 30.0
}


class YieldCurve:
    def __init__(self, yields: pd.Series):
        """
        yields: pandas Series with index as maturity labels (1M, 3M, ...)
        """

        # Build and sort by maturity (CRITICAL)
        df = pd.DataFrame({
            "maturity": [MATURITY_MAP[m] for m in yields.index],
            "yield": yields.values
        }).sort_values("maturity")

        self.maturities = df["maturity"].values
        self.yields = df["yield"].values

        # Cubic spline interpolation
        self.curve = CubicSpline(
            self.maturities,
            self.yields,
            bc_type="natural"
        )

    def rate(self, maturity):
        """
        Get interpolated yield for given maturity (in years)
        """
        return float(self.curve(maturity))

    def discount_factor(self, maturity):
        """
        Continuous compounding discount factor
        """
        r = self.rate(maturity)
        return np.exp(-r * maturity)