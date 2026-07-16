import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- SECURITY ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

# --- GLOBAL STATE INITIALIZATION ---
lang = st.session_state.get("lang", "English")
curr = st.session_state.get("currency", "MAD")
rates = st.session_state.get("rates", {"MAD": 1.0, "USD": 0.10, "EUR": 0.09})
syms = st.session_state.get("sym", {"MAD": "MAD", "USD": "$", "EUR": "€"})

rate = rates[curr]
sym = syms[curr]

# --- TRANSLATION DICTIONARY ---
t = {
    "English": {
        "banner_h": "💹 Live Charts & Market Trends", "banner_desc": "Track real-time market movements, volatility, and historical price trends.",
        "comp": "Company:", "time": "Timeframe:", "style": "Style:",
        "m1": "1 Month", "m3": "3 Months", "m6": "6 Months",
        "candle": "Candlesticks", "line": "Line Chart",
        "err": "Error loading CSV:", "chart_title": "Price Trend",
        "curr_price": "Current Price", "period_high": "Period High", "period_low": "Period Low", "show_ma": "Show Trend Line (Moving Average)"
    },
    "Français": {
        "banner_h": "💹 Graphiques en Direct et Tendances", "banner_desc": "Suivez les mouvements du marché, la volatilité et les tendances historiques.",
        "comp": "Entreprise :", "time": "Période :", "style": "Style :",
        "m1": "1 Mois", "m3": "3 Mois", "m6": "6 Mois",
        "candle": "Bougies (Candlesticks)", "line": "Courbe (Line)",
        "err": "Erreur de chargement CSV :", "chart_title": "Tendance des Prix",
        "curr_price": "Prix Actuel", "period_high": "Plus Haut", "period_low": "Plus Bas", "show_ma": "Afficher la Tendance (Moyenne Mobile)"
    },
    "Español": {
        "banner_h": "💹 Gráficos en Vivo y Tendencias", "banner_desc": "Rastrea los movimientos del mercado, la volatilidad y las tendencias históricas.",
        "comp": "Empresa:", "time": "Período:", "style": "Estilo:",
        "m1": "1 Mes", "m3": "3 Meses", "m6": "6 Meses",
        "candle": "Velas (Candlesticks)", "line": "Gráfico de Líneas",
        "err": "Error al cargar CSV:", "chart_title": "Tendencia de Precios",
        "curr_price": "Precio Actual", "period_high": "Máximo del Período", "period_low": "Mínimo del Período", "show_ma": "Mostrar Tendencia (Media Móvil)"
    },
    "العربية": {
        "banner_h": "💹 رسوم بيانية حية واتجاهات السوق", "banner_desc": "تتبع تحركات السوق في الوقت الفعلي، التقلبات، والاتجاهات التاريخية للأسعار.",
        "comp": "الشركة:", "time": "الإطار الزمني:", "style": "النمط:",
        "m1": "شهر واحد", "m3": "3 أشهر", "m6": "6 أشهر",
        "candle": "شموع يابانية", "line": "رسم خطي",
        "err": "خطأ في تحميل ملف CSV:", "chart_title": "اتجاه السعر",
        "curr_price": "السعر الحالي", "period_high": "الأعلى خلال الفترة", "period_low": "الأدنى خلال الفترة", "show_ma": "إظهار خط الاتجاه (المتوسط المتحرك)"
    }
}
txt = t[lang]

# --- UI STYLING & CSS HACKS ---
rtl_css = ""
if lang == "العربية":
    rtl_css = """
    .block-container { direction: rtl; text-align: right; }
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"], [data-testid="stHeader"] { direction: ltr !important; text-align: left !important; }
    """

st.markdown(f"""
<style>
    /* Global Fade-in Animation */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(15px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .block-container {{ animation: fadeIn 0.6s ease-out; }}

    [data-testid="stSidebarNav"] li:first-child a span {{ display: none !important; }}
    [data-testid="stSidebarNav"] li:first-child a::after {{ content: "🏠 Home"; font-size: 15px; margin-left: 0px; }}
    
    /* Live Charts Banner Styling (Gold/Bronze Theme) */
    .full-width-banner {{ position: relative; width: 100%; height: 250px; background-image: url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop'); background-size: cover; background-position: center; margin-bottom: 25px; border-radius: 10px; border-left: 5px solid #f5b041; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
    .banner-overlay {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, rgba(14,17,23,0.95) 0%, rgba(14,17,23,0.6) 50%, rgba(245,176,65,0.2) 100%); }}
    .banner-content {{ position: absolute; top: 50%; left: 30px; transform: translateY(-50%); z-index: 2; }}
    
    /* Quick Stats Styling */
    .stat-card {{ background-color: rgba(255,255,255,0.05); border-radius: 8px; padding: 15px; text-align: center; border-top: 3px solid #f5b041; margin-bottom: 20px; }}
    .stat-title {{ color: #b3b3b3; font-size: 14px; margin: 0 0 5px 0; text-transform: uppercase; }}
    .stat-value {{ color: white; font-size: 22px; font-weight: bold; margin: 0; }}
    
    {rtl_css}
    
    /* =========================================
       📱 MOBILE RESPONSIVENESS (SMART SCREENS)
       ========================================= */
    @media (max-width: 768px) {{
        .block-container {{ padding-top: 2rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }}
        [data-testid="stDataFrame"] {{ overflow-x: auto !important; max-width: 100% !important; }}
        .banner h1, .full-width-banner h1 {{ font-size: 1.6rem !important; }}
        .banner p, .full-width-banner p {{ font-size: 0.9rem !important; }}
        .js-plotly-plot, .plotly, .plot-container {{ max-width: 100% !important; }}
        [data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; margin-bottom: 15px !important; }}
    }}
</style>
""", unsafe_allow_html=True)

# --- BANNER (REPLACES st.title) ---
st.markdown(f"""
<div class="full-width-banner">
    <div class="banner-overlay"></div>
    <div class="banner-content" {'dir="rtl"' if lang=="العربية" else ''}>
        <h1 style="color: white; margin: 0; font-size: 2.5rem; letter-spacing: 1px;">{txt['banner_h']}</h1>
        <p style="color:#e0e0e0; font-size:1.1rem; margin-top: 8px;">{txt['banner_desc']}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- DATA FETCHING ---
@st.cache_data(ttl=60)
def get_live_market_data():
    try:
        df = pd.read_csv("btp_market_data.csv")
        df["Price_MAD"] = pd.to_numeric(df["Price_MAD"], errors='coerce')
        return df
    except Exception as e:
        st.error(f"{txt['err']} {str(e)}")
        return None

df_live = get_live_market_data()

# --- UI & CHART LOGIC ---
if df_live is not None:
    with st.container(border=True):
        c_sel1, c_sel2, c_sel3, c_sel4 = st.columns([2, 2, 2, 1.5])
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
    c_stat1, c_stat2, c_stat3 = st.columns(3)
    with c_stat1:
        st.markdown(f"<div class='stat-card'><p class='stat-title'>{txt['curr_price']}</p><p class='stat-value'>{closes[-1]:,.2f} {sym}</p></div>", unsafe_allow_html=True)
    with c_stat2:
        st.markdown(f"<div class='stat-card'><p class='stat-title'>{txt['period_high']}</p><p class='stat-value' style='color:#2ca02c;'>{max_price:,.2f} {sym}</p></div>", unsafe_allow_html=True)
    with c_stat3:
        st.markdown(f"<div class='stat-card'><p class='stat-title'>{txt['period_low']}</p><p class='stat-value' style='color:#d62728;'>{min_price:,.2f} {sym}</p></div>", unsafe_allow_html=True)

    # Build Plotly Chart
    fig_m = go.Figure()
    
    if chart_type == txt["candle"]:
        fig_m.add_trace(go.Candlestick(x=dates, open=opens, high=highs, low=lows, close=closes, name="Price", increasing_line_color='#2ca02c', decreasing_line_color='#d62728'))
    else:
        fig_m.add_trace(go.Scatter(x=dates, y=closes, mode='lines', name="Price", line=dict(color='#f5b041', width=2), fill='tozeroy', fillcolor='rgba(245,176,65,0.1)'))
        
    # Add Moving Average (MA)
    if show_ma:
        # Calculate a simple 7-day moving average
        ma_period = 7 if num_days >= 7 else num_days
        ma_values = pd.Series(closes).rolling(window=ma_period).mean().values
        fig_m.add_trace(go.Scatter(x=dates, y=ma_values, mode='lines', name=f"MA ({ma_period}d)", line=dict(color='#1f77b4', width=2, dash='dot')))

    fig_m.update_layout(
        height=500, 
        title=f"{txt['chart_title']} - {selected_company} ({time_period})", 
        template="plotly_dark", 
        xaxis_rangeslider_visible=False,
        yaxis_title=f"Price ({sym})",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_m, use_container_width=True)
