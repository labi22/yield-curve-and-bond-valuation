import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from yield_curve.data_loader import load_treasury_yields
from bond_engine.bond_pricer import Bond, price_bond
from bond_engine.portfolio import BondPortfolio
from yield_curve.curve_builder import YieldCurve
from scipy.optimize import minimize

class LocalShockCurve:
    def __init__(self, base_curve, center, shock_bp):
        self.base = base_curve
        self.center = center
        self.shock = shock_bp / 10000

    def rate(self, maturity):
        bump = np.exp(-((maturity - self.center) ** 2) / 1.0)
        return self.base.rate(maturity) + self.shock * bump

    def discount_factor(self, maturity):
        r = self.rate(maturity)
        return np.exp(-r * maturity)

def pv_liabilities(curve, times, cfs):
    return sum(cf * curve.discount_factor(t) for t, cf in zip(times, cfs))


def key_rate_duration_liability(times, cfs, yc, key_rate, shock_bp=1):
    base_pv = pv_liabilities(yc, times, cfs)

    shocked_curve = LocalShockCurve(yc, key_rate, shock_bp)
    shocked_pv = pv_liabilities(shocked_curve, times, cfs)

    return -(shocked_pv - base_pv) / base_pv / (shock_bp / 10000)

def optimize_hedge(yc, hedge_bonds, times, cfs, shock_bp):
    scenarios = [yc]

    for t in times:
        scenarios.append(LocalShockCurve(yc, t, +shock_bp))
        scenarios.append(LocalShockCurve(yc, t, -shock_bp))

    P = np.zeros((len(scenarios), len(hedge_bonds)))
    L = np.zeros(len(scenarios))

    for i, sc in enumerate(scenarios):
        for j, bond in enumerate(hedge_bonds):
            P[i, j] = price_bond(bond, sc)
        L[i] = pv_liabilities(sc, times, cfs)

    prices = np.array([price_bond(bond, yc) for bond in hedge_bonds])

    def objective(w):
        return np.dot(w, prices)

    constraints = [{
        "type": "ineq",
        "fun": lambda w, i=i: np.dot(P[i], w) - L[i]
    } for i in range(len(scenarios))]

    bounds = [(0, None)] * len(hedge_bonds)

    res = minimize(
        objective,
        x0=np.ones(len(hedge_bonds)),
        bounds=bounds,
        constraints=constraints,
        method="SLSQP"
    )

    return res.x

st.set_page_config(page_title="LDI Hedge Optimizer", layout="wide")
st.title("Liability-Driven Hedge Optimizer (Key-Rate Shocks)")

st.sidebar.header("Liability Cashflows")

n_cf = st.sidebar.slider("Number of Cashflows", 1, 10, 3)

liab_df = pd.DataFrame({
    "Time (Years)": [2, 5, 10][:n_cf],
    "Cashflow": [100, 150, 200][:n_cf]
})

liab_df = st.sidebar.data_editor(liab_df, num_rows="dynamic")

liability_times = liab_df["Time (Years)"].values
liability_cfs = liab_df["Cashflow"].values

st.sidebar.header("Shock Settings")

shock_bp = st.sidebar.slider("Shock Size (bp)", -200, 200, 100, step=25)
key_rate = st.sidebar.selectbox("Key Rate (Years)", [1, 2, 5, 10])

# Replace this with however you already load latest yields
#latest = st.session_state["latest_yields"]
df = load_treasury_yields(start="2024-01-01")
latest = df.iloc[-1]
yc = YieldCurve(latest)

bond_2y = Bond(100, latest["2Y"], 2, frequency=2)
bond_5y = Bond(100, latest["5Y"], 5, frequency=2)
bond_10y = Bond(100, latest["10Y"], 10, frequency=2)

bond_map = {
    "2Y Treasury": bond_2y,
    "5Y Treasury": bond_5y,
    "10Y Treasury": bond_10y
}

selected_labels = st.sidebar.multiselect(
    "Hedge Instruments",
    list(bond_map.keys()),
    default=list(bond_map.keys())
)

hedge_bonds = [bond_map[l] for l in selected_labels]

weights = optimize_hedge(
    yc,
    hedge_bonds,
    liability_times,
    liability_cfs,
    abs(shock_bp)
)

st.subheader("Optimal Hedge Weights")

st.dataframe(pd.DataFrame({
    "Bond": selected_labels,
    "Weight": weights
}))

shock_grid = np.arange(-200, 201, 20)

pv_portfolio = []
pv_liability = []

for s in shock_grid:
    sc = LocalShockCurve(yc, key_rate, s)
    pv_portfolio.append(
        sum(w * price_bond(b, sc) for w, b in zip(weights, hedge_bonds))
    )
    pv_liability.append(
        pv_liabilities(sc, liability_times, liability_cfs)
    )

fig, ax = plt.subplots()
ax.plot(shock_grid, pv_portfolio, label="Hedged Portfolio", linewidth=2)
ax.plot(shock_grid, pv_liability, label="Liability", linestyle="--")
ax.axvline(0, color="black", alpha=0.3)
ax.set_xlabel("Key Rate Shock (bp)")
ax.set_ylabel("PV")
ax.set_title(f"PV vs Shock @ {key_rate}Y")
ax.legend()
ax.grid(True)

st.pyplot(fig)

P0 = pv_liabilities(yc, liability_times, liability_cfs)
krd = key_rate_duration_liability(
    liability_times,
    liability_cfs,
    yc,
    key_rate
)

approx_krd = -P0 * krd * (shock_bp / 10000)

actual = pv_liabilities(
    LocalShockCurve(yc, key_rate, shock_bp),
    liability_times,
    liability_cfs
) - P0

st.subheader("Shock Attribution")

st.table(pd.DataFrame({
    "Metric": ["Actual ΔPV", "KRD Approx"],
    "Value": [actual, approx_krd]
}))
