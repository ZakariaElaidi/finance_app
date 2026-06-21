import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- SECURITY: Redirect if not logged in ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

# --- UI STYLING & CSS ---
st.markdown("""
<style>
    [data-testid="stSidebarNav"] li:first-child a span { display: none !important; }
    [data-testid="stSidebarNav"] li:first-child a::after { content: "🏠 Home"; font-size: 15px; margin-left: 0px; }
    .banner { background: linear-gradient(90deg, #0e1621 0%, #1f77b4 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #2ca02c; }
    .banner h1 { color: white; margin: 0; font-size: 2rem; }
    .banner p { color: #e0e0e0; margin: 0; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="banner">
    <h1>🏗️ BTP Sector Benchmark</h1>
    <p>Compare your target company against Casablanca Stock Exchange peers.</p>
</div>
""", unsafe_allow_html=True)

# --- FETCH MARKET DATA & SIMULATE BTP METRICS ---
@st.cache_data(ttl=60)
def get_live_market_data():
    try:
        df = pd.read_csv("btp_market_data.csv")
        df["Price_MAD"] = pd.to_numeric(df["Price_MAD"], errors='coerce')
        df["PE_Ratio"] = pd.to_numeric(df["PE_Ratio"], errors='coerce')
        
        np.random.seed(42)
        # Simulating metrics relevant to BTP (if not in CSV)
        df["Net_Margin_%"] = np.random.uniform(5, 18, len(df)).round(2)
        df["ROE_%"] = np.random.uniform(10, 25, len(df)).round(2)
        df["Gearing_%"] = np.random.uniform(30, 150, len(df)).round(2) # Debt to Equity (Crucial for BTP)
        df["Type"] = "Market Peer"
        return df
    except Exception: 
        # Fallback dummy data if CSV fails
        data = {
            "Company": ["TGCC", "LafargeHolcim", "Addoha", "Alliances", "Sonasid", "Ciments du Maroc"],
            "Price_MAD": [300, 1800, 25, 120, 700, 1500],
            "PE_Ratio": [15, 18, 12, 10, 14, 16],
            "Net_Margin_%": [12.5, 16.0, 8.5, 9.0, 6.5, 15.2],
            "ROE_%": [18.5, 22.0, 14.0, 15.5, 10.0, 20.1],
            "Gearing_%": [85.0, 45.0, 120.0, 135.0, 30.0, 40.0],
            "Type": ["Market Peer"] * 6
        }
        return pd.DataFrame(data)

df_live = get_live_market_data()

# --- SIDEBAR: TARGET COMPANY INPUT ---
st.sidebar.markdown("### 🎯 Your Target Details")
st.sidebar.info("Input your company's data to benchmark against the market.")
target_name = st.sidebar.text_input("Project Name", "Project Alpha")
target_margin = st.sidebar.number_input("Net Margin (%)", value=14.0, step=0.5)
target_roe = st.sidebar.number_input("ROE (%)", value=20.0, step=0.5)
target_gearing = st.sidebar.number_input("Gearing / Debt-to-Equity (%)", value=60.0, step=5.0, help="Total Debt / Total Equity. BTP average is ~80%.")
target_pe = st.sidebar.number_input("Implied P/E Ratio", value=13.0, step=0.5)

# Append Target to Dataframe
target_row = pd.DataFrame([{
    "Company": target_name, "Price_MAD": 0, "PE_Ratio": target_pe, 
    "Net_Margin_%": target_margin, "ROE_%": target_roe, 
    "Gearing_%": target_gearing, "Type": "Your Target"
}])
df_combined = pd.concat([target_row, df_live], ignore_index=True)

# --- THE UI ---
st.subheader("⚖️ 1. Peer Comparison: Profitability & Returns")
peers = st.multiselect("Select Competitors to Compare:", df_live["Company"].tolist(), default=df_live["Company"].tolist()[:4])

if peers:
    # Filter data for selected peers + the target company
    display_df = df_combined[(df_combined["Company"].isin(peers)) | (df_combined["Company"] == target_name)].copy()
    
    # Custom color mapping: Target is Gold, Peers are Blue
    color_map = {target_name: "#f5b041"}
    for peer in peers: color_map[peer] = "#1f77b4"

    col_bar1, col_bar2 = st.columns(2)
    
    with col_bar1:
        fig_margin = px.bar(display_df, x="Company", y="Net_Margin_%", color="Company", color_discrete_map=color_map, title="Net Margin (%)")
        fig_margin.update_layout(template="plotly_dark", showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_margin, use_container_width=True)
        
    with col_bar2:
        fig_roe = px.bar(display_df, x="Company", y="ROE_%", color="Company", color_discrete_map=color_map, title="Return on Equity - ROE (%)")
        fig_roe.update_layout(template="plotly_dark", showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_roe, use_container_width=True)

st.markdown("---")

# --- PRO ADD-ONS: BTP RISK MATRIX & SPIDER WEB ---
col_matrix, col_radar = st.columns([1.2, 1], gap="large")

with col_matrix:
    st.subheader("⚠️ 2. BTP Risk/Reward Matrix")
    st.markdown("<p style='color:#b3b3b3; font-size:0.9rem;'>In construction, high ROE is often driven by dangerous debt levels. This matrix compares Profitability (ROE) vs Risk (Gearing).</p>", unsafe_allow_html=True)
    
    # Scatter Plot: Risk vs Reward
    fig_scatter = px.scatter(
        df_combined, x="Gearing_%", y="ROE_%", color="Type", text="Company", size_max=60,
        color_discrete_map={"Your Target": "#f5b041", "Market Peer": "#1f77b4"}
    )
    fig_scatter.update_traces(textposition='top center', marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')))
    
    # Add quadrants (Averages)
    avg_gearing = df_live["Gearing_%"].mean()
    avg_roe = df_live["ROE_%"].mean()
    fig_scatter.add_hline(y=avg_roe, line_dash="dash", line_color="gray", annotation_text="Avg ROE")
    fig_scatter.add_vline(x=avg_gearing, line_dash="dash", line_color="gray", annotation_text="Avg Debt")
    
    fig_scatter.update_layout(template="plotly_dark", xaxis_title="Financial Risk (Gearing %)", yaxis_title="Reward (ROE %)", height=450)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_radar:
    st.subheader("🕸️ 3. 360° Sector Profile")
    st.markdown("<p style='color:#b3b3b3; font-size:0.9rem;'>Radar chart comparing your target against the BTP market average.</p>", unsafe_allow_html=True)
    
    categories = ['Net Margin', 'ROE', 'P/E Ratio', 'Financial Health (Inv Gearing)']
    
    # Invert Gearing for the radar chart so "Bigger is Better"
    target_health = max(0, 150 - target_gearing) 
    market_health = max(0, 150 - df_live["Gearing_%"].mean())
    
    target_vals = [target_margin, target_roe, target_pe, target_health]
    market_vals = [df_live["Net_Margin_%"].mean(), df_live["ROE_%"].mean(), df_live["PE_Ratio"].mean(), market_health]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=target_vals, theta=categories, fill='toself', name='Your Target', line_color='#f5b041'))
    fig_radar.add_trace(go.Scatterpolar(r=market_vals, theta=categories, fill='toself', name='Market Average', line_color='#1f77b4'))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(max(target_vals), max(market_vals)) + 5])),
        showlegend=True, template="plotly_dark", height=450, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_radar, use_container_width=True)
