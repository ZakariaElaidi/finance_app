import streamlit as st

# MUST BE THE FIRST LINE
st.set_page_config(page_title="Z.ELAIDI - Financial Analytics", layout="wide", page_icon="📊")

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import io
import json
import base64
from fpdf import FPDF
from supabase import create_client, ClientOptions

# ==========================================
# 1. SUPABASE CONFIGURATION
# ==========================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

try:
    supabase = create_client(
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY,
        options=ClientOptions(postgrest_client_timeout=10)
    )
except Exception as e:
    st.error(f"Database Connection Error: {e}")
    st.stop()

ADMIN_EMAIL = "zakariaelaidi2006@gmail.com"

if "user" not in st.session_state:
    st.session_state.user = None
if "lang" not in st.session_state:
    st.session_state.lang = "English"

# ==========================================
# 2. TRANSLATION DICTIONARY (i18n)
# ==========================================
t = {
    "English": {
        "tab1": "📈 Corporate Analysis", "tab2": "🏗️ BTP Benchmark", "tab3": "💼 M&A Valuation",
        "tab4": "💹 Live Charts", "tab5": "👤 About Creator", "tab6": "🗄️ My History",
        "upload_msg": "Upload your company's financial Excel template.",
        "dl_btn": "📥 Download Template", "logout": "🚪 Terminate Session",
        "mna_title": "💼 M&A & Private Equity Deal Room", "history_title": "🗄️ Database Records",
        "about_title": "👤 Administrator Profile"
    },
    "Français": {
        "tab1": "📈 Analyse Financière", "tab2": "🏗️ Benchmark BTP", "tab3": "💼 Valorisation M&A",
        "tab4": "💹 Graphiques en Direct", "tab5": "👤 À Propos", "tab6": "🗄️ Mon Historique",
        "upload_msg": "Téléchargez votre modèle financier Excel.",
        "dl_btn": "📥 Télécharger le Modèle", "logout": "🚪 Se Déconnecter",
        "mna_title": "💼 Salle des Transactions M&A et Private Equity", "history_title": "🗄️ Enregistrements",
        "about_title": "👤 Profil Administrateur"
    },
    "Español": {
        "tab1": "📈 Análisis Corporativo", "tab2": "🏗️ Benchmark BTP", "tab3": "💼 Valoración M&A",
        "tab4": "💹 Gráficos en Vivo", "tab5": "👤 Sobre el Creador", "tab6": "🗄️ Mi Historial",
        "upload_msg": "Sube tu plantilla financiera en Excel.",
        "dl_btn": "📥 Descargar Plantilla", "logout": "🚪 Cerrar Sesión",
        "mna_title": "💼 Sala de Fusiones y Adquisiciones", "history_title": "🗄️ Registros de Base de Datos",
        "about_title": "👤 Perfil del Administrador"
    },
    "Arabic": {
        "tab1": "📈 التحليل المالي", "tab2": "🏗️ مقارنة قطاع البناء", "tab3": "💼 تقييم الاستحواذ",
        "tab4": "💹 رسوم بيانية حية", "tab5": "👤 عن المطور", "tab6": "🗄️ سجلي",
        "upload_msg": "قم بتحميل قالب الإكسيل المالي الخاص بشركتك.",
        "dl_btn": "📥 تحميل القالب", "logout": "🚪 تسجيل الخروج",
        "mna_title": "💼 غرفة صفقات الدمج والاستحواذ", "history_title": "🗄️ السجلات المحفوظة",
        "about_title": "👤 الملف الشخصي للمسؤول"
    }
}
lang_dict = t[st.session_state.lang]

# ==========================================
# 3. PRO CSS STYLING
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.admin-badge { background-color: #c1272d; color: white; padding: 3px 8px; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; border-radius: 4px; display: inline-block; margin-left: 10px; }
.sidebar-user { background-color: #161a22; padding: 15px; border-radius: 8px; border-left: 3px solid #1f77b4; margin-bottom: 20px; word-wrap: break-word;}
.ma-card { background-color: #161a22; border: 1px solid #333; padding: 15px; border-radius: 8px; margin-top: 15px; }
.ma-card-title { color: #b3b3b3; font-size: 0.9rem; margin-bottom: 5px; }
.ma-card-value { color: white; font-size: 1.5rem; font-weight: bold; margin: 0; }
.btn-pdf { background-color: #c1272d; color: white; padding: 15px 15px; text-align: center; display: block; border-radius: 5px; text-decoration: none; font-weight: bold; margin-top: 15px; transition: 0.3s; }
.btn-pdf:hover { background-color: #a02025; color: white; }
.glossary-box { background-color: #0e1117; padding: 15px; border-left: 3px solid #f5b041; border-radius: 5px; font-size: 0.9rem; color: #d0d3d4; margin-bottom: 15px; }
.report-box { padding: 20px; border-radius: 10px; background-color: #161a22; border-left: 5px solid; margin-top: 20px; }
.metric-box { background-color: #161a22; padding: 15px; border-radius: 8px; border-top: 3px solid #1f77b4; margin-bottom: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. DATABASE, DATA HELPERS & PDF
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
    df_template = pd.DataFrame({
        "Line_Item": ["Revenue", "Net Income", "Current Assets", "Current Liabilities", "Inventory", "Total Assets", "Total Equity", "Total Debt"], 
        "2024": [0]*8, 
        "2025": [0]*8
    })
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer: 
        df_template.to_excel(writer, index=False)
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

# FIXED PDF GENERATOR (Safe Margins and Widths)
def create_detailed_pdf(company_ratios, expert_diagnosis, sector_avg_pe, df_table, sim_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(10, 10, 10) # Prevent Horizontal Space Error
    
    # Header
    pdf.set_fill_color(193, 39, 45)
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_y(12)
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "FINANCIAL & EQUITY RESEARCH REPORT", ln=True, align='C')
    
    # Date
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(45)
    pdf.set_font("Arial", 'I', 11)
    pdf.cell(0, 10, f"Generated automatically on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='R')
    pdf.ln(5)
    
    # Section 1: Variance Table
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, " 1. Financial Statement Variance Data", border=1, ln=True, fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(200, 200, 200)
    # Reduced widths slightly to ensure they fit in 190mm
    pdf.cell(55, 8, "Line Item", border=1, align='C', fill=True)
    pdf.cell(45, 8, "2024", border=1, align='C', fill=True)
    pdf.cell(45, 8, "2025", border=1, align='C', fill=True)
    pdf.cell(45, 8, "YoY Growth (%)", border=1, ln=True, align='C', fill=True)
    
    pdf.set_font("Arial", '', 10)
    for index, row in df_table.iterrows():
        pdf.cell(55, 8, str(index), border=1)
        pdf.cell(45, 8, f"{row.iloc[0]:,.0f}", border=1, align='R')
        pdf.cell(45, 8, f"{row.iloc[1]:,.0f}", border=1, align='R')
        val = row['YoY Growth (%)']
        growth_str = f"{val:.2f}%" if pd.notna(val) else "N/A"
        pdf.cell(45, 8, growth_str, border=1, ln=True, align='R')
    pdf.ln(8)

    # Section 2: Ratios
    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, " 2. Key Performance Ratios", border=1, ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    for key, value in company_ratios.items():
        pdf.cell(80, 8, f"{key}:", border=0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, f"{value}", border=0, ln=True)
        pdf.set_font("Arial", '', 12)
    pdf.ln(8)
    
    # Section 3: Expert Diagnosis
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, " 3. Expert Diagnosis & Vulnerabilities", border=1, ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    for note in expert_diagnosis:
        # Safe multi_cell call
        pdf.multi_cell(190, 8, txt=f"> {note}")
    pdf.ln(8)
    
    # Section 4: Sensitivity & Market
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, " 4. Sensitivity Simulation & Market Benchmark", border=1, ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"- Simulated Future Revenue: {sim_data['rev']:,.2f} MAD", ln=True)
    pdf.cell(0, 8, f"- Simulated Future Net Margin: {sim_data['margin']:.2f}%", ln=True)
    pdf.ln(5)
    pdf.multi_cell(190, 8, txt=f"The company's performance was evaluated against the Casablanca Stock Exchange (CSE) BTP sector. The average sector P/E Ratio currently stands at {sector_avg_pe:.2f}.")
    
    return bytes(pdf.output())

# ==========================================
# 5. AUTHENTICATION MODULE
# ==========================================
def auth_ui():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        st.markdown("<h2 style='text-align: left; color: white; border-top: 4px solid #c1272d; padding-top: 15px;'>SYSTEM ACCESS</h2>", unsafe_allow_html=True)
        choice = st.radio("Action", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
        email = st.text_input("Corporate Email", placeholder="email@domain.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")

        if st.button("Authenticate", use_container_width=True):
            if choice == "Login":
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.rerun()
                except Exception as e: st.error(f"Login Error: {str(e)}")
            else:
                try:
                    supabase.auth.sign_up({"email": email, "password": password})
                    st.success("Account created successfully. Switch to Login.")
                except Exception as e: st.error(f"Sign Up Error: {str(e)}")

# ==========================================
# 6. MAIN APPLICATION
# ==========================================
def main_app():
    is_admin = (st.session_state.user.email.lower() == ADMIN_EMAIL.lower())

    # --- SIDEBAR REDESIGN ---
    with st.sidebar:
        st.markdown("## ⚙️ Control Panel")
        
        # Language Selector
        new_lang = st.selectbox("🌐 Interface Language", ["English", "Français", "Español", "Arabic"], index=["English", "Français", "Español", "Arabic"].index(st.session_state.lang))
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()
            
        st.markdown("---")
        
        # User Profile Box
        admin_tag = '<span class="admin-badge">ADMIN</span>' if is_admin else ''
        st.markdown(f"""
        <div class="sidebar-user">
            <span style="color:#b3b3b3; font-size:12px;">LOGGED IN AS</span><br>
            <b>{st.session_state.user.email}</b> {admin_tag}
        </div>
        """, unsafe_allow_html=True)
        
        # Logout
        if st.button(lang_dict["logout"], use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

    st.markdown("""
    <div style="background: linear-gradient(to right, #0e1117, #1f77b4); padding: 30px; border-radius: 5px; border-left: 5px solid #c1272d; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">Casablanca Stock Exchange</h1>
        <p style='color:#b3b3b3; font-size:1.2rem; margin: 0;'>BTP Sector Equity Research & Financial Analytics Hub</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab6, tab5 = st.tabs([
        lang_dict["tab1"], lang_dict["tab2"], lang_dict["tab3"], 
        lang_dict["tab4"], lang_dict["tab6"], lang_dict["tab5"]
    ])
    
    df_live = get_live_market_data()
    has_data = False
    rev_25 = net_25 = user_net_margin = user_roe = current_ratio = 0

    # --- TAB 1: UPLOAD & ANALYSIS ---
    with tab1:
        c1, c2 = st.columns([3, 1])
        with c1: st.markdown(f"**{lang_dict['upload_msg']}**")
        with c2: st.download_button(lang_dict["dl_btn"], data=generate_template(), file_name="Template.xlsx", use_container_width=True)
        
        uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"], label_visibility="collapsed")
        
        if uploaded_file:
            has_data = True
            try:
                df_finance = pd.read_excel(uploaded_file)
                df_finance.columns = [str(c).strip() for c in df_finance.columns]
                df_finance.set_index(df_finance.columns[0], inplace=True)
                
                col_24 = df_finance.columns[0]
                col_25 = df_finance.columns[1]
                
                df_display = df_finance.copy()
                df_display[col_24] = pd.to_numeric(df_display[col_24], errors='coerce')
                df_display[col_25] = pd.to_numeric(df_display[col_25], errors='coerce')
                df_display['YoY Growth (%)'] = ((df_display[col_25] - df_display[col_24]) / df_display[col_24]) * 100
                
                def color_variance(row):
                    item = str(row.name).lower()
                    val = row['YoY Growth (%)']
                    if pd.isna(val): return [''] * len(row)
                    color = '#d62728' if ('liability' in item or 'debt' in item) and val > 0 else '#2ca02c' if val > 0 else '#d62728'
                    return [f'color: {color}' if col == 'YoY Growth (%)' else '' for col in row.index]

                left_col, right_col = st.columns([1.5, 1], gap="large")
                
                with left_col:
                    st.subheader("📋 Variance Analysis")
                    st.dataframe(df_display.style.apply(color_variance, axis=1).format({'YoY Growth (%)': "{:.2f}%"}), use_container_width=True)

                    rev_24, rev_25 = float(df_finance.loc["Revenue", col_24]), float(df_finance.loc["Revenue", col_25])
                    net_24, net_25 = float(df_finance.loc["Net Income", col_24]), float(df_finance.loc["Net Income", col_25])
                    ca_25 = float(df_finance.loc["Current Assets", col_25])
                    cl_25 = float(df_finance.loc["Current Liabilities", col_25])
                    eq_25 = float(df_finance.loc["Total Equity", col_25])
                    
                    user_net_margin = (net_25 / rev_25) * 100 if rev_25 > 0 else 0
                    user_roe = (net_25 / eq_25) * 100 if eq_25 > 0 else 0
                    current_ratio = ca_25 / cl_25 if cl_25 > 0 else 0

                with right_col:
                    st.subheader("🎛️ Sensitivity (What-If)")
                    sim_rev_exact = st.number_input("Revenue Growth (%)", -30, 30, 0, step=1)
                    sim_cost_exact = st.number_input("Cost Reduction (%)", 0, 30, 0, step=1)
                    
                    sim_rev = rev_25 * (1 + (sim_rev_exact/100))
                    sim_costs = (rev_25 - net_25) * (1 - (sim_cost_exact/100))
                    sim_net = sim_rev - sim_costs
                    sim_margin = (sim_net / sim_rev * 100) if sim_rev > 0 else 0
                    
                    st.markdown(f"""
                    <div class="metric-box">
                        <p style="margin:0; color:#b3b3b3; font-size:14px;">Simulated Revenue (MAD)</p>
                        <h3 style="margin:0; color:#2ca02c;">{sim_rev:,.2f}</h3>
                    </div>
                    <div class="metric-box">
                        <p style="margin:0; color:#b3b3b3; font-size:14px;">Simulated Net Margin</p>
                        <h3 style="margin:0; color:#1f77b4;">{sim_margin:.2f}%</h3>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")
                
                st.subheader("📊 Key Performance Ratios")
                cr1, cr2, cr3 = st.columns(3)
                cr1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=current_ratio, title={'text': "Current Ratio"}, gauge={'axis': {'range': [0, 3]}, 'bar': {'color': "#2ca02c"}})).update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark"), use_container_width=True)
                cr2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=user_net_margin, number={'suffix': "%"}, title={'text': "Net Margin"}, gauge={'axis': {'range': [0, 30]}, 'bar': {'color': "#1f77b4"}})).update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark"), use_container_width=True)
                cr3.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=user_roe, number={'suffix': "%"}, title={'text': "ROE"}, gauge={'axis': {'range': [0, 40]}, 'bar': {'color': "#9467bd"}})).update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark"), use_container_width=True)

                st.markdown("---")

                col_diag, col_chart = st.columns([1, 1], gap="large")
                
                with col_diag:
                    st.subheader("💡 Expert Diagnosis")
                    score_positif = sum([current_ratio >= 1.2, user_net_margin >= 8.0, user_roe >= 12.0])
                    if score_positif >= 2:
                        color, status = "#2ca02c", "Favorable Financial Situation"
                        selected_nbs = ["Excellent liquidity management.", "Strong operational profitability confirmed.", "Optimal value creation for shareholders with attractive ROE."]
                    else:
                        color, status = "#d62728", "Critical Financial Situation"
                        selected_nbs = ["Potential liquidity drain: Monitor short-term solvency.", "Value destruction: Margins are below sector standards.", "High dependency on debt or low operational efficiency."]
                        
                    st.markdown(f"""
                    <div class="report-box" style="border-color: {color};">
                        <h4 style="color: {color}; margin-top: 0;">{status}</h4>
                        <ul>
                            <li style="color: #b3b3b3;"><b>N.B:</b> {selected_nbs[0]}</li>
                            <li style="color: #b3b3b3;"><b>N.B:</b> {selected_nbs[1]}</li>
                            <li style="color: #b3b3b3;"><b>N.B:</b> {selected_nbs[2]}</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                with col_chart:
                    st.subheader("📈 YoY Progression")
                    fig_yoy = go.Figure()
                    fig_yoy.add_trace(go.Bar(x=['2024', '2025'], y=[rev_24, rev_25], name='Revenue', marker_color='#1f77b4'))
                    fig_yoy.add_trace(go.Bar(x=['2024', '2025'], y=[net_24, net_25], name='Net Income', marker_color='#2ca02c'))
                    fig_yoy.update_layout(barmode='group', template="plotly_dark", height=250, margin=dict(l=0, r=0, t=30, b=0))
                    st.plotly_chart(fig_yoy, use_container_width=True)

                st.markdown("---")

                st.subheader("💾 Actions & Reports")
                c_action1, c_action2 = st.columns(2)
                
                with c_action1:
                    if st.button("Save Analysis to My History", use_container_width=True):
                        session_data = {
                            "Revenue": rev_25, "Net Margin": round(user_net_margin, 2), "ROE": round(user_roe, 2),
                            "Current Ratio": round(current_ratio, 2), "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        if save_history(st.session_state.user.id, st.session_state.user.email, session_data):
                            st.success("✅ Saved successfully!")
                        else: st.error("⚠️ Failed to save.")
                        
                with c_action2:
                    try:
                        ratios_dict = {"Revenue": f"{rev_25:,.2f} MAD", "Net Margin": f"{user_net_margin:.2f}%", "ROE": f"{user_roe:.2f}%", "Current Ratio": f"{current_ratio:.2f}"}
                        sector_pe = df_live['PE_Ratio'].mean() if df_live is not None else 15.0
                        pdf_bytes = create_detailed_pdf(ratios_dict, selected_nbs, sector_pe, df_display, {"rev": sim_rev, "margin": sim_margin})
                        b64_pdf = base64.b64encode(pdf_bytes).decode('latin-1')
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="Financial_Report_Z_ELAIDI.pdf" class="btn-pdf">📄 Download Detailed PDF Report</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")

            except Exception as e:
                st.error(f"⚠️ Error processing file. {str(e)}")

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
        st.header(lang_dict["mna_title"])
        
        with st.expander("ℹ️ Glossary & Definitions"):
            st.markdown("""
            <div class="glossary-box">
                <b>WACC (Weighted Average Cost of Capital):</b> The minimum acceptable return a company must earn to satisfy its creditors and investors.<br>
                <b>Terminal Growth %:</b> The constant rate at which a company is expected to grow forever beyond the initial projection period.<br>
                <b>EV (Enterprise Value):</b> A measure of a company's total value, often used as a more comprehensive alternative to equity market capitalization.<br>
                <b>Entry/Exit Multiples:</b> Financial metrics (like EV/EBITDA) used to determine the purchase and selling price of the business.<br>
                <b>IRR (Internal Rate of Return):</b> The annualized expected profitability of the Private Equity investment.
            </div>
            """, unsafe_allow_html=True)

        if not has_data:
            st.info("💡 Upload your Financial Template in Tab 1 to populate data. Using proxy data for now.")
            
        base_rev = rev_25 if has_data else 5000000.0
        base_ebitda = net_25 * 1.3 if has_data else 1200000.0

        col_dcf, col_lbo = st.columns(2, gap="large")
        
        with col_dcf:
            st.subheader("📊 DCF Valuation Engine")
            wacc = st.slider("WACC %", 5.0, 20.0, 10.0, 0.5, help="Weighted Average Cost of Capital") / 100
            tg = st.slider("Terminal Growth %", 0.0, 5.0, 2.0, 0.1, help="Expected constant growth rate forever") / 100
            proj_growth = st.slider("Projected Growth %", -10.0, 30.0, 5.0, 1.0, help="Estimated annual growth rate (5-Years)") / 100
            margin = st.slider("Cash Flow Margin %", 1.0, 30.0, 15.0, 1.0, help="Percentage of revenue converted into FCF") / 100

            cfs = [base_rev * ((1 + proj_growth)**i) * margin for i in range(1, 6)]
            ev = sum([cf / ((1 + wacc)**(i+1)) for i, cf in enumerate(cfs)]) + (((cfs[-1] * (1 + tg)) / (wacc - tg)) / ((1 + wacc)**5) if wacc > tg else 0)
            
            st.markdown(f"""
            <div class="ma-card" style="border-left: 4px solid #1f77b4;">
                <div class="ma-card-title">Implied Enterprise Value (EV)</div>
                <div class="ma-card-value">{ev:,.2f} MAD</div>
            </div>
            """, unsafe_allow_html=True)

        with col_lbo:
            st.subheader("💰 LBO Quick-Modeler")
            c_l1, c_l2 = st.columns(2)
            with c_l1: entry_mult = st.number_input("Entry Multiple (x)", 3.0, 15.0, 6.0, 0.5, help="Purchase price expressed as an EBITDA multiple")
            with c_l2: exit_mult = st.number_input("Exit Multiple (x)", 3.0, 15.0, 6.0, 0.5, help="Selling price expressed as an EBITDA multiple at Year 5")
            debt_pct = st.slider("Debt Funding %", 0.0, 90.0, 60.0, 5.0, help="Percentage of acquisition funded by debt") / 100

            entry_ev = base_ebitda * entry_mult
            debt = entry_ev * debt_pct
            equity = entry_ev - debt
            exit_ev = (base_ebitda * ((1 + proj_growth)**5)) * exit_mult
            exit_equity = exit_ev - max(0, debt - sum(cfs)*0.5)

            moic = exit_equity / equity if equity > 0 else 0
            irr = ((moic**(1/5) - 1) * 100) if moic > 0 else 0
            
            st.markdown(f"""
            <div class="ma-card" style="border-left: 4px solid #9467bd;">
                <div class="ma-card-title">Private Equity Metrics (5-Year Horizon)</div>
                <div class="ma-card-value" style="font-size: 1.2rem;">IRR: {irr:.2f}% &nbsp; | &nbsp; MoIC: {moic:.2f}x</div>
            </div>
            """, unsafe_allow_html=True)

    # --- TAB 4: CHARTS ---
    with tab4:
        if df_live is not None:
            c_sel1, c_sel2, c_sel3 = st.columns(3)
            with c_sel1: selected_company = st.selectbox("Company:", df_live["Company"].tolist())
            with c_sel2: time_period = st.selectbox("Timeframe:", ["1 Month", "3 Months", "6 Months"])
            with c_sel3: chart_type = st.radio("Style:", ["Candlesticks", "Line Chart"], horizontal=True)
            
            num_days = {"1 Month": 30, "3 Months": 90, "6 Months": 180}[time_period]
            base_price = df_live[df_live["Company"] == selected_company]["Live_Price_MAD"].values[0]
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

    # --- TAB 6: MY HISTORY ---
    with tab6:
        st.header(lang_dict["history_title"])
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
        st.header(lang_dict["about_title"])
        col_about1, col_about2 = st.columns([2, 1])
        with col_about1:
            st.markdown("""
            ### **Zakaria Elaidi** | *Financial Analyst & M&A Specialist*
            
            Currently pursuing a Master's degree in Finance (Programme Grande École) at **ENCG El Jadida**, Zakaria specializes in advanced financial analysis, corporate finance, and investment valuation.
            
            With a strategic focus on targeting roles in **M&A, Investment Banking, and Private Equity**, he bridges the gap between traditional equity research and modern data science tools (Python, Pandas, SQL).
            
            **Professional Background:**
            * **Consulting Experience:** Successfully delivered over 150 financial modeling and analysis projects globally as a freelance consultant.
            * **Corporate Exposure:** Completed the rigorous KPMG UK Audit Job Simulation and is actively preparing for an upcoming professional placement at OCP Group.
            * **Core Expertise:** DCF Valuation, LBO Modeling, Market Finance, Marché des Capitaux, and Financial Statement Analysis.
            """)
        with col_about2:
            st.markdown("""
            <div style="background-color: #161a22; padding: 25px; border: 1px solid #333; text-align: center; border-radius: 8px; border-top: 4px solid #c1272d;">
                <h4 style="margin-top:0; color:#fff;">Professional Network</h4>
                <p style="color:#b3b3b3; font-size: 0.9rem;">Open to networking, M&A discussions, and equity research collaborations.</p>
                <a href="https://www.linkedin.com/in/zakaria-elaidi/" target="_blank" style="background-color: #0077b5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin-top: 10px;">Connect on LinkedIn</a>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 7. ROUTER
# ==========================================
if st.session_state.user is None:
    auth_ui()
else:
    main_app()
