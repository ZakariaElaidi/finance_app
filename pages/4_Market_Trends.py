import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
        "header_tag": "SECONDARY TOOL",
        "banner_h": "Market Trends & Live Charts", "banner_desc": "Track real-time market movements, volatility, and historical price trends.",
        "comp": "Company:", "time": "Timeframe:", "style": "Chart Style:",
        "m1": "1 Month", "m3": "3 Months", "m6": "6 Months",
        "candle": "Candlesticks", "line": "Line Chart",
        "err": "Error loading market data:", "chart_title": "Historical Price Trajectory",
        "curr_price": "Last Close", "period_high": "Period High", "period_low": "Period Low", "show_ma": "Overlay Moving Average (MA)"
    },
    "Français": {
        "header_tag": "OUTIL SECONDAIRE",
        "banner_h": "Tendances & Graphiques", "banner_desc": "Suivez les mouvements du marché, la volatilité et les tendances historiques.",
        "comp": "Entreprise :", "time": "Période :", "style": "Style :",
        "m1": "1 Mois", "m3": "3 Mois", "m6": "6 Mois",
        "candle": "Bougies", "line": "Courbe",
        "err": "Erreur de chargement des données :", "chart_title": "Trajectoire Historique des Prix",
        "curr_price": "Dernière Clôture", "period_high": "Plus Haut", "period_low": "Plus Bas", "show_ma": "Afficher Moyenne Mobile (MA)"
    },
    "Español": {
        "header_tag": "HERRAMIENTA SECUNDARIA",
        "banner_h": "Tendencias y Gráficos", "banner_desc": "Rastree los movimientos del mercado, la volatilidad y las tendencias históricas.",
        "comp": "Empresa:", "time": "Período:", "style": "Estilo:",
        "m1": "1 Mes", "m3": "3 Meses", "m6": "6 Meses",
        "candle": "Velas", "line": "Gráfico de Líneas",
        "err": "Error al cargar datos:", "chart_title": "Trayectoria Histórica de Precios",
        "curr_price": "Último Cierre", "period_high": "Máximo", "period_low": "Mínimo", "show_ma": "Mostrar Media Móvil (MA)"
    },
    "العربية": {
        "header_tag": "أداة مساعدة",
        "banner_h": "رسوم بيانية حية واتجاهات السوق", "banner_desc": "تتبع تحركات السوق في الوقت الفعلي، التقلبات، والاتجاهات التاريخية للأسعار.",
        "comp": "الشركة:", "time": "الإطار الزمني:", "style": "النمط:",
        "m1": "شهر واحد", "m3": "3 أشهر", "m6": "6 أشهر",
        "candle": "شموع يابانية", "line": "رسم خطي",
        "err": "خطأ في تحميل بيانات السوق:", "chart_title": "المسار التاريخي للأسعار",
        "curr_price": "آخر إغلاق", "period_high": "الأعلى", "period_low": "الأدنى", "show_ma": "إظهار المتوسط المتحرك (MA)"
    }
}
txt = t[lang]

# --- FULL WIDTH CSS INJECTION (Red Theme) ---
rtl_css = """
.block-container { direction: rtl; text-align: right; }
[data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"], [data-testid="stHeader"] { direction: ltr !important; text-align: left !important; }
""" if lang == "العربية" else ""

st.markdown(f"""
<style>
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    
    .block-container {{ 
        animation: fadeIn 0.5s ease-out; 
        overflow-x: hidden; 
        max-width: 100% !important; 
        padding-top: 2rem !important; 
        padding-bottom: 5rem !important; 
        padding-left: 3rem !important; 
        padding-right: 3rem !important; 
    }}
    
    .inst-header {{ background: linear-gradient(145deg, #0e1117, #161b22); border-left: 4px solid #d62728; padding: 30px 40px; border-radius: 8px; margin-bottom: 40px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
    .inst-phase {{ color: #d62728; font-size: 0.9rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; display: block; }}
    .inst-title {{ color: #ffffff; font-size: 2.5rem; font-weight: 700; margin: 0; padding: 0; letter-spacing: -0.5px; }}
    .inst-desc {{ color: #8b949e; font-size: 1.1rem; margin-top: 10px; }}
    
    .kpi-container {{ display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }}
    .kpi-card {{ flex: 1; min-width: 200px; background: rgba(30, 34, 43, 0.5); border: 1px solid rgba(255,255,255,0.05); padding: 20px 25px; border-radius: 8px; border-top: 4px solid #d62728; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}
    .kpi-val {{ font-size: 2.2rem; font-weight: 700; color: #ffffff; margin: 0; }}
    .kpi-lbl {{ font-size: 0.9rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin: 0; margin-top: 5px; }}
    
    div[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 8px !important; background: rgba(22,26,34,0.4); padding: 1.5rem !important; margin-bottom: 2rem !important; }}
    
    [data-testid="stSidebarNav"] li:first-child a span {{ display: none !important; }}
    [data-testid="stSidebarNav"] li:first-child a::after {{ content: "🏠 Home"; font-size: 15px; margin-left: 0px; }}
    
    {rtl_css}
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown(f"""
<div class="inst-header" {'dir="rtl"' if lang=="العربية" else ''}>
    <span class="inst-phase">{txt['header_tag']}</span>
    <h1 class="inst-title">{txt['banner_h']}</h1>
    <p class="inst-desc">{txt['banner_desc']}</p>
</div>
""", unsafe_allow_html=True)

# --- DATA FETCHING (Simulated baseline to match other tools) ---
@st.cache_data(ttl=60)
def get_live_market_data():
    try:
        # We simulate the CSV data read here to keep the architecture intact without needing the physical file
        assets = [
            {"Company": "LafargeHolcim", "Price_MAD": 1820.00},
            {"Company": "Addoha", "Price_MAD": 34.50},
            {"Company": "Alliances", "Price_MAD": 275.00},
            {"Company": "Ciments du Maroc", "Price_MAD": 1785.00},
            {"Company": "TGCC", "Price_MAD": 345.00},
            {"Company": "Sonasid", "Price_MAD": 890.00}
        ]
        return pd.DataFrame(assets)
    except Exception as e:
        st.error(f"{txt['err']} {str(e)}")
        return None

df_live = get_live_market_data()

# --- UI & CHART LOGIC ---
if df_live is not None:
    with st.container(border=True):
        c_sel1, c_sel2, c_sel3, c_sel4 = st.columns([2, 2, 2, 1.5], gap="large")
        with c_sel1: selected_company = st.selectbox(txt["comp"], df_live["Company"].tolist())
        with c_sel2: time_period = st.selectbox(txt["time"], [txt["m1"], txt["m3"], txt["m6"]])
        with c_sel3: chart_type = st.radio(txt["style"], [txt["candle"], txt["line"]], horizontal=True)
        with c_sel4: 
            st.markdown("<br>", unsafe_allow_html=True)
            show_ma = st.toggle(txt["show_ma"], value=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Map the translated time period back to number of days
    days_map = {txt["m1"]: 30, txt["m3"]: 90, txt["m6"]: 180}
    num_days = days_map[time_period]
    
    # Get base price and apply currency rate
    base_price_mad = df_live[df_live["Company"] == selected_company]["Price_MAD"].values[0]
    base_price = base_price_mad * rate 
    
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=num_days)
    
    # Simulate market volatility based on the converted base price
    np.random.seed(42 + len(selected_company) + num_days)
    vol = base_price * 0.05
    changes = np.random.normal(0, vol, size=num_days)
    closes = base_price - np.cumsum(changes[::-1])[::-1] 
    opens = closes - np.random.normal(0, vol, size=num_days)
    highs = np.maximum(opens, closes) + np.abs(np.random.normal(0, vol*1.2, size=num_days))
    lows = np.minimum(opens, closes) - np.abs(np.random.normal(0, vol*1.2, size=num_days))
    
    # Calculate Quick Stats
    max_price = max(highs)
    min_price = min(lows)
    
    # Display Quick Stats
    st.markdown(f"""
    <div class="kpi-container" {'dir="rtl"' if lang=="العربية" else ''}>
        <div class="kpi-card"><p class="kpi-val">{closes[-1]:,.2f} <span style="font-size: 1.2rem;">{sym}</span></p><p class="kpi-lbl">{txt['curr_price']}</p></div>
        <div class="kpi-card" style="border-top-color: #2ea043;"><p class="kpi-val" style="color: #2ea043;">{max_price:,.2f} <span style="font-size: 1.2rem;">{sym}</span></p><p class="kpi-lbl">{txt['period_high']}</p></div>
        <div class="kpi-card" style="border-top-color: #f85149;"><p class="kpi-val" style="color: #f85149;">{min_price:,.2f} <span style="font-size: 1.2rem;">{sym}</span></p><p class="kpi-lbl">{txt['period_low']}</p></div>
    </div>
    """, unsafe_allow_html=True)

    # Build Plotly Chart
    fig_m = go.Figure()
    
    if chart_type == txt["candle"]:
        fig_m.add_trace(go.Candlestick(x=dates, open=opens, high=highs, low=lows, close=closes, name="Price", increasing_line_color='#2ea043', decreasing_line_color='#f85149'))
    else:
        fig_m.add_trace(go.Scatter(x=dates, y=closes, mode='lines', name="Price", line=dict(color='#d62728', width=2), fill='tozeroy', fillcolor='rgba(214, 39, 40, 0.1)'))
        
    # Add Moving Average (MA)
    if show_ma:
        ma_period = 7 if num_days >= 7 else num_days
        ma_values = pd.Series(closes).rolling(window=ma_period).mean().values
        fig_m.add_trace(go.Scatter(x=dates, y=ma_values, mode='lines', name=f"MA ({ma_period}d)", line=dict(color='#58a6ff', width=2, dash='dot')))

    fig_m.update_layout(
        height=600, 
        title=f"{txt['chart_title']} - {selected_company} ({time_period})", 
        template="plotly_dark", 
        xaxis_rangeslider_visible=False,
        yaxis_title=f"Market Price ({sym})",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    st.plotly_chart(fig_m, use_container_width=True)
