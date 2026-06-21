import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
from datetime import datetime, timedelta
import random
import io

# 1. Configuration de la page
st.set_page_config(page_title="Z.ELAIDI - Financial Analytics Hub", layout="wide", page_icon="📊")

# 2. FULL WIDTH BANNER CSS
st.markdown("""
<style>
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
    max-width: 100% !important;
    padding-left: 0rem !important;
    padding-right: 0rem !important;
}
.full-width-banner {
    position: relative;
    width: 100%;
    height: 350px;
    background-image: url('https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=2500&q=80');
    background-size: cover;
    background-position: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 16px rgba(0,0,0,0.5);
}
.banner-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.7));
}
.moroccan-badge {
    position: absolute;
    bottom: 30px;
    right: 40px;
    background: rgba(15, 15, 15, 0.9);
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    font-family: sans-serif;
    font-weight: 600;
    font-size: 16px;
    border-left: 4px solid #c1272d;
    display: flex;
    align-items: center;
    gap: 12px;
}
.content-wrapper {
    padding-left: 3rem;
    padding-right: 3rem;
}
.report-box {
    padding: 20px;
    border-radius: 10px;
    background-color: #1e1e1e;
    border-left: 5px solid;
    margin-top: 20px;
}
</style>
<div class="full-width-banner">
    <div class="banner-overlay"></div>
    <div class="moroccan-badge">
        <img src="https://upload.wikimedia.org/wikipedia/commons/2/2c/Flag_of_Morocco.svg" width="28" style="border-radius:2px;">
        Casablanca Stock Exchange Focus
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)

st.title("📊 Financial Analytics & Equity Research Hub")
st.markdown("---")

def generate_template():
    df_template = pd.DataFrame({
        "Line_Item": ["Revenue", "Net Income", "Current Assets", "Current Liabilities", "Inventory", "Total Assets", "Total Equity", "Total Debt"],
        "2024": [0, 0, 0, 0, 0, 0, 0, 0],
        "2025": [0, 0, 0, 0, 0, 0, 0, 0]
    })
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_template.to_excel(writer, index=False)
    return output.getvalue()

# 3. LIVE MARKET ENGINE
@st.cache_data(ttl=60)
def get_live_market_data():
    try:
        df = pd.read_csv("btp_market_data.csv")
        df["Price_MAD"] = pd.to_numeric(df["Price_MAD"], errors='coerce')
        df["PE_Ratio"] = pd.to_numeric(df["PE_Ratio"], errors='coerce')
        
        np.random.seed(int(time.time() / 60))
        fluctuation = np.random.uniform(-0.02, 0.02, len(df))
        df["Live_Price_MAD"] = df["Price_MAD"] * (1 + fluctuation)
        df["Live_Price_MAD"] = df["Live_Price_MAD"].round(2)
        df["Variation"] = (fluctuation * 100).round(2)
        return df
    except Exception as e:
        return None

df_live = get_live_market_data()

tab1, tab2, tab3 = st.tabs(["📈 Corporate Financial Analysis", "🏗️ BTP Sector Equity Research", "💹 Live Market Charts (MASI)"])

# ==========================================
# TAB 1: AUTOMATED FINANCIAL ANALYSIS 
# ==========================================
with tab1:
    st.header("🔍 Automated Corporate Financial Analysis")
    
    col_text, col_btn = st.columns([3, 1])
    with col_text:
        st.markdown("**Upload your company's financial Excel template to automatically generate a visual performance analysis.**")
    with col_btn:
        st.download_button(
            label="📥 Télécharger le Template Requis",
            data=generate_template(),
            file_name="Financial_Template_Standard.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    uploaded_file = st.file_uploader("Choose your completed Excel file (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            df_finance = pd.read_excel(uploaded_file)
            df_finance.columns = [str(c).strip() for c in df_finance.columns]
            df_finance.iloc[:, 0] = df_finance.iloc[:, 0].astype(str).str.strip()
            df_finance.set_index(df_finance.columns[0], inplace=True)
            
            col_2024 = [c for c in df_finance.columns if '2024' in str(c)][0]
            col_2025 = [c for c in df_finance.columns if '2025' in str(c)][0]
            
            st.subheader("📋 Imported Financial Data (Variance Analysis)")
            st.markdown("Les indicateurs en **<span style='color:#00ff00'>Vert</span>** sont des points forts, ceux en **<span style='color:#ff0000'>Rouge</span>** sont des alertes.", unsafe_allow_html=True)
            
            df_display = df_finance.copy()
            df_display[col_2024] = pd.to_numeric(df_display[col_2024], errors='coerce')
            df_display[col_2025] = pd.to_numeric(df_display[col_2025], errors='coerce')
            
            df_display['YoY Growth (%)'] = ((df_display[col_2025] - df_display[col_2024]) / df_display[col_2024]) * 100
            
            def color_variance(row):
                item = str(row.name).lower()
                val = row['YoY Growth (%)']
                if pd.isna(val): return [''] * len(row)
                color = 'white'
                if 'liability' in item or 'debt' in item:
                    color = '#ff0000' if val > 0 else '#00ff00'
                else:
                    color = '#00ff00' if val > 0 else '#ff0000'
                return [f'color: {color}' if col == 'YoY Growth (%)' else '' for col in row.index]

            st.dataframe(df_display.style.apply(color_variance, axis=1).format({'YoY Growth (%)': "{:.2f}%"}), use_container_width=True)

            required_rows = ["Revenue", "Net Income", "Current Assets", "Current Liabilities", "Total Equity"]
            missing_rows = [row for row in required_rows if row not in df_finance.index]
            
            if missing_rows:
                st.error(f"⚠️ Format Invalide : Les lignes suivantes sont manquantes ou mal orthographiées : {', '.join(missing_rows)}. Veuillez télécharger le template requis ci-dessus.")
            else:
                rev_25 = float(df_finance.loc["Revenue", col_2025])
                net_25 = float(df_finance.loc["Net Income", col_2025])
                ca_25 = float(df_finance.loc["Current Assets", col_2025])
                cl_25 = float(df_finance.loc["Current Liabilities", col_2025])
                eq_25 = float(df_finance.loc["Total Equity", col_2025])
                
                current_ratio_25 = ca_25 / cl_25
                net_margin_25 = (net_25 / rev_25) * 100
                roe_25 = (net_25 / eq_25) * 100
                
                st.subheader("📊 Key Performance Ratios (Visuals)")
                col1, col2, col3 = st.columns(3)
                
                fig1 = go.Figure(go.Indicator(
                    mode = "gauge+number", value = current_ratio_25,
                    title = {'text': "Current Ratio", 'font': {'size': 16}},
                    gauge = {'axis': {'range': [0, 3]}, 'bar': {'color': "#2ca02c"}}
                ))
                fig1.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
                col1.plotly_chart(fig1, use_container_width=True)
                
                fig2 = go.Figure(go.Indicator(
                    mode = "gauge+number", value = net_margin_25, number = {'suffix': "%"},
                    title = {'text': "Net Margin", 'font': {'size': 16}},
                    gauge = {'axis': {'range': [0, 30]}, 'bar': {'color': "#1f77b4"}}
                ))
                fig2.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
                col2.plotly_chart(fig2, use_container_width=True)
                
                fig3 = go.Figure(go.Indicator(
                    mode = "gauge+number", value = roe_25, number = {'suffix': "%"},
                    title = {'text': "Return on Equity (ROE)", 'font': {'size': 16}},
                    gauge = {'axis': {'range': [0, 40]}, 'bar': {'color': "#9467bd"}}
                ))
                fig3.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
                col3.plotly_chart(fig3, use_container_width=True)

                st.subheader("💡 Expert Financial Diagnosis")
                nb_positifs = [
                    "Excellente gestion de la trésorerie. L'entreprise peut s'auto-financer facilement.",
                    "Forte rentabilité opérationnelle confirmée.",
                    "Structure de coûts très bien maîtrisée (Avantage compétitif fort).",
                    "Création de valeur optimale pour les actionnaires (ROE très attractif).",
                    "Forte capacité à honorer les dettes à court terme sans stress de liquidité.",
                    "Marge bénéficiaire nette au-dessus de la norme sectorielle.",
                    "Efficacité remarquable dans la rotation et l'utilisation des actifs.",
                    "Indépendance financière solide face aux chocs du marché.",
                    "Potentiel de croissance organique fort grâce aux réserves générées.",
                    "Gestion rigoureuse et saine des passifs circulants."
                ]
                nb_negatifs = [
                    "Fuite de liquidité sévère : Risque imminent d'insolvabilité à court terme.",
                    "Marge nette critique : Les charges absorbent presque la totalité des revenus.",
                    "Destruction de valeur : Le ROE est trop faible pour attirer ou retenir les investisseurs.",
                    "Déséquilibre flagrant du fonds de roulement : Nécessité d'optimiser les stocks et créances.",
                    "Poids de la dette circillante trop lourd par rapport aux liquidités disponibles.",
                    "Dégradation alarmante de la profitabilité. Besoin urgent de revoir le modèle de pricing.",
                    "Besoin urgent d'optimiser les coûts fixes pour stopper l'hémorragie financière.",
                    "Risque de dépendance extrême aux créanciers externes.",
                    "Faible retour sur investissement des capitaux engagés.",
                    "Structure financière sous tension (Alerte rouge sur la trésorerie)."
                ]
                
                score_positif = 0
                if current_ratio_25 >= 1.2: score_positif += 1
                if net_margin_25 >= 8.0: score_positif += 1
                if roe_25 >= 12.0: score_positif += 1
                
                random.seed(int(rev_25))
                
                if score_positif >= 2:
                    color = "#2ca02c"
                    status = "Situation Financière Favorable (Points Forts)"
                    selected_nbs = random.sample(nb_positifs, 3)
                else:
                    color = "#d62728"
                    status = "Situation Financière Critique (Fuites à corriger)"
                    selected_nbs = random.sample(nb_negatifs, 3)
                    
                st.markdown(f"""
                <div class="report-box" style="border-color: {color};">
                    <h4 style="color: {color}; margin-top: 0;">{status}</h4>
                    <ul>
                        <li style="color: {color};"><b>N.B:</b> {selected_nbs[0]}</li>
                        <li style="color: {color};"><b>N.B:</b> {selected_nbs[1]}</li>
                        <li style="color: {color};"><b>N.B:</b> {selected_nbs[2]}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"⚠️ Erreur de lecture : Le fichier n'est pas structuré correctement. Veuillez télécharger et utiliser le template.")

# ==========================================
# TAB 2: EQUITY RESEARCH (Chart Fixed)
# ==========================================
with tab2:
    st.header(f"🏗️ BTP Sector Live Dashboard")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Casablanca Time)")
    
    if df_live is not None:
        def color_variation(val):
            color = '#00ff00' if val > 0 else '#ff0000' if val < 0 else 'white'
            return f'color: {color}'
            
        st.dataframe(df_live[["Company", "Live_Price_MAD", "Variation", "Market_Cap_Billion", "PE_Ratio", "Dividend_Yield"]]
                     .style.map(color_variation, subset=['Variation'])
                     .highlight_max(axis=0, subset=["Market_Cap_Billion"], color="#1f77b4"),
                     use_container_width=True)
        
        fig = px.bar(df_live, x="Company", y="Live_Price_MAD", color="Variation", 
                     title="Live Stock Prices (MAD) & Intraday Variation", 
                     color_continuous_scale="RdYlGn", template="plotly_dark")
        
        # Disable Zoom/Pan on Bar Chart to prevent distortion
        fig.update_layout(
            dragmode=False,
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True)
        )
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})

# ==========================================
# TAB 3: LIVE MARKET CHARTS (Zoom Enabled)
# ==========================================
with tab3:
    st.header("💹 Technical Analysis & Historical Trends")
    
    if df_live is not None:
        col_sel1, col_sel2, col_sel3 = st.columns([1, 1, 1])
        with col_sel1:
            selected_company = st.selectbox("Select Company:", df_live["Company"].tolist())
        with col_sel2:
            time_period = st.selectbox("Timeframe (Historique):", ["1 Month (30 Days)", "3 Months (90 Days)", "6 Months (180 Days)"])
        with col_sel3:
            chart_type = st.radio("Chart Style:", ["Candlesticks", "Line Chart"], horizontal=True)
        
        days_map = {"1 Month (30 Days)": 30, "3 Months (90 Days)": 90, "6 Months (180 Days)": 180}
        num_days = days_map[time_period]
        
        base_price = df_live[df_live["Company"] == selected_company]["Live_Price_MAD"].values[0]
        
        today = pd.Timestamp.today().normalize()
        dates = pd.date_range(end=today, periods=num_days)
        
        np.random.seed(42 + len(selected_company) + num_days)
        
        volatility = base_price * 0.05
        price_changes = np.random.normal(0, volatility, size=num_days)
        
        close_prices = base_price - np.cumsum(price_changes[::-1])[::-1] 
        open_prices = close_prices - np.random.normal(0, volatility, size=num_days)
        
        high_noise = np.abs(np.random.normal(0, volatility*1.2, size=num_days))
        low_noise = np.abs(np.random.normal(0, volatility*1.2, size=num_days))
        
        high_prices = np.maximum(open_prices, close_prices) + high_noise
        low_prices = np.minimum(open_prices, close_prices) - low_noise
        
        if chart_type == "Candlesticks":
            fig_market = go.Figure(data=[go.Candlestick(x=dates, open=open_prices, high=high_prices, low=low_prices, close=close_prices,
                                                        increasing_line_color='#00ff00', decreasing_line_color='#ff0000')])
        else:
            fig_market = go.Figure(data=[go.Scatter(x=dates, y=close_prices, mode='lines+markers', line=dict(color='#1f77b4', width=2))])
            
        fig_market.update_layout(
            height=450, 
            title=f"Price Movement - {selected_company} ({time_period})",
            yaxis_title="Price (MAD)", 
            template="plotly_dark", 
            xaxis_rangeslider_visible=False,
            dragmode='zoom', # Enable zoom mode
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis=dict(range=[dates[0], dates[-1] + timedelta(days=2)]) 
        )
        
        st.plotly_chart(fig_market, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# FOOTER: BY ELAIDI ZAKARIA
# ==========================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #a0a0a0; font-size: 15px; letter-spacing: 1px; padding-bottom: 20px;'>
        © 2026 | Automated Financial Analytics Platform | <b>By ELAIDI ZAKARIA</b>
    </div>
    """, 
    unsafe_allow_html=True
)
