import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import timedelta, date

# Configuration de la page (Wide pour prendre tout l'écran)
st.set_page_config(page_title="Z.ELAIDI - Financial Analytics Hub", layout="wide", page_icon="📊")

# 1. BANNER DYNAMIC FULL WIDTH AVEC DRAPEAU MAROCAIN
st.markdown("""
<style>
@keyframes fadeinleft {
    from { opacity: 0; transform: translateX(-50px); }
    to   { opacity: 1; transform: translateX(0); }
}
.banner-container {
    position: relative;
    width: 100%;
    height: 280px;
    margin-bottom: 30px;
    border-radius: 12px;
    overflow: hidden;
    animation: fadeinleft 1.2s ease-out;
    box-shadow: 0 8px 16px rgba(0,0,0,0.4);
}
.banner-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.moroccan-badge {
    position: absolute;
    bottom: 20px;
    right: 20px;
    background: rgba(15, 15, 15, 0.85);
    color: white;
    padding: 10px 20px;
    border-radius: 30px;
    font-family: sans-serif;
    font-weight: 600;
    font-size: 16px;
    border: 1px solid #c1272d;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.5);
}
</style>
<div class="banner-container">
    <img class="banner-img" src="https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=2000&q=80" alt="Finance Banner">
    <div class="moroccan-badge">
        <img src="https://upload.wikimedia.org/wikipedia/commons/2/2c/Flag_of_Morocco.svg" width="28" style="border-radius:2px;">
        Casablanca Stock Exchange Focus
    </div>
</div>
""", unsafe_allow_html=True)

st.title("📊 Financial Analytics & Equity Research Hub")
st.markdown("---")

# Création des 3 Tabs
tab1, tab2, tab3 = st.tabs(["📈 Corporate Financial Analysis", "🏗️ BTP Sector Equity Research", "💹 Live Market Charts (MASI)"])

# ==========================================
# TAB 1: AUTOMATED FINANCIAL ANALYSIS (AVEC CIRCLES)
# ==========================================
with tab1:
    st.header("🔍 Automated Corporate Financial Analysis")
    st.markdown("Uploadi l-fichier Excel dial l-entreprise باش تخرج ليك l-analyse automatique f des graphiques circulaires.")
    
    uploaded_file = st.file_uploader("Choisissez le fichier Excel template", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            df_finance = pd.read_excel(uploaded_file)
            df_finance.columns = [str(c).strip() for c in df_finance.columns]
            df_finance.iloc[:, 0] = df_finance.iloc[:, 0].astype(str).str.strip()
            df_finance.set_index(df_finance.columns[0], inplace=True)
            
            st.subheader("📋 Données Financières Importées")
            st.dataframe(df_finance)
            
            col_2024 = [c for c in df_finance.columns if '2024' in str(c)][0]
            col_2025 = [c for c in df_finance.columns if '2025' in str(c)][0]
            
            rev_24, rev_25 = float(df_finance.loc["Revenue", col_2024]), float(df_finance.loc["Revenue", col_2025])
            net_24, net_25 = float(df_finance.loc["Net Income", col_2024]), float(df_finance.loc["Net Income", col_2025])
            ca_24, ca_25 = float(df_finance.loc["Current Assets", col_2024]), float(df_finance.loc["Current Assets", col_2025])
            cl_24, cl_25 = float(df_finance.loc["Current Liabilities", col_2024]), float(df_finance.loc["Current Liabilities", col_2025])
            eq_24, eq_25 = float(df_finance.loc["Total Equity", col_2024]), float(df_finance.loc["Total Equity", col_2025])
            
            current_ratio_25 = ca_25 / cl_25
            net_margin_25 = (net_25 / rev_25) * 100
            roe_25 = (net_25 / eq_25) * 100
            
            st.subheader("📊 Ratios Clés de Performance (Visualisation)")
            col1, col2, col3 = st.columns(3)
            
            # GAUGE CHART 1: Current Ratio
            fig1 = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = current_ratio_25,
                title = {'text': "Current Ratio", 'font': {'size': 20}},
                gauge = {'axis': {'range': [0, 3]}, 'bar': {'color': "#2ca02c"}, 'steps': [{'range': [0, 1], 'color': "#d62728"}, {'range': [1, 1.5], 'color': "#ff7f0e"}]}
            ))
            fig1.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10), template="plotly_dark")
            col1.plotly_chart(fig1, use_container_width=True)
            
            # GAUGE CHART 2: Marge Nette
            fig2 = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = net_margin_25,
                number = {'suffix': "%"},
                title = {'text': "Marge Nette", 'font': {'size': 20}},
                gauge = {'axis': {'range': [0, 30]}, 'bar': {'color': "#1f77b4"}}
            ))
            fig2.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10), template="plotly_dark")
            col2.plotly_chart(fig2, use_container_width=True)
            
            # GAUGE CHART 3: ROE
            fig3 = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = roe_25,
                number = {'suffix': "%"},
                title = {'text': "Return on Equity (ROE)", 'font': {'size': 20}},
                gauge = {'axis': {'range': [0, 40]}, 'bar': {'color': "#9467bd"}}
            ))
            fig3.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10), template="plotly_dark")
            col3.plotly_chart(fig3, use_container_width=True)
            
            # Rapport
            st.info("💡 **Analyse:** Visualisation générée avec succès. Les indicateurs dans la zone verte/bleue montrent une bonne santé financière.")
            
        except Exception as e:
            st.error(f"Erreur de lecture du fichier. Détails: {e}")

# ==========================================
# TAB 2: EQUITY RESEARCH
# ==========================================
with tab2:
    st.header("🏗️ BTP Sector Market Dashboard (Casablanca)")
    try:
        df_btp = pd.read_csv("btp_market_data.csv")
        df_btp["Price_MAD"] = pd.to_numeric(df_btp["Price_MAD"])
        df_btp["PE_Ratio"] = pd.to_numeric(df_btp["PE_Ratio"])
        
        st.dataframe(df_btp.style.highlight_max(axis=0, subset=["Market_Cap_Billion", "PE_Ratio"], color="#1f77b4"))
        
        fig = px.bar(df_btp, x="Company", y="PE_Ratio", color="Company", title="P/E Ratio par Entreprise (BTP Maroc)", text_auto=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur de chargement des données BTP: {e}")

# ==========================================
# TAB 3: LIVE MARKET CHARTS (Options & Bigger Candles)
# ==========================================
with tab3:
    st.header("💹 Simulation Bourse de Casablanca (MASI Live Trend)")
    
    try:
        col_sel1, col_sel2 = st.columns([1, 1])
        with col_sel1:
            selected_company = st.selectbox("Sélectionnez l'entreprise à analyser:", df_btp["Company"].tolist())
        with col_sel2:
            chart_type = st.radio("Style d'affichage du graphique:", ["Bougies (Candlesticks)", "Ligne (Line Chart)"], horizontal=True)
        
        # Génération de données avec plus de volatilité pour des bougies plus grandes
        base_price = df_btp[df_btp["Company"] == selected_company]["Price_MAD"].values[0]
        dates = pd.date_range(end=pd.Timestamp.today(), periods=40)
        np.random.seed(42 + len(selected_company))
        
        volatility = base_price * 0.04 # Augmenté pour avoir des candles plus grandes
        price_changes = np.random.normal(0, volatility, size=40)
        close_prices = base_price + np.cumsum(price_changes)
        open_prices = close_prices - np.random.normal(0, volatility/1.5, size=40)
        high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.normal(0, volatility/2, size=40))
        low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.normal(0, volatility/2, size=40))
        
        if chart_type == "Bougies (Candlesticks)":
            fig_market = go.Figure(data=[go.Candlestick(x=dates, open=open_prices, high=high_prices, low=low_prices, close=close_prices,
                                                        increasing_line_color='#00ff00', decreasing_line_color='#ff0000')])
        else:
            fig_market = go.Figure(data=[go.Scatter(x=dates, y=close_prices, mode='lines+markers', line=dict(color='#1f77b4', width=3))])
            
        # Height augmenté à 650 pour des bougies super grandes et claires
        fig_market.update_layout(height=650, title=f"Evolution du cours - {selected_company}",
                                 yaxis_title="Prix (MAD)", template="plotly_dark", xaxis_rangeslider_visible=False,
                                 margin=dict(l=20, r=20, t=50, b=20))
        
        st.plotly_chart(fig_market, use_container_width=True)
    except Exception as e:
        st.warning("Veuillez vérifier les données pour afficher le graphique.")

# ==========================================
# FOOTER: BY ELAIDI ZAKARIA
# ==========================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #a0a0a0; font-size: 15px; letter-spacing: 1px;'>
        © 2026 | Automated Financial Analytics Platform | <b>By ELAIDI ZAKARIA</b>
    </div>
    """, 
    unsafe_allow_html=True
)
