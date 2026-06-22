import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
from bs4 import BeautifulSoup
import yfinance as yf

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
        "banner_h": "🏗️ BTP Sector Benchmark", "banner_desc": "Compare your target company against Casablanca Stock Exchange peers.",
        "target_title": "🎯 Configure Target Data", "proj_name": "Project Name", "nm": "Net Margin (%)", "roe": "ROE (%)",
        "gearing": "Gearing (Debt/Equity %)", "pe": "Implied P/E Ratio", "help_gearing": "BTP average is ~80%.",
        "info_update": "💡 Charts and tables update automatically with LIVE Market Data.", "data_title": "📊 Live Market Data Overview",
        "p1_title": "⚖️ 1. Peer Comparison: Profitability & Returns", "select_peers": "Select Competitors to Compare:",
        "p2_title": "⚠️ 2. BTP Risk/Reward Matrix", "p2_desc": "Compares Profitability (ROE) vs Financial Risk (Gearing).",
        "p3_title": "🕸️ 3. 360° Sector Profile", "p3_desc": "Radar chart comparing your target against the market average.",
        "col_price": f"Price ({sym})", "your_target": "Your Target", "market_peer": "Market Peer"
    },
    "Français": {
        "banner_h": "🏗️ Benchmark du Secteur BTP", "banner_desc": "Comparez votre entreprise cible avec ses pairs de la Bourse de Casablanca.",
        "target_title": "🎯 Configurer les Données Cibles", "proj_name": "Nom du Projet", "nm": "Marge Nette (%)", "roe": "ROE (%)",
        "gearing": "Gearing (Dette/Capitaux Propres %)", "pe": "Ratio P/E Implicite", "help_gearing": "La moyenne du BTP est d'environ 80%.",
        "info_update": "💡 Les graphiques se mettent à jour automatiquement (Données en temps réel).", "data_title": "📊 Données du Marché en Direct",
        "p1_title": "⚖️ 1. Comparaison: Rentabilité & Rendements", "select_peers": "Sélectionnez les concurrents à comparer :",
        "p2_title": "⚠️ 2. Matrice Risque/Rendement BTP", "p2_desc": "Compare la Rentabilité (ROE) au Risque Financier (Gearing).",
        "p3_title": "🕸️ 3. Profil Sectoriel à 360°", "p3_desc": "Graphique radar comparant votre cible à la moyenne du marché.",
        "col_price": f"Prix ({sym})", "your_target": "Votre Cible", "market_peer": "Pair du Marché"
    },
    "Español": {
        "banner_h": "🏗️ Benchmark del Sector BTP", "banner_desc": "Compara tu empresa objetivo con sus pares de la Bolsa de Casablanca.",
        "target_title": "🎯 Configurar Datos Objetivo", "proj_name": "Nombre del Proyecto", "nm": "Margen Neto (%)", "roe": "ROE (%)",
        "gearing": "Gearing (Deuda/Capital %)", "pe": "Ratio P/E Implícito", "help_gearing": "El promedio de BTP es ~80%.",
        "info_update": "💡 Los gráficos se actualizan automáticamente (Datos en tiempo real).", "data_title": "📊 Resumen de Datos del Mercado",
        "p1_title": "⚖️ 1. Comparación: Rentabilidad y Retornos", "select_peers": "Selecciona competidores para comparar:",
        "p2_title": "⚠️ 2. Matriz de Riesgo/Recompensa BTP", "p2_desc": "Compara Rentabilidad (ROE) vs Riesgo Financiero (Gearing).",
        "p3_title": "🕸️ 3. Perfil Sectorial 360°", "p3_desc": "Gráfico de radar que compara tu objetivo con el promedio del mercado.",
        "col_price": f"Precio ({sym})", "your_target": "Tu Objetivo", "market_peer": "Par del Mercado"
    },
    "العربية": {
        "banner_h": "🏗️ مقارنة أداء قطاع البناء", "banner_desc": "قارن شركتك المستهدفة مع نظيراتها في بورصة الدار البيضاء.",
        "target_title": "🎯 إعداد بيانات الشركة المستهدفة", "proj_name": "اسم المشروع", "nm": "هامش الربح الصافي (%)", "roe": "العائد على حقوق المساهمين (%)",
        "gearing": "الرافعة المالية (الديون/حقوق الملكية %)", "pe": "مكرر الربحية الضمني", "help_gearing": "متوسط القطاع حوالي 80%.",
        "info_update": "💡 يتم تحديث الرسوم البيانية تلقائيًا (بيانات حية).", "data_title": "📊 بيانات السوق الحية",
        "p1_title": "⚖️ 1. مقارنة الأقران: الربحية والعوائد", "select_peers": "اختر المنافسين للمقارنة:",
        "p2_title": "⚠️ 2. مصفوفة المخاطر والمكافآت", "p2_desc": "يقارن الربحية مقابل المخاطر المالية (الرافعة المالية).",
        "p3_title": "🕸️ 3. ملف تعريف القطاع 360 درجة", "p3_desc": "رسم بياني راداري يقارن شركتك مع متوسط السوق.",
        "col_price": f"السعر ({sym})", "your_target": "شركتك المستهدفة", "market_peer": "منافس في السوق"
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
    [data-testid="stSidebarNav"] li:first-child a span {{ display: none !important; }}
    [data-testid="stSidebarNav"] li:first-child a::after {{ content: "🏠 Home"; font-size: 15px; margin-left: 0px; }}
    
    .full-width-banner {{ position: relative; width: 100%; height: 250px; background-image: url('https://images.unsplash.com/photo-1541888086425-d81bb19240f5?q=80&w=2070&auto=format&fit=crop'); background-size: cover; background-position: center; margin-bottom: 25px; border-radius: 10px; border-left: 5px solid #2ca02c; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
    .banner-overlay {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, rgba(14,17,23,1) 0%, rgba(14,17,23,0.8) 40%, rgba(44,160,44,0.2) 100%); }}
    .banner-content {{ position: absolute; top: 50%; left: 30px; transform: translateY(-50%); z-index: 2; }}
    {rtl_css}
</style>
""", unsafe_allow_html=True)

# --- BANNER ---
st.markdown(f"""
<div class="full-width-banner">
    <div class="banner-overlay"></div>
    <div class="banner-content" {'dir="rtl"' if lang=="العربية" else ''}>
        <h1 style="color: white; margin: 0; font-size: 2.5rem; letter-spacing: 1px;">{txt['banner_h']}</h1>
        <p style="color:#e0e0e0; font-size:1.1rem; margin-top: 8px;">{txt['banner_desc']}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- HYBRID LIVE MARKET DATA ENGINE ---
@st.cache_data(ttl=900) # Cache for 15 mins
def get_live_market_data():
    targets = {
        "LafargeHolcim": {"yf": "LHM.CM", "gf": "LHM:CMA"},
        "Addoha": {"yf": "ADH.CM", "gf": "ADH:CMA"},
        "Alliances": {"yf": "ADI.CM", "gf": "ADI:CMA"},
        "Ciments du Maroc": {"yf": "CMA.CM", "gf": "CMA:CMA"},
        "TGCC": {"yf": "TGC.CM", "gf": "TGC:CMA"},
        "Sonasid": {"yf": "SND.CM", "gf": "SND:CMA"},
        "Jet Contractors": {"yf": "JET.CM", "gf": "JET:CMA"},
        "Colorado": {"yf": "COL.CM", "gf": "COL:CMA"}
    }
    
    # Modern User-Agent to prevent bot blocking
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    data_list = []
    
    for name, tkrs in targets.items():
        live_price = None
        source = "🔴 Fallback"
        
        # 1. Try Yahoo Finance First
        try:
            stock = yf.Ticker(tkrs["yf"])
            hist = stock.history(period="1d")
            if not hist.empty:
                live_price = float(hist['Close'].iloc[-1])
                source = "🟢 LIVE (YF)"
        except:
            pass
            
        # 2. Try Google Finance Web Scraper if YF fails
        if live_price is None:
            try:
                url = f"https://www.google.com/finance/quote/{tkrs['gf']}"
                res = requests.get(url, headers=headers, timeout=5)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    price_div = soup.find("div", class_="YMlKec fxKbKc")
                    if price_div:
                        clean_price = price_div.text.replace("MAD", "").replace(",", "").replace(" ", "").strip()
                        live_price = float(clean_price)
                        source = "🟢 LIVE (GF)"
            except:
                pass
                
        data_list.append({
            "Company": name,
            "Price_MAD": live_price,
            "Data_Status": source
        })
        
    df_live = pd.DataFrame(data_list)
    
    # Fundamental Constants (Fallbacks & Ratios)
    fallbacks = {
        "LafargeHolcim": {"Price_MAD": 1800, "PE_Ratio": 18.2, "Net_Margin_%": 16.5, "ROE_%": 22.0, "Gearing_%": 45.0},
        "Addoha": {"Price_MAD": 25, "PE_Ratio": 12.0, "Net_Margin_%": 8.5, "ROE_%": 14.0, "Gearing_%": 120.0},
        "Alliances": {"Price_MAD": 120, "PE_Ratio": 10.5, "Net_Margin_%": 9.0, "ROE_%": 15.5, "Gearing_%": 135.0},
        "Ciments du Maroc": {"Price_MAD": 1500, "PE_Ratio": 16.8, "Net_Margin_%": 15.2, "ROE_%": 20.1, "Gearing_%": 40.0},
        "TGCC": {"Price_MAD": 300, "PE_Ratio": 15.0, "Net_Margin_%": 12.5, "ROE_%": 18.5, "Gearing_%": 85.0},
        "Sonasid": {"Price_MAD": 850, "PE_Ratio": 14.5, "Net_Margin_%": 5.2, "ROE_%": 8.5, "Gearing_%": 20.0},
        "Jet Contractors": {"Price_MAD": 350, "PE_Ratio": 18.0, "Net_Margin_%": 6.0, "ROE_%": 12.0, "Gearing_%": 110.0},
        "Colorado": {"Price_MAD": 55, "PE_Ratio": 15.5, "Net_Margin_%": 8.5, "ROE_%": 11.0, "Gearing_%": 15.0}
    }
    
    final_data = []
    for name, metrics in fallbacks.items():
        row = df_live[df_live["Company"] == name]
        actual_price = metrics["Price_MAD"]
        status = "🔴 Fallback"
        
        if not row.empty:
            val = row["Price_MAD"].values[0]
            if pd.notnull(val):
                actual_price = val
                status = row["Data_Status"].values[0]
        
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

with st.spinner("🔄 Booting Hybrid Live Engine (Connecting to Markets)..."):
    df_live = get_live_market_data().copy()
    df_live["Type"] = txt["market_peer"]
    # Apply currency rate
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

# --- RAW DATA TABLE (WITH TRANSPARENCY COLUMN) ---
st.subheader(txt["data_title"])

def highlight_target(row):
    if row['Type'] == txt["your_target"]: return ['background-color: rgba(245, 176, 65, 0.15)'] * len(row)
    return [''] * len(row)

# Show Data_Status so the user can verify if data is Live or Cached
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
    color_map = {target_name: "#f5b041"}
    for peer in peers: color_map[peer] = "#2ca02c" 

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
        color_discrete_map={txt["your_target"]: "#f5b041", txt["market_peer"]: "#2ca02c"} 
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
    fig_radar.add_trace(go.Scatterpolar(r=target_vals, theta=categories, fill='toself', name=txt["your_target"], line_color='#f5b041'))
    fig_radar.add_trace(go.Scatterpolar(r=market_vals, theta=categories, fill='toself', name=txt["market_peer"], line_color='#2ca02c')) 
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(max(target_vals), max(market_vals)) + 5])),
        showlegend=True, template="plotly_dark", height=450, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_radar, use_container_width=True)
