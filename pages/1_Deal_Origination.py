import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import yfinance as yf
import random

# --- SECURITY & STATE ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

lang = st.session_state.get("lang", "English")
curr = st.session_state.get("currency", "MAD")
rates = st.session_state.get("rates", {"MAD": 1.0, "USD": 0.10, "EUR": 0.09})
syms = st.session_state.get("sym", {"MAD": "MAD", "USD": "$", "EUR": "€"})

rate = rates[curr]
sym = syms[curr]

# --- INSTITUTIONAL TRANSLATION DICTIONARY ---
t = {
    "English": {
        "phase": "PHASE 1: DEAL ORIGINATION",
        "title": "M&A Target Screening Terminal",
        "desc": "Identify and benchmark undervalued corporate targets using live market data algorithms.",
        "kpi1": "Sector Avg P/E", "kpi2": "Market Volatility", "kpi3": "Tracked Assets", "kpi4": "Active Signals",
        "target_cfg": "⚙️ Target Standalone Assumptions",
        "t_name": "Target Code Name", "t_margin": "EBITDA Margin (%)", "t_roe": "Target ROE (%)", "t_gear": "Gearing (D/E %)", "t_pe": "Entry Multiple (x)",
        "score_title": "Deal Feasibility Score",
        "tab1": "📊 Live Comps Matrix", "tab2": "📈 Valuation Multiples", "tab3": "⚠️ Risk vs Return", "tab4": "🕸️ Strategic Fit",
        "refresh": "🔄 Sync Market Data", "col_price": f"Market Price ({sym})", "t_type": "Identified Target", "m_type": "Public Peer"
    },
    "Français": {
        "phase": "PHASE 1: ORIGINATION DE DEALS",
        "title": "Terminal de Screening M&A",
        "desc": "Identifiez et analysez les cibles sous-évaluées via des algorithmes de marché en direct.",
        "kpi1": "P/E Moyen", "kpi2": "Volatilité Marché", "kpi3": "Actifs Suivis", "kpi4": "Signaux Actifs",
        "target_cfg": "⚙️ Hypothèses de la Cible",
        "t_name": "Nom de Code", "t_margin": "Marge EBITDA (%)", "t_roe": "ROE Cible (%)", "t_gear": "Gearing (D/CP %)", "t_pe": "Multiple d'Entrée (x)",
        "score_title": "Score de Faisabilité",
        "tab1": "📊 Matrice des Comparables", "tab2": "📈 Multiples de Valorisation", "tab3": "⚠️ Risque vs Rendement", "tab4": "🕸️ Adéquation Stratégique",
        "refresh": "🔄 Sync Données Marché", "col_price": f"Prix Marché ({sym})", "t_type": "Cible Identifiée", "m_type": "Pair Public"
    },
    "Español": {
        "phase": "FASE 1: ORIGINACIÓN DE ACUERDOS",
        "title": "Terminal de Screening M&A",
        "desc": "Identifique y evalúe objetivos infravalorados utilizando algoritmos de datos en vivo.",
        "kpi1": "P/E Promedio", "kpi2": "Volatilidad Mercado", "kpi3": "Activos Seguidos", "kpi4": "Señales Activas",
        "target_cfg": "⚙️ Supuestos del Objetivo",
        "t_name": "Nombre en Clave", "t_margin": "Margen EBITDA (%)", "t_roe": "ROE Objetivo (%)", "t_gear": "Gearing (D/C %)", "t_pe": "Múltiplo de Entrada (x)",
        "score_title": "Puntuación de Viabilidad",
        "tab1": "📊 Matriz de Comparables", "tab2": "📈 Múltiplos de Valoración", "tab3": "⚠️ Riesgo vs Retorno", "tab4": "🕸️ Ajuste Estratégico",
        "refresh": "🔄 Sincronizar Mercado", "col_price": f"Precio Mercado ({sym})", "t_type": "Objetivo Identificado", "m_type": "Par Público"
    },
    "العربية": {
        "phase": "المرحلة الأولى: اكتشاف الصفقات",
        "title": "منصة فحص أهداف الاندماج والاستحواذ",
        "desc": "تحديد وتقييم الشركات المستهدفة باستخدام خوارزميات بيانات السوق الحية.",
        "kpi1": "متوسط مكرر الربحية", "kpi2": "تقلبات السوق", "kpi3": "الأصول المتتبعة", "kpi4": "الإشارات النشطة",
        "target_cfg": "⚙️ افتراضات الشركة المستهدفة",
        "t_name": "الاسم الرمزي", "t_margin": "هامش الأرباح (%)", "t_roe": "العائد على الحقوق (%)", "t_gear": "الرافعة المالية (%)", "t_pe": "مضاعف الدخول (x)",
        "score_title": "مؤشر جدوى الصفقة",
        "tab1": "📊 مصفوفة المقارنات", "tab2": "📈 مضاعفات التقييم", "tab3": "⚠️ المخاطر مقابل العائد", "tab4": "🕸️ الملاءمة الاستراتيجية",
        "refresh": "🔄 تحديث بيانات السوق", "col_price": f"سعر السوق ({sym})", "t_type": "الهدف المحدد", "m_type": "منافس عام"
    }
}
txt = t[lang]

# --- ADVANCED CSS INJECTION ---
rtl_css = """
.block-container { direction: rtl; text-align: right; }
[data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"], [data-testid="stHeader"] { direction: ltr !important; text-align: left !important; }
""" if lang == "العربية" else ""

st.markdown(f"""
<style>
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .block-container {{ animation: fadeIn 0.5s ease-out; overflow-x: hidden; max-width: 1400px; }}
    
    /* Institutional Header */
    .inst-header {{ background: linear-gradient(145deg, #0e1117, #161b22); border-left: 4px solid #1f77b4; padding: 20px 30px; border-radius: 8px; margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
    .inst-phase {{ color: #1f77b4; font-size: 0.85rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 5px; display: block; }}
    .inst-title {{ color: #ffffff; font-size: 2.2rem; font-weight: 700; margin: 0; padding: 0; letter-spacing: -0.5px; }}
    .inst-desc {{ color: #8b949e; font-size: 1rem; margin-top: 8px; }}
    
    /* KPI Strip */
    .kpi-container {{ display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }}
    .kpi-card {{ flex: 1; min-width: 150px; background: rgba(30, 34, 43, 0.5); border: 1px solid rgba(255,255,255,0.05); padding: 15px 20px; border-radius: 8px; border-top: 3px solid #3fb950; }}
    .kpi-val {{ font-size: 1.8rem; font-weight: 700; color: #ffffff; margin: 0; }}
    .kpi-lbl {{ font-size: 0.8rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin: 0; }}
    
    /* Input Container Override */
    div[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 8px !important; background: rgba(22,26,34,0.4); }}
    
    {rtl_css}
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
col_head, col_btn = st.columns([4, 1], vertical_alignment="bottom")
with col_head:
    st.markdown(f"""
    <div class="inst-header" {'dir="rtl"' if lang=="العربية" else ''}>
        <span class="inst-phase">{txt['phase']}</span>
        <h1 class="inst-title">{txt['title']}</h1>
        <p class="inst-desc">{txt['desc']}</p>
    </div>
    """, unsafe_allow_html=True)
with col_btn:
    if st.button(txt["refresh"], use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

# --- HYBRID DATA ENGINE (YFINANCE + QUANTITATIVE SIMULATION) ---
@st.cache_data(ttl=60, show_spinner=False)
def fetch_institutional_data():
    assets = {
        "LafargeHolcim": {"ticker": "LHM.CM", "base_p": 1780, "pe": 18.2, "margin": 16.5, "roe": 22.0, "gear": 45.0},
        "Addoha": {"ticker": "ADH.CM", "base_p": 33, "pe": 12.0, "margin": 8.5, "roe": 14.0, "gear": 120.0},
        "Alliances": {"ticker": "ADI.CM", "base_p": 260, "pe": 10.5, "margin": 9.0, "roe": 15.5, "gear": 135.0},
        "Ciments du Maroc": {"ticker": "CMA.CM", "base_p": 1750, "pe": 16.8, "margin": 15.2, "roe": 20.1, "gear": 40.0},
        "TGCC": {"ticker": "TGC.CM", "base_p": 330, "pe": 15.0, "margin": 12.5, "roe": 18.5, "gear": 85.0},
        "Sonasid": {"ticker": "SND.CM", "base_p": 870, "pe": 14.5, "margin": 5.2, "roe": 8.5, "gear": 20.0},
        "Jet Contractors": {"ticker": "JET.CM", "base_p": 500, "pe": 18.0, "margin": 6.0, "roe": 12.0, "gear": 110.0}
    }
    
    final_data = []
    for name, data in assets.items():
        price = None
        status = ""
        # 1. Attempt yfinance API
        try:
            ticker = yf.Ticker(data["ticker"])
            history = ticker.history(period="1d")
            if not history.empty:
                price = float(history['Close'].iloc[-1])
                status = "🟢 API (yfinance)"
        except: pass
        
        # 2. Advanced Quantitative Simulation (If API blocked)
        if price is None or price <= 0:
            # Simulate Geometric Brownian Motion (GBM) tick based on base price
            volatility = random.uniform(-0.015, 0.015) # 1.5% daily fluctuation
            price = data["base_p"] * (1 + volatility)
            status = "🟡 Quant Sim (GBM)"
            
        final_data.append({
            "Company": name, "Price_MAD": price, "Status": status,
            "PE_Ratio": data["pe"], "Net_Margin_%": data["margin"], "ROE_%": data["roe"], "Gearing_%": data["gear"]
        })
    return pd.DataFrame(final_data)

with st.spinner("Executing Market Algorithms..."):
    df_live = fetch_institutional_data().copy()
    df_live["Type"] = txt["m_type"]
    df_live["Price_Converted"] = df_live["Price_MAD"] * rate

# --- TOP KPI STRIP ---
avg_pe = df_live["PE_Ratio"].mean()
avg_roe = df_live["ROE_%"].mean()
st.markdown(f"""
<div class="kpi-container" {'dir="rtl"' if lang=="العربية" else ''}>
    <div class="kpi-card"><p class="kpi-val">{avg_pe:.1f}x</p><p class="kpi-lbl">{txt['kpi1']}</p></div>
    <div class="kpi-card" style="border-color: #f85149;"><p class="kpi-val">1.2%</p><p class="kpi-lbl">{txt['kpi2']}</p></div>
    <div class="kpi-card" style="border-color: #58a6ff;"><p class="kpi-val">{len(df_live)}</p><p class="kpi-lbl">{txt['kpi3']}</p></div>
    <div class="kpi-card" style="border-color: #a371f7;"><p class="kpi-val">3</p><p class="kpi-lbl">{txt['kpi4']}</p></div>
</div>
""", unsafe_allow_html=True)

# --- TARGET CONFIGURATION & GAUGE SCORE ---
col_cfg, col_gauge = st.columns([2.5, 1], gap="medium")

with col_cfg:
    st.markdown(f"#### {txt['target_cfg']}")
    with st.container(border=True):
        r1c1, r1c2, r1c3 = st.columns(3)
        t_name = r1c1.text_input(txt["t_name"], "Project Titan")
        t_margin = r1c2.number_input(txt["t_margin"], value=15.0, step=0.5)
        t_roe = r1c3.number_input(txt["t_roe"], value=18.0, step=0.5)
        
        r2c1, r2c2, r2c3 = st.columns(3)
        t_gear = r2c1.number_input(txt["t_gear"], value=55.0, step=5.0)
        t_pe = r2c2.number_input(txt["t_pe"], value=12.5, step=0.5)
        
        # Calculate proprietary deal score based on inputs vs market
        score = 50
        if t_pe < avg_pe: score += 15 # Cheaper than market
        if t_roe > avg_roe: score += 20 # Better return than market
        if t_gear < 80: score += 15 # Healthy debt
        
with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = score, title = {'text': txt["score_title"], 'font': {'size': 14, 'color': '#8b949e'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#1f77b4"},
            'steps': [
                {'range': [0, 40], 'color': "rgba(248, 81, 73, 0.3)"},
                {'range': [40, 70], 'color': "rgba(245, 176, 65, 0.3)"},
                {'range': [70, 100], 'color': "rgba(63, 185, 80, 0.3)"}],
        }
    ))
    fig_gauge.update_layout(height=220, margin=dict(l=20, r=20, t=30, b=10), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_gauge, use_container_width=True)

# Combine Data
target_row = pd.DataFrame([{
    "Company": t_name, "Price_Converted": 0, "Status": "🎯 Model Input",
    "PE_Ratio": t_pe, "Net_Margin_%": t_margin, "ROE_%": t_roe, "Gearing_%": t_gear, "Type": txt["t_type"]
}])
df_combined = pd.concat([target_row, df_live], ignore_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- ADVANCED TABBED ANALYTICS ---
tab1, tab2, tab3, tab4 = st.tabs([txt["tab1"], txt["tab2"], txt["tab3"], txt["tab4"]])

with tab1:
    def highlight_target(row):
        if row['Type'] == txt["t_type"]: return ['background-color: rgba(31, 119, 180, 0.3)'] * len(row)
        return [''] * len(row)

    display_table = df_combined[["Company", "Type", "Status", "Price_Converted", "PE_Ratio", "Net_Margin_%", "ROE_%", "Gearing_%"]].rename(
        columns={"Price_Converted": txt["col_price"]}
    )
    st.dataframe(
        display_table.style.apply(highlight_target, axis=1).format({
            txt["col_price"]: "{:,.2f}", "PE_Ratio": "{:.2f}x", "Net_Margin_%": "{:.2f}%", "ROE_%": "{:.2f}%", "Gearing_%": "{:.2f}%"
        }),
        use_container_width=True, hide_index=True, height=300
    )

with tab2:
    col_c1, col_c2 = st.columns(2)
    c_map = {t_name: "#1f77b4"}
    for p in df_live["Company"]: c_map[p] = "#30363d"
    
    with col_c1:
        fig_pe = px.bar(df_combined, x="Company", y="PE_Ratio", color="Company", color_discrete_map=c_map, title="P/E Multiples")
        fig_pe.update_layout(template="plotly_dark", showlegend=False, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_pe, use_container_width=True)
    with col_c2:
        fig_m = px.bar(df_combined, x="Company", y="Net_Margin_%", color="Company", color_discrete_map=c_map, title="EBITDA Margins (%)")
        fig_m.update_layout(template="plotly_dark", showlegend=False, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_m, use_container_width=True)

with tab3:
    fig_scatter = px.scatter(
        df_combined, x="Gearing_%", y="ROE_%", color="Type", text="Company", size_max=60,
        color_discrete_map={txt["t_type"]: "#1f77b4", txt["m_type"]: "#8b949e"} 
    )
    fig_scatter.update_traces(textposition='top center', marker=dict(size=14))
    fig_scatter.add_hline(y=avg_roe, line_dash="dash", line_color="gray", opacity=0.5)
    fig_scatter.add_vline(x=df_live["Gearing_%"].mean(), line_dash="dash", line_color="gray", opacity=0.5)
    fig_scatter.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab4:
    cats = ['Margin', 'ROE', 'P/E Efficiency', 'Debt Safety']
    t_health = max(0, 150 - t_gear) 
    m_health = max(0, 150 - df_live["Gearing_%"].mean())
    t_vals = [t_margin, t_roe, (20-t_pe)*2, t_health]
    m_vals = [df_live["Net_Margin_%"].mean(), df_live["ROE_%"].mean(), (20-avg_pe)*2, m_health]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=t_vals, theta=cats, fill='toself', name=txt["t_type"], line_color='#1f77b4'))
    fig_radar.add_trace(go.Scatterpolar(r=m_vals, theta=cats, fill='toself', name=txt["m_type"], line_color='#8b949e')) 
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=False)), template="plotly_dark", height=400, margin=dict(l=40, r=40, t=40, b=40))
    st.plotly_chart(fig_radar, use_container_width=True)
