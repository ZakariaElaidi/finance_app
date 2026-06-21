import streamlit as st

# --- SECURITY: Redirect if not logged in ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

st.title("👤 About Creator")
st.markdown("<br>", unsafe_allow_html=True)

col_text, col_network = st.columns([2, 1], gap="large")

with col_text:
    st.markdown("### Zakaria Elaidi | *Financial Analyst & M&A Specialist*")
    st.write("Currently pursuing a Master's degree in Finance (Programme Grande École) at **ENCG El Jadida**, Zakaria specializes in advanced financial analysis, corporate finance, and investment valuation.")
    st.write("With a strategic focus on targeting roles in **M&A, Investment Banking, and Private Equity**, he bridges the gap between traditional equity research and modern data science tools (Python, Pandas, SQL).")
    
    st.markdown("#### Professional Background")
    st.markdown("- **Consulting Experience:** Successfully delivered over 150 financial modeling and analysis projects globally as a freelance consultant.")
    st.markdown("- **Corporate Exposure:** Completed the rigorous KPMG UK Audit Job Simulation and actively preparing for a professional placement at OCP Group.")
    st.markdown("- **Core Expertise:** DCF Valuation, LBO Modeling, Market Finance, Marché des Capitaux, and Financial Statement Analysis.")

with col_network:
    st.markdown("""
    <div style="background-color: #0e1117; padding: 25px; border-radius: 8px; border-top: 4px solid #c1272d; text-align: center; height: 100%;">
        <h3 style="margin-top:0; color:#fff;">Professional Network</h3>
        <p style="color:#b3b3b3; font-size: 0.95rem; margin-bottom: 20px;">Open to networking, M&A discussions, and equity research collaborations.</p>
        <br>
        <a href="https://www.linkedin.com/in/zakaria-elaidi/" target="_blank" style="background-color: #0077b5; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: block;">Connect on LinkedIn</a>
    </div>
    """, unsafe_allow_html=True)
