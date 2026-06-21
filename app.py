import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
from datetime import datetime
import io
import base64
import json
from fpdf import FPDF
from supabase import create_client

# ==========================================
# 1. SUPABASE CONFIGURATION
# ==========================================
SUPABASE_URL = "https://jultknrcpxenpefpxeqh.supabase.co"
SUPABASE_KEY = "sb_publishable_uZMzGu6xCTr5DRFCJHM08g_DFHNC4Hv"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. PAGE CONFIG & SESSION STATE
# ==========================================
st.set_page_config(page_title="Z.ELAIDI - Financial Analytics Hub", layout="wide", page_icon="📊")

if "lang" not in st.session_state:
    st.session_state.lang = "English"
if "user" not in st.session_state:
    st.session_state.user = None

# --- TRANSLATION DICTIONARY ---
t = {
    "English": {
        "maintitle": "Financial Analytics & Equity Research Hub",
        "tab1": "📈 Corporate Financial Analysis",
        "tab2": "🏗️ BTP Sector Benchmark",
        "tab3": "💼 M&A & Valuation",
        "tab4": "💹 Live Charts",
        "tab5": "👤 About Creator",
        "tab6": "🗄️ My History",
        "upload_text": "**Upload your company's financial Excel template to unlock the dashboard.**",
        "dl_template": "📥 Download Required Template",
        "dl_pdf": "📄 Download Complete PDF Report",
        "lang_sel": "Select Language:"
    },
    "Français": {
        "maintitle": "Hub d'Analyse Financière et de Recherche",
        "tab1": "📈 Analyse Financière",
        "tab2": "🏗️ Benchmark BTP",
        "tab3": "💼 M&A et Valorisation",
        "tab4": "💹 Graphiques",
        "tab5": "👤 À propos",
        "tab6": "🗄️ Mon Historique",
        "upload_text": "**Téléchargez votre modèle Excel pour débloquer le tableau de bord.**",
        "dl_template": "📥 Télécharger le modèle",
        "dl_pdf": "📄 Télécharger le Rapport PDF",
        "lang_sel": "Sélectionner la Langue :"
    },
    "Arabic": {
        "maintitle": "منصة التحليل المالي وأبحاث الأسهم",
        "tab1": "📈 التحليل المالي",
        "tab2": "🏗️ مقارنة قطاع البناء",
        "tab3": "💼 التقييم والاستحواذ",
        "tab4": "💹 رسوم بيانية",
        "tab5": "👤 عن المطور",
        "tab6": "🗄️ سجل أعمالي",
        "upload_text": "**قم بتحميل قالب الإكسيل المالي لفتح لوحة التحليل.**",
        "dl_template": "📥 تحميل القالب",
        "dl_pdf": "📄 تحميل تقرير PDF",
        "lang_sel": "اختر لغة:"
    }
}

lang_dict = t[st.session_state.lang]

# ==========================================
# 3. PREMIUM CSS
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
.full-width-banner { position: relative; width: 100%; height: 250px; background-image: url('https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=2500&q=80'); background-size: cover; background-position: center; margin-bottom: 2rem; border-radius: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.6); overflow: hidden; }
.banner-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(to right, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 100%); }
.banner-title-container { position: absolute; top: 50%; left: 5%; transform: translateY(-50%); color: white; z-index: 2; }
.banner-title-container h1 { font-size: 2.8rem; font-weight: 700; margin-bottom: 0px; }
.metric-card { background-color: #1e1e1e; padding: 15px; border-radius: 8px; border-top: 3px solid #1f77b4; margin-bottom: 15px; }
.auth-box { max-width: 400px; margin: 0 auto; padding: 30px; background-color: #1e1e1e; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border-top: 4px solid #c1272d; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. DATABASE & DATA HELPERS
# ==========================================
def save_history(user_id, email, data_dict):
    try:
        supabase.table("users_history").insert({
            "user_id": user_id,
            "email": email,
            "work_data": json.dumps(data_dict)
        }).execute()
        return True
    except Exception as e:
        return False

def get_history(user_id):
    try:
        res = supabase.table("users_history").select("created_at, work_data").eq("user_id", user_id).order("created_at", desc=True).execute()
        return res.data
    except:
        return []

def generate_template():
    df_template = pd.DataFrame({"Line_Item": ["Revenue", "Net Income", "Current Assets", "Current Liabilities", "Inventory", "Total Assets", "Total Equity", "Total Debt"], "2024": [0]*8, "2025": [0]*8})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer: df_template.to_excel(writer, index=False)
    return output.getvalue()

@st.cache_data(ttl=60)
def get_live_market_data():
    try:
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
    except: return None

# ==========================================
# 5. AUTHENTICATION MODULE
# ==========================================
def auth_ui():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🔐 Secure Access</h2>", unsafe_allow_html=True)
    
    choice = st.selectbox("Action:", ["Login", "Sign Up"], label_visibility="collapsed")
    email = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    if st.button("Submit", use_container_width=True):
        if choice == "Login":
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.rerun()
            except Exception as e:
                st.error("⚠️ Invalid email or password.")
        else:
            try:
                supabase.auth.sign_up({"email": email, "password": password})
                st.success("✅ Account created! Please check your email to verify.")
            except Exception as e:
                st.error(f"⚠️ Error creating account.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. MAIN APPLICATION
# ==========================================
def main_app():
    st.markdown("""
    <div class="full-width-banner">
        <div class="banner-overlay"></div>
        <div class="banner-title-container">
            <h1>Casablanca Stock Exchange</h1>
            <p style='color:#b3b3b3; font-size:1.2rem;'>BTP Sector Equity Research & Financial Analytics Hub</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Profile & Logout
    with st.sidebar:
        st.markdown(f"### 👤 Profile\n**{st.session_state.user.email}**")
        if st.button("🚪 Logout", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()
        st.markdown("---")
        st.markdown(f"<p style='text-align: center; color: #b3b3b3;'>🌐 {lang_dict['lang_sel']}</p>", unsafe_allow_html=True)
        sel_lang = st.radio("Lang", ["English", "Français", "Arabic"], index=["English", "Français", "Arabic"].index(st.session_state.lang), label_visibility="collapsed")
        if sel_lang != st.session_state.lang:
            st.session_state.lang = sel_lang
            st.rerun()

    # TABS
    tab1, tab2, tab3, tab4, tab6, tab5 = st.tabs([lang_dict["tab1"], lang_dict["tab2"], lang_dict["tab3"], lang_dict["tab4"], lang_dict["tab6"], lang_dict["tab5"]])
    df_live = get_live_market_data()
    
    # Global vars for cross-tab logic
    has_data = False
    user_net_margin = 0
    user_roe = 0

    # --- TAB 1: UPLOAD & ANALYSIS ---
    with tab1:
        c1, c2 = st.columns([3, 1])
        with c1: st.markdown(lang_dict["upload_text"])
        with c2: st.download_button(lang_dict["dl_template"], data=generate_template(), file_name="Template.xlsx", use_container_width=True)
        
        uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])
        
        if uploaded_file:
            has_data = True
            try:
                df_finance = pd.read_excel(uploaded_file)
                df_finance.set_index(df_finance.columns[0], inplace=True)
                col_2024, col_2025 = df_finance.columns[0], df_finance.columns[1]
                
                rev_25 = float(df_finance.loc["Revenue", col_2025])
                net_25 = float(df_finance.loc["Net Income", col_2025])
                ca_25 = float(df_finance.loc["Current Assets", col_2025])
                cl_25 = float(df_finance.loc["Current Liabilities", col_2025])
                eq_25 = float(df_finance.loc["Total Equity", col_2025])
                
                user_net_margin = (net_25 / rev_25) * 100 if rev_25 > 0 else 0
                user_roe = (net_25 / eq_25) * 100 if eq_25 > 0 else 0
                current_ratio = ca_25 / cl_25 if cl_25 > 0 else 0

                left_col, right_col = st.columns([1.5, 1], gap="large")
                
                with left_col:
                    st.subheader("📋 Key Performance Ratios")
                    cr1, cr2, cr3 = st.columns(3)
                    fig1 = go.Figure(go.Indicator(mode="gauge+number", value=current_ratio, title={'text': "Current Ratio"}, gauge={'axis': {'range': [0, 3]}, 'bar': {'color': "#2ca02c"}}))
                    fig1.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
                    cr1.plotly_chart(fig1, use_container_width=True)
                    
                    fig2 = go.Figure(go.Indicator(mode="gauge+number", value=user_net_margin, number={'suffix': "%"}, title={'text': "Net Margin"}, gauge={'axis': {'range': [0, 30]}, 'bar': {'color': "#1f77b4"}}))
                    fig2.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
                    cr2.plotly_chart(fig2, use_container_width=True)

                    fig3 = go.Figure(go.Indicator(mode="gauge+number", value=user_roe, number={'suffix': "%"}, title={'text': "ROE"}, gauge={'axis': {'range': [0, 40]}, 'bar': {'color': "#9467bd"}}))
                    fig3.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
                    cr3.plotly_chart(fig3, use_container_width=True)

                with right_col:
                    st.subheader("💾 Save Session to Database")
                    st.write("Save these metrics to your profile history.")
                    if st.button("Save Analysis to My History", use_container_width=True):
                        session_data = {
                            "Revenue": rev_25,
                            "Net Margin": round(user_net_margin, 2),
                            "ROE": round(user_roe, 2),
                            "Current Ratio": round(current_ratio, 2),
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        if save_history(st.session_state.user.id, st.session_state.user.email, session_data):
                            st.success("✅ Saved successfully! Check 'My History' tab.")
                        else:
                            st.error("⚠️ Failed to save. Check database connection.")
            except Exception as e:
                st.error("⚠️ Error processing file. Make sure you use the exact template format.")

    # --- TAB 2: SECTOR BENCHMARK ---
    with tab2:
        if df_live is not None:
            st.dataframe(df_live[["Company", "Live_Price_MAD", "Variation", "PE_Ratio", "Net_Margin_%", "ROE_%"]].style.highlight_max(axis=0, subset=["Net_Margin_%", "ROE_%"], color="#1f77b4"), use_container_width=True)
            
            if has_data:
                st.markdown("---")
                st.subheader("⚖️ Peer Comparison (Your Company vs Market)")
                peers = st.multiselect("Select Competitors:", df_live["Company"].tolist(), default=df_live["Company"].tolist()[:2])
                if peers:
                    peer_data = df_live[df_live["Company"].isin(peers)]
                    comp_df = pd.DataFrame({"Entity": ["Your Company"] + peer_data["Company"].tolist(), "Net Margin (%)": [user_net_margin] + peer_data["Net_Margin_%"].tolist(), "ROE (%)": [user_roe] + peer_data["ROE_%"].tolist()})
                    fig_comp = px.bar(comp_df, x="Entity", y=["Net Margin (%)", "ROE (%)"], barmode="group", template="plotly_dark")
                    st.plotly_chart(fig_comp, use_container_width=True)

    # --- TAB 3: M&A DEAL ROOM ---
    with tab3:
        st.header("💼 M&A & Private Equity Deal Room")
        if not has_data: st.info("💡 Upload your Financial Template in Tab 1 to populate these models automatically.")
        
        base_rev = rev_25 if has_data else 5000000.0
        base_ebitda = net_25 * 1.3 if has_data else 1200000.0

        col_dcf, col_lbo = st.columns(2, gap="large")
        with col_dcf:
            st.subheader("📊 DCF Valuation Engine")
            wacc = st.slider("WACC %", 5.0, 20.0, 10.0, 0.5) / 100
            tg = st.slider("Terminal Growth %", 0.0, 5.0, 2.0, 0.1) / 100
            proj_growth = st.slider("Projected Growth %", -10.0, 30.0, 5.0, 1.0) / 100
            margin = st.slider("Cash Flow Margin %", 1.0, 30.0, 15.0, 1.0) / 100

            cfs = [base_rev * ((1 + proj_growth)**i) * margin for i in range(1, 6)]
            ev = sum([cf / ((1 + wacc)**(i+1)) for i, cf in enumerate(cfs)]) + (((cfs[-1] * (1 + tg)) / (wacc - tg)) / ((1 + wacc)**5) if wacc > tg else 0)
            
            st.markdown(f'<div class="metric-card"><p style="margin:0; color:#b3b3b3;">Implied Enterprise Value (EV)</p><h2 style="margin:0; color:#00ff00;">{ev:,.2f} MAD</h2></div>', unsafe_allow_html=True)

        with col_lbo:
            st.subheader("💰 LBO Quick-Modeler")
            c_l1, c_l2 = st.columns(2)
            with c_l1: entry_mult = st.number_input("Entry Multiple", 3.0, 15.0, 6.0, 0.5)
            with c_l2: exit_mult = st.number_input("Exit Multiple", 3.0, 15.0, 6.0, 0.5)
            debt_pct = st.slider("Debt Funding %", 0.0, 90.0, 60.0, 5.0) / 100

            entry_ev = base_ebitda * entry_mult
            debt = entry_ev * debt_pct
            equity = entry_ev - debt
            exit_ev = (base_ebitda * ((1 + proj_growth)**5)) * exit_mult
            exit_equity = exit_ev - max(0, debt - sum(cfs)*0.5)

            moic = exit_equity / equity if equity > 0 else 0
            irr = ((moic**(1/5) - 1) * 100) if moic > 0 else 0
            
            st.markdown(f'<div class="metric-card" style="border-top-color:#9467bd;"><p style="margin:0; color:#b3b3b3;">Private Equity IRR (5-Year)</p><h2 style="margin:0; color:{"#00ff00" if irr>=20 else "#ff0000"};">{irr:.2f}%</h2><p style="margin:0; color:#b3b3b3;">MoIC: <b>{moic:.2f}x</b></p></div>', unsafe_allow_html=True)

    # --- TAB 4: CHARTS ---
    with tab4:
        if df_live is not None:
            sel_co = st.selectbox("Select Company:", df_live["Company"].tolist())
            base_price = df_live[df_live["Company"] == sel_co]["Live_Price_MAD"].values[0]
            dates = pd.date_range(end=pd.Timestamp.today(), periods=90)
            np.random.seed(42)
            closes = base_price - np.cumsum(np.random.normal(0, base_price*0.05, size=90)[::-1])[::-1]
            fig_m = go.Figure(data=[go.Scatter(x=dates, y=closes, mode='lines', line=dict(color='#1f77b4', width=2))])
            fig_m.update_layout(height=400, title=f"90-Day Trend - {sel_co}", template="plotly_dark")
            st.plotly_chart(fig_m, use_container_width=True)

    # --- TAB 6: MY HISTORY ---
    with tab6:
        st.header("🗄️ My Saved Analyses")
        st.write("Review past financial uploads and metrics saved to your account.")
        history_data = get_history(st.session_state.user.id)
        
        if len(history_data) == 0:
            st.info("No saved history found. Go to Tab 1, upload an Excel file, and click 'Save Analysis'.")
        else:
            for item in history_data:
                date_str = item['created_at'][:10]
                data = json.loads(item['work_data'])
                with st.expander(f"📊 Analysis Saved on: {date_str} (Saved at {data.get('Date', 'N/A')})"):
                    st.write(f"**Revenue:** {data.get('Revenue', 0):,.2f} MAD")
                    st.write(f"**Net Margin:** {data.get('Net Margin', 0)}%")
                    st.write(f"**ROE:** {data.get('ROE', 0)}%")
                    st.write(f"**Current Ratio:** {data.get('Current Ratio', 0)}")

    # --- TAB 5: ABOUT ---
    with tab5:
        st.header("👤 About the Creator")
        c_a1, c_a2 = st.columns([2, 1])
        with c_a1:
            st.markdown("### **Zakaria Elaidi** | *Financial Analyst*")
            st.markdown("Zakaria is a dedicated financial analyst specializing in Finance at **ENCG El Jadida**.")
            st.info("💡 **Core Expertise:** Equity Research, Corporate Finance, Data Automation.")
        with c_a2:
            st.markdown('<div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; text-align: center; border-top: 4px solid #c1272d;"><a href="https://www.linkedin.com/in/zakaria-elaidi/" target="_blank" style="background-color: #0077b5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Connect on LinkedIn</a></div>', unsafe_allow_html=True)

# ==========================================
# 7. ROUTER
# ==========================================
if st.session_state.user is None:
    auth_ui()
else:
    main_app()
