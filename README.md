# 📈 Fixed Income Analytics & LDI Hedge Optimizer

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

A modular fixed income analytics framework built in Python featuring:

- Bond pricing engine
- Yield curve construction
- Portfolio valuation
- Key Rate Duration (KRD) analysis
- Scenario-based rate shocks
- Liability-Driven Investment (LDI) hedge optimization
- Interactive Streamlit dashboards

---

## 🚀 Overview

This project implements a quantitative fixed income toolkit designed for:

- Interest rate risk analysis  
- Duration & convexity modeling  
- Liability hedging  
- Scenario stress testing  
- Institutional LDI portfolio construction  

The system is modular, extensible, and structured like a production-ready quant codebase.

---


---

## 🧠 Methodology

### 🔹 Bond Pricing

For each bond:

\[
P = \sum_{t=1}^{T} CF_t \cdot DF(t)
\]

Where:

\[
DF(t) = e^{-r(t) \cdot t}
\]

- \( r(t) \) interpolated from the yield curve
- Supports configurable coupon frequency

---

### 🔹 Key Rate Duration (KRD)

Localized Gaussian shocks isolate maturity-specific rate sensitivity:

\[
KRD = -\frac{\Delta P}{P \cdot \Delta y}
\]

Used for:
- Sensitivity decomposition
- Hedge construction
- Stress testing

---

### 🔹 LDI Hedge Optimization

We solve:

\[
\min_w \sum_i w_i P_i
\]

Subject to:

\[
\text{Portfolio PV}_{scenario} \ge \text{Liability PV}_{scenario}
\]

Across:
- Base curve
- +Shock at each key rate
- -Shock at each key rate

Optimization:
- Non-negative weights
- SLSQP solver (scipy)

---

## 🖥 Applications

### 1️⃣ Bond Valuation Dashboard

Run:

```bash
streamlit run app/bond_portfolio.py
```

### 2️⃣ LDI Hedge Optimizer

Run:

```bash
streamlit run app/hedge_bond.py

