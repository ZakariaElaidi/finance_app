import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
import json
import urllib.parse
from bs4 import BeautifulSoup
import concurrent.futures

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
        "pipeline_phase": "PHASE 1: DEAL ORIGINATION & MARKET SCREENING",
        "banner_h": "BTP Sector Market Screener", "banner_desc": "Identify undervalued targets within the Moroccan BTP sector based on live public comps.",
        "target_title": "🎯 Deal Origination Sandbox", "proj_name": "Target Code Name", "nm": "Target Net Margin (%)", "roe": "Target ROE (%)",
        "gearing": "Target Gearing (D/E %)", "pe": "Entry Multiple (P/E)", "help_gearing": "BTP average is ~80%.",
        "info_update": "💡 Analytics feed directly from Live Market Trading Data.", "data_title": "📊 Public Comps Table (Live Feed)",
        "p1_title": "⚖️ 1. Peer Comparison: Standalone Value", "select_peers": "Select Market Peers to Benchmark:",
        "p2_title": "⚠️ 2. Sector Risk/Reward Positioning", "p2_desc": "Evaluate target's cost of capital profile against market profitability.",
        "p3_title": "🕸️ 3. Strategic Fit Radar", "p3_desc": "Compare specific operational metrics against the broader sector.",
        "col_price": f"Share Price ({sym})", "your_target": "Identified Target", "market_peer": "Public Peer"
    },
    "Français": {
        "pipeline_phase": "PHASE 1: ORIGINATION DE DEALS & SCREENING",
        "banner_h": "Screener du Secteur BTP", "banner_desc": "Identifiez des cibles sous-évaluées sur la base de comparables boursiers en direct.",
        "target_title": "🎯 Sandbox d'Origination", "proj_name": "Nom de Code de la Cible", "nm": "Marge Nette Cible (%)", "roe": "ROE Cible (%)",
        "gearing": "Gearing Cible (D/CP %)", "pe": "Multiple d'Entrée (P/E)", "help_gearing": "La moyenne du BTP est d'environ 80%.",
        "info_update": "💡 Flux d'analyse basé sur les données de trading en direct.", "data_title": "📊 Table des Comparables Publics",
        "p1_title": "⚖️ 1. Comparaison: Valeur Intrinsèque", "select_peers": "Sélectionnez les pairs pour le benchmark:",
        "p2_title": "⚠️ 2. Positionnement Risque/Rendement Sectoriel", "p2_desc": "Évaluez le profil du coût du capital par rapport à la rentabilité.",
        "p3_title": "🕸️ 3. Radar d'Adéquation Stratégique", "p3_desc": "Comparez les métriques opérationnelles spécifiques avec le secteur.",
        "col_price": f"Prix de l'action ({sym})", "your_target": "Cible Identifiée", "market_peer": "Pair Public"
    },
    "Español": {
        "pipeline_phase": "FASE 1: ORIGINACIÓN DE ACUERDOS",
        "banner_h": "Filtro del Mercado del Sector BTP", "banner_desc": "Identifica objetivos infravalorados basados en comparables públicos en vivo.",
        "target_title": "🎯 Entorno de Originación", "proj_name": "Nombre en Clave del Objetivo", "nm": "Margen Neto Objetivo (%)", "roe": "ROE Objetivo (%)",
        "gearing": "Gearing Objetivo (D/C %)", "pe": "Múltiplo de Entrada (P/E)", "help_gearing": "El promedio de BTP es ~80%.",
        "info_update": "💡 Análisis basado directamente en datos de mercado en vivo.", "data_title": "📊 Tabla de Comparables Públicos",
        "p1_title": "⚖️ 1. Comparación: Valor Independiente", "select_peers": "Selecciona Pares para el Benchmark:",
        "p2_title": "⚠️ 2. Posicionamiento de Riesgo/Recompensa", "p2_desc": "Evalúa el perfil de costo de capital frente a la rentabilidad del mercado.",
        "p3_title": "🕸️ 3. Radar de Ajuste Estratégico", "p3_desc": "Compara métricas operativas específicas contra el sector en general.",
        "col_price": f"Precio de la Acción ({sym})", "your_target": "Objetivo Identificado", "market_peer": "Par Público"
    },
    "العربية": {
        "pipeline_phase": "المرحلة الأولى: اكتشاف الصفقات وتحليل السوق",
        "banner_h": "شاشة تحليل قطاع البناء", "banner_desc": "تحديد الشركات المقيمة بأقل من قيمتها الحقيقية بناءً على مقارنات السوق الحية.",
        "target_title": "🎯 بيئة اكتشاف الصفقات", "proj_name": "الاسم الرمزي للهدف", "nm": "هامش الربح المستهدف (%)", "roe": "العائد المستهدف (%)",
        "gearing": "الرافعة المالية المستهدفة (%)", "pe": "مضاعف الدخول (P/E)", "help_gearing": "متوسط القطاع حوالي 80%.",
        "info_update": "💡 تستمد التحليلات بياناتها مباشرة من السوق الحي.", "data_title": "📊 جدول المقارنات العامة (بيانات حية)",
        "p1_title": "⚖️ 1. مقارنة الأقران: القيمة المستقلة", "select_peers": "اختر المنافسين للمقارنة المرجعية:",
        "p2_title": "⚠️ 2. مصفوفة المخاطر والعوائد", "p2_desc": "تقييم ملف تكلفة رأس المال مقابل ربحية السوق.",
        "p3_title": "🕸️ 3. رادار الملاءمة الاستراتيجية", "p3_desc": "قارن مقاييس تشغيلية محددة مع القطاع بأكمله.",
        "col_price": f"سعر السهم ({sym})", "your_target": "الشركة المستهدفة", "market_peer": "منافس عام"
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
    
    /* Minimalist Header Styling replacing the image banner */
    .minimal-header {{ background: linear-gradient(135deg, rgba(22,26,34,0.8), rgba(31,119,180,0.15)); border-left: 5px solid #1f77b4; padding: 25px 30px; border-radius: 8px; margin-bottom: 30px; border-top: 1px solid rgba(255,255,255,0.05); border-right: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
    .minimal-header h1 {{ color: white; margin: 0; font-size: 2.2rem; letter-spacing: 0.5px; font-weight: 700; }}
    .minimal-header p {{ color: #a0aab5; font-size: 1.1rem; margin-top: 8px; margin-bottom: 0; }}
    
    /* Pipeline Indicator Styling */
    .pipeline-indicator {{ display: inline-block; background-color: rgba(31,119,180,0.2); border: 1px solid #1f77b4; color: #1f77b4; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; }}
    
    {rtl_css}
    
    @media (max-width: 768px) {{
        .block-container {{ padding-top: 2rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }}
        [data-testid="stDataFrame"] {{ overflow-x: auto !important; max-width: 100% !important; }}
        .minimal-header h1 {{ font-size: 1.6rem !important; }}
        .minimal-header p {{ font-size: 0.9rem !important; }}
        .js-plotly-plot, .plotly, .plot-container {{ max-width: 100% !important; }}
        [data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; margin-bottom: 15px !important; }}
    }}
</style>
""", unsafe_allow_html=True)

# --- MINIMALIST HEADER WITH PIPELINE INDICATOR ---
st.markdown(f"""
<div class="minimal-header" {'dir="rtl"' if lang=="العربية" else ''}>
    <div class="pipeline-indicator">{txt['pipeline_phase']}</div>
    <h1>{txt['banner_h']}</h1>
    <p>{txt['banner_desc']}</p>
</div>
""", unsafe_allow_html=True)

# --- MANUAL CACHE CLEAR BUTTON ---
col_clear1, col_clear2 = st.columns([4, 1])
with col_clear2:
    if st.button("🔄 Refresh Comps Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- THE ULTIMATE MARKETWATCH SCRAPER (NO API BLOCKS) ---
@st.cache_data(ttl=300, show_spinner=False)
def fetch_live_market_data_pro():
    fallbacks = {
        "LafargeHolcim": {"Price_MAD": 1780, "PE_Ratio": 18.2, "Net_Margin_%": 16.5, "ROE_%": 22.0, "Gearing_%": 45.0, "mw": "lhm", "yf": "LHM.CM"},
        "Addoha": {"Price_MAD": 33, "PE_Ratio": 12.0, "Net_Margin_%": 8.5, "ROE_%": 14.0, "Gearing_%": 120.0, "mw": "adh", "yf": "ADH.CM"},
        "Alliances": {"Price_MAD": 260, "PE_Ratio": 10.5, "Net_Margin_%": 9.0, "ROE_%": 15.5, "Gearing_%": 135.0, "mw": "adi", "yf": "ADI.CM"},
        "Ciments du Maroc": {"Price_MAD": 1750, "PE_Ratio": 16.8, "Net_Margin_%": 15.2, "ROE_%": 20.1, "Gearing_%": 40.0, "mw": "cma", "yf": "CMA.CM"},
        "TGCC": {"Price_MAD": 330, "PE_Ratio": 15.0, "Net_Margin_%": 12.5, "ROE_%": 18.5, "Gearing_%": 85.0, "mw": "tgc", "yf": "TGC.CM"},
        "Sonasid": {"Price_MAD": 870, "PE_Ratio": 14.5, "Net_Margin_%": 5.2, "ROE_%": 8.5, "Gearing_%": 20.0, "mw": "snd", "yf": "SND.CM"},
        "Jet Contractors": {"Price_MAD": 500, "PE_Ratio": 18.0, "Net_Margin_%": 6.0, "ROE_%": 12.0, "Gearing_%": 110.0, "mw": "jet", "yf": "JET.CM"},
        "Colorado": {"Price_MAD": 53, "PE_Ratio": 15.5, "Net_Margin_%": 8.5, "ROE_%": 11.0, "Gearing_%": 15.0, "mw": "col", "yf": "COL.CM"}
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    def fetch_price(name, data):
        # LAYER 1: MarketWatch HTML
        try:
            url_mw = f"https://www.marketwatch.com/investing/stock/{data['mw']}?countrycode=ma"
            res = requests.get(url_mw, headers=headers, timeout=5)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                price_tag = soup.find("bg-quote", class_="value")
                if price_tag:
                    val = float(price_tag.text.replace(",", "").strip())
                    if val > 0:
                        return name, val, "🟢 LIVE (MW)"
        except: pass

        # LAYER 2: Yahoo Finance HTML
        try:
            url_yf = f"https://finance.yahoo.com/quote/{data['yf']}"
            res = requests.get(url_yf, headers=headers, timeout=5)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                price_tag = soup.find("fin-streamer", {"data-symbol": data['yf'], "data-field": "regularMarketPrice"})
                if price_tag:
                    val = float(price_tag.text.replace(",", "").strip())
                    if val > 0:
                        return name, val, "🟢 LIVE (YF Html)"
        except: pass

        # LAYER 3: Google Finance via Proxy
        try:
            gf_url = f"https://www.google.com/finance/quote/{data['mw'].upper()}:CMA"
            proxy_url = f"https://api.allorigins.win/get?url={urllib.parse.quote(gf_url)}"
            res = requests.get(proxy_url, timeout=6)
            if res.status_code == 200:
                html = res.json().get('contents', '')
                soup = BeautifulSoup(html, 'html.parser')
                price_div = soup.find("div", class_="YMlKec fxKbKc")
                if price_div:
                    clean_price = price_div.text.replace("MAD", "").replace(",", "").replace(" ", "").replace("\xa0", "").strip()
                    val = float(clean_price)
                    if val > 0:
                        return name, val, "🟢 LIVE (GF Proxy)"
        except: pass

        return name, None, "🔴 Fallback"

    live_prices = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_price, name, data) for name, data in fallbacks.items()]
        for future in concurrent.futures.as_completed(futures):
            name, price, status = future.result()
            if price is not None:
                live_prices[name] = {"Price_MAD": price, "Data_Status": status}

    final_data = []
    for name, metrics in fallbacks.items():
        actual_price = metrics["Price_MAD"]
        status = "🔴 Fallback"

        if name in live_prices:
            actual_price = live_prices[name]["Price_MAD"]
            status = live_prices[name]["Data_Status"]

        final_data.append({
            "Company": name,
            "Price_MAD": actual_price,
            "Data_Status": status,
            "PE_Ratio": metrics["PE_Ratio"],
            "Net_Margin_%": metrics["Net_Margin_%"],
            "ROE_%": metrics["ROE_%"],
            "Gearing_%": metrics["Gearing_%"]
        })

    return pd.DataFrame(final_data)

with st.spinner("⚡ Connecting to Global Markets..."):
    df_live = fetch_live_market_data_pro().copy()
    df_live["Type"] = txt["market_peer"]
    df_live["Price_Converted"] = df_live["Price_MAD"] * rate

# --- TARGET INPUTS IN MAIN PAGE ---
st.markdown(f"### {txt['target_title']}")
with st.container(border=True):
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        target_name = st.text_input(txt["proj_name"], "Project Alpha")
    with col_in2:
        target_margin = st.number_input(txt["nm"], value=14.0, step=0.5)
    with col_in3:
        target_roe = st.number_input(txt["roe"], value=20.0, step=0.5)
        
    col_in4, col_in5, col_in6 = st.columns(3)
    with col_in4:
        target_gearing = st.number_input(txt["gearing"], value=60.0, step=5.0, help=txt["help_gearing"])
    with col_in5:
        target_pe = st.number_input(txt["pe"], value=13.0, step=0.5)
    with col_in6:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(txt["info_update"])

# Append Target to Dataframe
target_row = pd.DataFrame([{
    "Company": target_name, "Price_Converted": 0, "Data_Status": "🎯 Input",
    "PE_Ratio": target_pe, "Net_Margin_%": target_margin, "ROE_%": target_roe, 
    "Gearing_%": target_gearing, "Type": txt["your_target"]
}])
df_combined = pd.concat([target_row, df_live], ignore_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- RAW DATA TABLE ---
st.subheader(txt["data_title"])

def highlight_target(row):
    if row['Type'] == txt["your_target"]: return ['background-color: rgba(31, 119, 180, 0.25)'] * len(row)
    return [''] * len(row)

display_table = df_combined[["Company", "Type", "Data_Status", "Price_Converted", "PE_Ratio", "Net_Margin_%", "ROE_%", "Gearing_%"]].rename(
    columns={"Price_Converted": txt["col_price"], "Data_Status": "Feed Status"}
)

st.dataframe(
    display_table.style.apply(highlight_target, axis=1).format({
        txt["col_price"]: "{:,.2f}",
        "PE_Ratio": "{:.2f}x",
        "Net_Margin_%": "{:.2f}%",
        "ROE_%": "{:.2f}%",
        "Gearing_%": "{:.2f}%"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# --- THE UI (CHARTS) ---
st.subheader(txt["p1_title"])
peers = st.multiselect(txt["select_peers"], df_live["Company"].tolist(), default=df_live["Company"].tolist()[:5])

if peers:
    display_df = df_combined[(df_combined["Company"].isin(peers)) | (df_combined["Company"] == target_name)].copy()
    color_map = {target_name: "#1f77b4"}
    for peer in peers: color_map[peer] = "#a0aab5" 

    col_bar1, col_bar2 = st.columns(2)
    with col_bar1:
        fig_margin = px.bar(display_df, x="Company", y="Net_Margin_%", color="Company", color_discrete_map=color_map, title=txt["nm"])
        fig_margin.update_layout(template="plotly_dark", showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_margin, use_container_width=True)
        
    with col_bar2:
        fig_roe = px.bar(display_df, x="Company", y="ROE_%", color="Company", color_discrete_map=color_map, title=txt["roe"])
        fig_roe.update_layout(template="plotly_dark", showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_roe, use_container_width=True)

st.markdown("---")

# --- BTP RISK MATRIX & SPIDER WEB ---
col_matrix, col_radar = st.columns([1.2, 1], gap="large")

with col_matrix:
    st.subheader(txt["p2_title"])
    st.markdown(f"<p style='color:#b3b3b3; font-size:0.9rem;'>{txt['p2_desc']}</p>", unsafe_allow_html=True)
    
    fig_scatter = px.scatter(
        df_combined, x="Gearing_%", y="ROE_%", color="Type", text="Company", size_max=60,
        color_discrete_map={txt["your_target"]: "#1f77b4", txt["market_peer"]: "#a0aab5"} 
    )
    fig_scatter.update_traces(textposition='top center', marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')))
    
    avg_gearing = df_live["Gearing_%"].mean()
    avg_roe = df_live["ROE_%"].mean()
    fig_scatter.add_hline(y=avg_roe, line_dash="dash", line_color="gray", annotation_text="Avg ROE")
    fig_scatter.add_vline(x=avg_gearing, line_dash="dash", line_color="gray", annotation_text="Avg Debt")
    
    fig_scatter.update_layout(template="plotly_dark", xaxis_title=txt["gearing"], yaxis_title=txt["roe"], height=450)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_radar:
    st.subheader(txt["p3_title"])
    st.markdown(f"<p style='color:#b3b3b3; font-size:0.9rem;'>{txt['p3_desc']}</p>", unsafe_allow_html=True)
    
    categories = ['Net Margin', 'ROE', 'P/E Ratio', 'Financial Health']
    
    target_health = max(0, 150 - target_gearing) 
    market_health = max(0, 150 - df_live["Gearing_%"].mean())
    
    target_vals = [target_margin, target_roe, target_pe, target_health]
    market_vals = [df_live["Net_Margin_%"].mean(), df_live["ROE_%"].mean(), df_live["PE_Ratio"].mean(), market_health]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=target_vals, theta=categories, fill='toself', name=txt["your_target"], line_color='#1f77b4'))
    fig_radar.add_trace(go.Scatterpolar(r=market_vals, theta=categories, fill='toself', name=txt["market_peer"], line_color='#a0aab5')) 
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(max(target_vals), max(market_vals)) + 5])),
        showlegend=True, template="plotly_dark", height=450, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_radar, use_container_width=True)
