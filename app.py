import streamlit as st

st.set_page_config(
    page_title="Z.ELAIDI - Financial Analytics",
    layout="wide",
    page_icon="📊"
)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import io
import json
import base64
from fpdf import FPDF


# ==========================================
# SUPABASE CONFIGURATION
# ==========================================
from supabase import create_client
import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

st.write("URL:", SUPABASE_URL)

try:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )
    st.success("Supabase client created")
except Exception as e:
    st.error(f"Client Error: {e}")
    st.stop()
ADMIN_EMAIL = "zakariaelaidi2006@gmail.com"

if "user" not in st.session_state:
    st.session_state.user = None
# ==========================================
# 2. SAFE CSS
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.admin-badge { background-color: #c1272d; color: white; padding: 5px 10px; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; display: inline-block; margin-bottom: 10px; }
.ma-card { background-color: #161a22; border: 1px solid #333; padding: 15px; border-radius: 8px; margin-top: 15px; }
.ma-card-title { color: #b3b3b3; font-size: 0.9rem; margin-bottom: 5px; }
.ma-card-value { color: white; font-size: 1.5rem; font-weight: bold; margin: 0; }
.btn-pdf { background-color: #c1272d; color: white; padding: 10px 15px; text-align: center; display: block; border-radius: 5px; text-decoration: none; font-weight: bold; margin-top: 15px; }
.btn-pdf:hover { background-color: #a02025; color: white; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATABASE, DATA HELPERS & PDF
# ==========================================
def save_history(user_id, email, data_dict):
    try:
        supabase.table("users_history").insert({"user_id": user_id, "email": email, "work_data": json.dumps(data_dict)}).execute()
        return True
    except: return False

def get_history(user_id):
    try:
        res = supabase.table("users_history").select("created_at, work_data").eq("user_id", user_id).order("created_at", desc=True).execute()
        return res.data
    except: return []

def generate_template():
    df_template = pd.DataFrame({"Line_Item": ["Revenue", "Net Income", "Current Assets", "Current Liabilities", "Total Equity", "Total Debt"], "2024": [0]*6, "2025": [0]*6})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer: df_template.to_excel(writer, index=False)
    return output.getvalue()

@st.cache_data(ttl=60)
def get_live_market_data():
    try:
        df = pd.DataFrame({
            "Company": ["TGCC", "LafargeHolcim", "Sonasid", "Jet Contractors", "Colorado"],
            "Price_MAD": [250.0, 1800.0, 750.0, 320.0, 50.0],
            "PE_Ratio": [15.2, 18.5, 12.1, 14.0, 10.5]
        })
        np.random.seed(42)
        fluctuation = np.random.uniform(-0.02, 0.02, len(df))
        df["Live_Price_MAD"] = (df["Price_MAD"] * (1 + fluctuation)).round(2)
        df["Variation"] = (fluctuation * 100).round(2)
        df["Net_Margin_%"] = np.random.uniform(5, 18, len(df)).round(2)
        df["ROE_%"] = np.random.uniform(10, 25, len(df)).round(2)
        return df
    except: return None

def create_pdf(metrics_dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(193, 39, 45)
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_y(12)
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "FINANCIAL ANALYTICS REPORT", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(45)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='R')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, " Key Performance Metrics", border=1, ln=True, fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 12)
    for key, value in metrics_dict.items():
        pdf.cell(80, 10, f"{key}:", border=0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"{value}", border=0, ln=True)
        pdf.set_font("Arial", '', 12)
    
    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "Generated via Z.ELAIDI Financial Hub", align='C')
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 4. AUTHENTICATION MODULE
# ==========================================
def auth_ui():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        st.markdown("<h2 style='text-align: left; color: white; border-top: 4px solid #c1272d; padding-top: 15px;'>SYSTEM ACCESS</h2>", unsafe_allow_html=True)

        choice = st.radio(
            "Action",
            ["Login", "Sign Up"],
            horizontal=True,
            label_visibility="collapsed"
        )

        email = st.text_input(
            "Corporate Email",
            placeholder="email@domain.com"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••"
        )

        if st.button("Authenticate", use_container_width=True):
            if choice == "Login":
                try:
                    res = supabase.auth.sign_in_with_password(
                        {
                            "email": email,
                            "password": password
                        }
                    )
                    st.session_state.user = res.user
                    st.rerun()

                except Exception as e:
                    st.error(f"Login Error: {str(e)}")

            else:
                try:
                    supabase.auth.sign_up(
                        {
                            "email": email,
                            "password": password
                        }
                    )
                    st.success(
                        "Account created successfully. Switch to Login."
                    )

                except Exception as e:
                    st.error(f"Sign Up Error: {str(e)}")

# ==========================================
# 5. MAIN APPLICATION
# ==========================================
def main_app():
    is_admin = (st.session_state.user.email.lower() == ADMIN_EMAIL.lower())

    st.markdown("""
    <div style="background: linear-gradient(to right, #0e1117, #1f77b4); padding: 30px; border-radius: 5px; border-left: 5px solid #c1272d; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">Casablanca Stock Exchange</h1>
        <p style='color:#b3b3b3; font-size:1.2rem; margin: 0;'>BTP Sector Equity Research & Financial Analytics Hub</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if is_admin:
            st.markdown('<div class="admin-badge">SYSTEM ADMIN</div>', unsafe_allow_html=True)
            st.markdown(f"**{st.session_state.user.email}**")
            st.success("Full Analytics Access Granted")
        else:
            st.markdown("### 👤 USER SESSION")
            st.markdown(f"**{st.session_state.user.email}**")
            
        st.markdown("---")
        if st.button("🚪 Terminate Session", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

    tab1, tab2, tab3, tab4, tab6, tab5 = st.tabs([
        "📈 Corporate Analysis", "🏗️ BTP Benchmark", "💼 M&A Valuation", 
        "💹 Live Charts", "🗄️ My History", "👤 About Creator"
    ])
    df_live = get_live_market_data()
    
    has_data = False
    rev_25 = net_25 = user_net_margin = user_roe = current_ratio = 0

    # --- TAB 1: UPLOAD & ANALYSIS ---
    with tab1:
        c1, c2 = st.columns([3, 1])
        with c1: st.markdown("**Upload your company's financial Excel template.**")
        with c2: st.download_button("📥 Download Template", data=generate_template(), file_name="Template.xlsx", use_container_width=True)
        
        uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"], label_visibility="collapsed")
        
        if uploaded_file:
            has_data = True
            try:
                df_finance = pd.read_excel(uploaded_file)
                df_finance.set_index(df_finance.columns[0], inplace=True)
                col_25 = df_finance.columns[1]
                
                rev_25 = float(df_finance.loc["Revenue", col_25])
                net_25 = float(df_finance.loc["Net Income", col_25])
                ca_25 = float(df_finance.loc["Current Assets", col_25])
                cl_25 = float(df_finance.loc["Current Liabilities", col_25])
                eq_25 = float(df_finance.loc["Total Equity", col_25])
                
                user_net_margin = (net_25 / rev_25) * 100 if rev_25 > 0 else 0
                user_roe = (net_25 / eq_25) * 100 if eq_25 > 0 else 0
                current_ratio = ca_25 / cl_25 if cl_25 > 0 else 0

                left_col, right_col = st.columns([1.5, 1], gap="large")
                
                with left_col:
                    st.subheader("📋 Key Performance Ratios")
                    cr1, cr2, cr3 = st.columns(3)
                    cr1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=current_ratio, title={'text': "Current Ratio"}, gauge={'axis': {'range': [0, 3]}, 'bar': {'color': "#2ca02c"}})).update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark"), use_container_width=True)
                    cr2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=user_net_margin, number={'suffix': "%"}, title={'text': "Net Margin"}, gauge={'axis': {'range': [0, 30]}, 'bar': {'color': "#1f77b4"}})).update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark"), use_container_width=True)
                    cr3.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=user_roe, number={'suffix': "%"}, title={'text': "ROE"}, gauge={'axis': {'range': [0, 40]}, 'bar': {'color': "#9467bd"}})).update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark"), use_container_width=True)

                with right_col:
                    st.subheader("💾 Database & Reports")
                    if st.button("Save Analysis to My History", use_container_width=True):
                        session_data = {
                            "Revenue": rev_25, "Net Margin": round(user_net_margin, 2), "ROE": round(user_roe, 2),
                            "Current Ratio": round(current_ratio, 2), "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        if save_history(st.session_state.user.id, st.session_state.user.email, session_data):
                            st.success("✅ Saved successfully!")
                        else: st.error("⚠️ Failed to save.")
                    
                    # PDF Generation Button
                    try:
                        metrics = {
                            "Revenue (MAD)": f"{rev_25:,.2f}",
                            "Net Margin (%)": f"{user_net_margin:.2f}%",
                            "ROE (%)": f"{user_roe:.2f}%",
                            "Current Ratio": f"{current_ratio:.2f}"
                        }
                        pdf_bytes = create_pdf(metrics)
                        b64_pdf = base64.b64encode(pdf_bytes).decode('latin-1')
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="Financial_Report_Z_ELAIDI.pdf" class="btn-pdf">📄 Download PDF Report</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    except Exception as e:
                        st.error("Error generating PDF. Please check if fpdf is installed.")
            except Exception as e:
                st.error("⚠️ Error processing file. Ensure strict template format.")

    # --- TAB 2: SECTOR BENCHMARK ---
    with tab2:
        if df_live is not None:
            st.dataframe(df_live[["Company", "Live_Price_MAD", "Variation", "PE_Ratio", "Net_Margin_%", "ROE_%"]].style.highlight_max(axis=0, subset=["Net_Margin_%", "ROE_%"], color="#1f77b4"), use_container_width=True)
            if has_data:
                st.markdown("---")
                peers = st.multiselect("Select Competitors:", df_live["Company"].tolist(), default=df_live["Company"].tolist()[:2])
                if peers:
                    peer_data = df_live[df_live["Company"].isin(peers)]
                    comp_df = pd.DataFrame({"Entity": ["Your Company"] + peer_data["Company"].tolist(), "Net Margin (%)": [user_net_margin] + peer_data["Net_Margin_%"].tolist(), "ROE (%)": [user_roe] + peer_data["ROE_%"].tolist()})
                    st.plotly_chart(px.bar(comp_df, x="Entity", y=["Net Margin (%)", "ROE (%)"], barmode="group", template="plotly_dark"), use_container_width=True)

    # --- TAB 3: M&A DEAL ROOM ---
    with tab3:
        st.header("💼 M&A & Private Equity Deal Room")
        if not has_data:
            st.info("💡 Upload your Financial Template in Tab 1 to populate data. Using proxy data for now.")
            
        base_rev = rev_25 if has_data else 5000000.0
        base_ebitda = net_25 * 1.3 if has_data else 1200000.0

        col_dcf, col_lbo = st.columns(2, gap="large")
        
        with col_dcf:
            st.subheader("📊 DCF Valuation Engine")
            # Added helpful tooltips (i) to all inputs
            wacc = st.slider("WACC %", 5.0, 20.0, 10.0, 0.5, help="Weighted Average Cost of Capital: The minimum average return expected by investors.") / 100
            tg = st.slider("Terminal Growth %", 0.0, 5.0, 2.0, 0.1, help="The constant rate at which the company is expected to grow forever after the projection period.") / 100
            proj_growth = st.slider("Projected Growth %", -10.0, 30.0, 5.0, 1.0, help="Estimated annual growth rate for the 5-year projection period.") / 100
            margin = st.slider("Cash Flow Margin %", 1.0, 30.0, 15.0, 1.0, help="The percentage of revenue converted into Free Cash Flow.") / 100

            cfs = [base_rev * ((1 + proj_growth)**i) * margin for i in range(1, 6)]
            ev = sum([cf / ((1 + wacc)**(i+1)) for i, cf in enumerate(cfs)]) + (((cfs[-1] * (1 + tg)) / (wacc - tg)) / ((1 + wacc)**5) if wacc > tg else 0)
            
            # Professional Card instead of st.success
            st.markdown(f"""
            <div class="ma-card" style="border-left: 4px solid #1f77b4;">
                <div class="ma-card-title">Implied Enterprise Value (EV)</div>
                <div class="ma-card-value">{ev:,.2f} MAD</div>
            </div>
            """, unsafe_allow_html=True)

        with col_lbo:
            st.subheader("💰 LBO Quick-Modeler")
            c_l1, c_l2 = st.columns(2)
            with c_l1: entry_mult = st.number_input("Entry Multiple (x)", 3.0, 15.0, 6.0, 0.5, help="Purchase price expressed as a multiple of EBITDA.")
            with c_l2: exit_mult = st.number_input("Exit Multiple (x)", 3.0, 15.0, 6.0, 0.5, help="Expected selling price expressed as a multiple of EBITDA at year 5.")
            debt_pct = st.slider("Debt Funding %", 0.0, 90.0, 60.0, 5.0, help="Percentage of the acquisition funded by debt.") / 100

            entry_ev = base_ebitda * entry_mult
            debt = entry_ev * debt_pct
            equity = entry_ev - debt
            exit_ev = (base_ebitda * ((1 + proj_growth)**5)) * exit_mult
            exit_equity = exit_ev - max(0, debt - sum(cfs)*0.5)

            moic = exit_equity / equity if equity > 0 else 0
            irr = ((moic**(1/5) - 1) * 100) if moic > 0 else 0
            
            # Professional Card instead of st.info
            st.markdown(f"""
            <div class="ma-card" style="border-left: 4px solid #9467bd;">
                <div class="ma-card-title">Private Equity Metrics (5-Year Horizon)</div>
                <div class="ma-card-value" style="font-size: 1.2rem;">IRR: {irr:.2f}% &nbsp; | &nbsp; MoIC: {moic:.2f}x</div>
            </div>
            """, unsafe_allow_html=True)

    # --- TAB 4: CHARTS ---
    with tab4:
        if df_live is not None:
            sel_co = st.selectbox("Select Company:", df_live["Company"].tolist())
            base_price = df_live[df_live["Company"] == sel_co]["Live_Price_MAD"].values[0]
            dates = pd.date_range(end=pd.Timestamp.today(), periods=90)
            np.random.seed(42)
            closes = base_price - np.cumsum(np.random.normal(0, base_price*0.05, size=90)[::-1])[::-1]
            st.plotly_chart(go.Figure(data=[go.Scatter(x=dates, y=closes, mode='lines', line=dict(color='#1f77b4', width=2))]).update_layout(height=400, title=f"90-Day Trend - {sel_co}", template="plotly_dark"), use_container_width=True)

    # --- TAB 6: MY HISTORY ---
    with tab6:
        st.header("🗄️ Database Records")
        hist = get_history(st.session_state.user.id)
        if len(hist) == 0:
            st.info("No records found in database.")
        else:
            for item in hist:
                date_str = item['created_at'][:10]
                data = json.loads(item['work_data'])
                with st.expander(f"📊 Session: {date_str} - {data.get('Date', 'N/A')}"):
                    st.write(f"**Revenue:** {data.get('Revenue', 0):,.2f} MAD")
                    st.write(f"**Net Margin:** {data.get('Net Margin', 0)}%")
                    st.write(f"**ROE:** {data.get('ROE', 0)}%")

    # --- TAB 5: ABOUT ---
    with tab5:
        st.header("👤 Administrator Profile")
        c_a1, c_a2 = st.columns([2, 1])
        with c_a1:
            st.markdown("### **Zakaria Elaidi** | *Lead Financial Analyst*")
            st.markdown("Administrator of the BTP Financial Engine. ENCG El Jadida.")
        with c_a2:
            st.markdown("""
            <div style="background-color: #161a22; padding: 20px; border: 1px solid #333; text-align: center; border-radius: 5px;">
                <a href="https://www.linkedin.com/in/zakaria-elaidi/" target="_blank" style="color: #1f77b4; text-decoration: none; font-weight: bold;">[ Connect on LinkedIn ]</a>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 7. ROUTER
# ==========================================
if st.session_state.user is None:
    auth_ui()
else:
    main_app()
