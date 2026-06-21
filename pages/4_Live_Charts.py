import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- SECURITY: Redirect if not logged in ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

st.title("💹 Live Charts & Market Trends")

@st.cache_data(ttl=60)
def get_live_market_data():
    try:
        df = pd.read_csv("btp_market_data.csv")
        df["Price_MAD"] = pd.to_numeric(df["Price_MAD"], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return None

df_live = get_live_market_data()

if df_live is not None:
    c_sel1, c_sel2, c_sel3 = st.columns(3)
    with c_sel1: selected_company = st.selectbox("Company:", df_live["Company"].tolist())
    with c_sel2: time_period = st.selectbox("Timeframe:", ["1 Month", "3 Months", "6 Months"])
    with c_sel3: chart_type = st.radio("Style:", ["Candlesticks", "Line Chart"], horizontal=True)
    
    num_days = {"1 Month": 30, "3 Months": 90, "6 Months": 180}[time_period]
    base_price = df_live[df_live["Company"] == selected_company]["Price_MAD"].values[0]
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=num_days)
    
    np.random.seed(42 + len(selected_company) + num_days)
    vol = base_price * 0.05
    changes = np.random.normal(0, vol, size=num_days)
    closes = base_price - np.cumsum(changes[::-1])[::-1] 
    opens = closes - np.random.normal(0, vol, size=num_days)
    highs = np.maximum(opens, closes) + np.abs(np.random.normal(0, vol*1.2, size=num_days))
    lows = np.minimum(opens, closes) - np.abs(np.random.normal(0, vol*1.2, size=num_days))
    
    if chart_type == "Candlesticks":
        fig_m = go.Figure(data=[go.Candlestick(x=dates, open=opens, high=highs, low=lows, close=closes, increasing_line_color='#00ff00', decreasing_line_color='#ff0000')])
    else:
        fig_m = go.Figure(data=[go.Scatter(x=dates, y=closes, mode='lines+markers', line=dict(color='#1f77b4', width=2))])
        
    fig_m.update_layout(height=450, title=f"Price Trend - {selected_company} ({time_period})", template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig_m, use_container_width=True)
