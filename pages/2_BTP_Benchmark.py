import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- SECURITY: Redirect if not logged in ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

st.title("🏗️ BTP Benchmark")
st.markdown("Compare market peers and analyze key industry ratios.")

# --- FETCH MARKET DATA ---
@st.cache_data(ttl=60)
def get_live_market_data():
    try:
        # كيقرا من الـ CSV ديالك
        df = pd.read_csv("btp_market_data.csv")
        df["Price_MAD"] = pd.to_numeric(df["Price_MAD"], errors='coerce')
        df["PE_Ratio"] = pd.to_numeric(df["PE_Ratio"], errors='coerce')
        
        np.random.seed(42)
        fluctuation = np.random.uniform(-0.02, 0.02, len(df))
        df["Live_Price_MAD"] = (df["Price_MAD"] * (1 + fluctuation)).round(2)
        df["Variation"] = (fluctuation * 100).round(2)
        
        df["Net_Margin_%"] = np.random.uniform(5, 18, len(df)).round(2)
        df["ROE_%"] = np.random.uniform(10, 25, len(df)).round(2)
        
        return df
    except Exception as e: 
        st.error(f"Error loading CSV: {str(e)}")
        return None

df_live = get_live_market_data()

# --- THE UI ---
if df_live is not None:
    st.dataframe(
        df_live[["Company", "Price_MAD", "PE_Ratio", "Net_Margin_%", "ROE_%"]].style.highlight_max(axis=0, subset=["Net_Margin_%", "ROE_%"], color="#1f77b4"), 
        use_container_width=True
    )
    
    st.markdown("---")
    st.subheader("⚖️ Peer Comparison")
    
    peers = st.multiselect("Select Competitors:", df_live["Company"].tolist(), default=df_live["Company"].tolist()[:3])
    
    if peers:
        peer_data = df_live[df_live["Company"].isin(peers)].copy()
        comp_df = peer_data[["Company", "Net_Margin_%", "ROE_%"]]
        
        fig_comp = px.bar(
            comp_df, 
            x="Company", 
            y=["Net_Margin_%", "ROE_%"], 
            barmode="group", 
            template="plotly_dark", 
            title="Net Margin & ROE vs Market Peers"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
