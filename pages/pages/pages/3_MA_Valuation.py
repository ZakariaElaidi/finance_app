import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- SECURITY: Redirect if not logged in ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

st.title("💼 M&A & Private Equity Deal Room")

st.markdown("""
<style>
.ma-card { background-color: #161a22; border: 1px solid #333; padding: 15px; border-radius: 8px; margin-top: 15px; margin-bottom: 20px;}
.ma-card-title { color: #b3b3b3; font-size: 0.9rem; margin-bottom: 5px; }
.ma-card-value { color: white; font-size: 1.5rem; font-weight: bold; margin: 0; }
</style>
""", unsafe_allow_html=True)

with st.expander("ℹ️ Glossary & Advanced Definitions"):
    st.markdown("""
    * **CAPM (Capital Asset Pricing Model):** Formula used to calculate the Expected Return on Equity ($K_e$).
    * **Monte Carlo Simulation:** A computational algorithm that relies on repeated random sampling to understand the impact of risk and uncertainty in the valuation.
    * **MoIC (Multiple on Invested Capital):** Shows how much value an investment has generated (Exit Equity / Entry Equity).
    """)

# --- SIDEBAR INPUTS (PROXY DATA) ---
st.sidebar.header("🏢 Target Base Financials")
st.sidebar.info("Input the target company's base financials here to feed the models.")
base_rev = st.sidebar.number_input("Base Revenue (MAD)", value=5000000.0, step=100000.0)
base_ebitda = st.sidebar.number_input("Base EBITDA (MAD)", value=1200000.0, step=50000.0)

# --- ADVANCED WACC CALCULATOR (CAPM) ---
st.subheader("⚙️ Advanced WACC Calculator (CAPM)")
use_capm = st.toggle("Enable CAPM Calculation Mode")

if use_capm:
    st.markdown("<div style='padding: 15px; border: 1px solid #333; border-radius: 8px;'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    rf = c1.number_input("Risk-Free Rate (%)", value=4.0, help="E.g., Moroccan 10Y Treasury Bond") / 100
    rm = c2.number_input("Market Return (%)", value=10.0, help="Expected return of the CSE") / 100
    beta = c3.number_input("Beta (β)", value=1.2, help="Volatility relative to the market")
    tax = c4.number_input("Tax Rate (%)", value=30.0) / 100
    
    c5, c6 = st.columns(2)
    kd_raw = c5.number_input("Cost of Debt (%)", value=6.0) / 100
    debt_weight = c6.slider("Debt Weighting (%)", 0.0, 100.0, 40.0) / 100
    equity_weight = 1 - debt_weight
    
    # Math Engine
    ke = rf + beta * (rm - rf)
    kd = kd_raw * (1 - tax)
    wacc = (ke * equity_weight) + (kd * debt_weight)
    
    st.info(f"**Cost of Equity (Ke):** {ke*100:.2f}% &nbsp; | &nbsp; **Cost of Debt post-tax (Kd):** {kd*100:.2f}%")
    st.success(f"🎯 **Implied WACC:** {wacc*100:.2f}%")
    st.markdown("</div>", unsafe_allow_html=True)
else:
    wacc = st.slider("WACC %", 5.0, 20.0, 10.0, 0.5) / 100

st.markdown("---")

# --- VALUATION ENGINES ---
col_dcf, col_lbo = st.columns(2, gap="large")

with col_dcf:
    st.subheader("📊 Standard DCF Engine")
    tg = st.slider("Terminal Growth %", 0.0, 5.0, 2.0, 0.1) / 100
    proj_growth = st.slider("Projected Growth %", -10.0, 30.0, 5.0, 1.0) / 100
    margin = st.slider("FCF Margin %", 1.0, 30.0, 15.0, 1.0) / 100

    # DCF Math
    cfs = [base_rev * ((1 + proj_growth)**i) * margin for i in range(1, 6)]
    ev = sum([cf / ((1 + wacc)**(i+1)) for i, cf in enumerate(cfs)]) + (((cfs[-1] * (1 + tg)) / (wacc - tg)) / ((1 + wacc)**5) if wacc > tg else 0)
    
    st.markdown(f"""
    <div class="ma-card" style="border-left: 4px solid #1f77b4;">
        <div class="ma-card-title">Implied Enterprise Value (EV)</div>
        <div class="ma-card-value">{ev:,.2f} MAD</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 🎲 MONTE CARLO SIMULATION
    if st.button("🎲 Run Monte Carlo Simulation (10k Iterations)", use_container_width=True, type="primary"):
        with st.spinner("Running 10,000 simulations..."):
            np.random.seed(42)
            # Create normal distributions for risk modeling (2% standard deviation)
            sim_growths = np.random.normal(proj_growth, 0.02, 10000) 
            sim_margins = np.random.normal(margin, 0.02, 10000) 
            
            sim_evs = []
            for g, m in zip(sim_growths, sim_margins):
                s_cfs = [base_rev * ((1 + g)**i) * m for i in range(1, 6)]
                s_ev = sum([cf / ((1 + wacc)**(i+1)) for i, cf in enumerate(s_cfs)]) + (((s_cfs[-1] * (1 + tg)) / (wacc - tg)) / ((1 + wacc)**5) if wacc > tg else 0)
                sim_evs.append(s_ev)
            
            fig_mc = go.Figure(data=[go.Histogram(x=sim_evs, nbinsx=50, marker_color='#c1272d')])
            fig_mc.update_layout(title="Enterprise Value Probability Distribution", template="plotly_dark", xaxis_title="EV (MAD)", yaxis_title="Frequency", height=350)
            st.plotly_chart(fig_mc, use_container_width=True)
            
            perc_25, perc_75 = np.percentile(sim_evs, 25), np.percentile(sim_evs, 75)
            st.caption(f"**75% Confidence Interval:** {perc_25:,.0f} MAD to {perc_75:,.0f} MAD")

with col_lbo:
    st.subheader("💰 LBO Quick-Modeler")
    c_l1, c_l2 = st.columns(2)
    with c_l1: entry_mult = st.number_input("Entry Multiple (x)", 3.0, 15.0, 6.0, 0.5)
    with c_l2: exit_mult = st.number_input("Exit Multiple (x)", 3.0, 15.0, 6.0, 0.5)
    debt_pct = st.slider("Debt Funding %", 0.0, 90.0, 60.0, 5.0) / 100

    # LBO Math
    entry_ev = base_ebitda * entry_mult
    debt = entry_ev * debt_pct
    equity = entry_ev - debt
    exit_ev = (base_ebitda * ((1 + proj_growth)**5)) * exit_mult
    # Assuming half of FCF pays down debt
    exit_equity = exit_ev - max(0, debt - sum(cfs)*0.5)

    moic = exit_equity / equity if equity > 0 else 0
    irr = ((moic**(1/5) - 1) * 100) if moic > 0 else 0
    
    st.markdown(f"""
    <div class="ma-card" style="border-left: 4px solid #9467bd;">
        <div class="ma-card-title">Private Equity Metrics (5-Year Horizon)</div>
        <div class="ma-card-value" style="font-size: 1.2rem;">IRR: {irr:.2f}% &nbsp; | &nbsp; MoIC: {moic:.2f}x</div>
    </div>
    """, unsafe_allow_html=True)
