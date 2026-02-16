import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import streamlit as st
import numpy as np
import pandas as pd

from yield_curve.data_loader import load_treasury_yields
from bond_engine.bond_pricer import Bond
from bond_engine.portfolio import BondPortfolio
from bond_engine.rate_shock import ShockedYieldCurve
from yield_curve.curve_builder import YieldCurve

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Bond Analytics Lab",
    layout="wide"
)

st.title("📊 Bond Analytics Lab")

# -----------------------------
# Sidebar – Yield Curve
# -----------------------------
#st.sidebar.header("Yield Curve")

#base_rate = st.sidebar.slider(
#    "Flat Yield (%)",
#    min_value=0.0,
#    max_value=10.0,
#    value=5.0,
#    step=0.1
#) / 100

#yields = pd.Series(
#    {
#        "1M": base_rate,
#        "3M": base_rate,
#        "6M": base_rate,
#        "1Y": base_rate,
#        "2Y": base_rate,
#        "5Y": base_rate,
#        "10Y": base_rate,
#        "30Y": base_rate,
#    }
#)

#yc = YieldCurve(yields)
df = load_treasury_yields(start="2024-01-01")
latest = df.iloc[-1]
yc = YieldCurve(latest)

# -----------------------------
# Sidebar – Shock
# -----------------------------
st.sidebar.header("Rate Shock")

shock_bp = st.sidebar.slider(
    "Parallel Shock (bp)",
    min_value=-200,
    max_value=200,
    value=0,
    step=25
)

shocked_curve = ShockedYieldCurve(yc, shock_bp)

# -----------------------------
# Bond Inputs
# -----------------------------
st.header("Bond Definitions")

cols = st.columns(3)

bonds = []
weights = []

for i, col in enumerate(cols):
    with col:
        st.subheader(f"Bond {i+1}")

        maturity = st.number_input(
            "Maturity (years)",
            min_value=1,
            max_value=30,
            value=5 + i * 5,
            step=1,
            key=f"mat_{i}"
        )

        coupon = st.number_input(
            "Coupon (%)",
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.25,
            key=f"cpn_{i}"
        ) / 100

        weight = st.number_input(
            "Weight",
            min_value=-5.0,
            max_value=5.0,
            value=1/3,
            step=0.1,
            key=f"w_{i}"
        )

        bond = Bond(
            face_value=100,
            coupon_rate=coupon,
            maturity=maturity,
            frequency=2
        )

        bonds.append(bond)
        weights.append(weight)

# -----------------------------
# Normalize weights
# -----------------------------
weights = np.array(weights)
weights = weights / np.sum(np.abs(weights))

portfolio = BondPortfolio(bonds, weights)

# -----------------------------
# Analytics
# -----------------------------
st.header("📈 Portfolio Analytics")

price = portfolio.price(yc)
duration = portfolio.duration(yc)
convexity = portfolio.convexity(yc)

shocked_price = portfolio.price(shocked_curve)
pnl_pct = (shocked_price / price - 1) * 100

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Price", f"{price:.2f}")
col2.metric("Duration", f"{duration:.2f}")
col3.metric("Convexity", f"{convexity:.2f}")
col4.metric("Shock Price", f"{shocked_price:.2f}")
col5.metric("Shock P&L", f"{pnl_pct:.2f} %")

# -----------------------------
# Shock Curve Plot
# -----------------------------
st.header("Price vs Yield Shock")

shocks = np.arange(-200, 201, 10)
prices = []

for s in shocks:
    sc = ShockedYieldCurve(yc, s)
    prices.append(portfolio.price(sc))

df = pd.DataFrame({
    "Shock (bp)": shocks,
    "Price": prices
})

st.line_chart(df.set_index("Shock (bp)"))