import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
from datetime import datetime, timedelta
import random
import io
import base64
from fpdf import FPDF

# 1. Page Configuration & Session State
st.set_page_config(page_title="Z.ELAIDI - Financial Analytics Hub", layout="wide", page_icon="📊")

if "lang" not in st.session_state:
    st.session_state.lang = "English"

# --- TRANSLATION DICTIONARY ---
t = {
    "English": {
        "maintitle": "Financial Analytics & Equity Research Hub",
        "tab1": "📈 Corporate Financial Analysis",
        "tab2": "🏗️ BTP Sector Equity Research",
        "tab3": "💹 Live Market Charts",
        "tab4": "👤 About the Creator",
        "tab5": "💼 M&A & Valuation Deal Room",
        "upload_text": "**Upload your company's financial Excel template to unlock the dual-pane analysis dashboard.**",
        "dl_template": "📥 Download Required Template",
        "variance": "📋 Imported Variance Analysis",
        "ratios": "📊 Key Performance Ratios",
        "diagnosis": "💡 Expert Financial Diagnosis",
        "whatif": "🎛️ Sensitivity Analysis (What-If)",
        "sim_rev": "Simulated Revenue (MAD)",
        "sim_margin": "Simulated Net Margin",
        "dl_pdf": "📄 Download Complete PDF Report",
        "lang_sel": "Select Interface Language:"
    },
    "Français": {
        "maintitle": "Hub d'Analyse Financière et de Recherche en Actions",
        "tab1": "📈 Analyse Financière d'Entreprise",
        "tab2": "🏗️ Recherche Secteur BTP",
        "tab3": "💹 Graphiques de Marché",
        "tab4": "👤 À propos du Créateur",
        "tab5": "💼 Salle M&A et Valorisation",
        "upload_text": "**Téléchargez votre modèle Excel financier pour débloquer le tableau de bord d'analyse.**",
        "dl_template": "📥 Télécharger le modèle requis",
        "variance": "📋 Analyse des Écarts Importée",
        "ratios": "📊 Ratios de Performance Clés",
        "diagnosis": "💡 Diagnostic Financier Expert",
        "whatif": "🎛️ Analyse de Sensibilité (Simulations)",
        "sim_rev": "Revenu Simulé (MAD)",
        "sim_margin": "Marge Nette Simulée",
        "dl_pdf": "📄 Télécharger le Rapport PDF Complet",
        "lang_sel": "Sélectionner la Langue de l'Interface :"
    },
    "Arabic": {
        "maintitle": "منصة التحليل المالي وأبحاث الأسهم",
        "tab1": "📈 التحليل المالي للشركات",
        "tab2": "🏗️ أبحاث قطاع البناء",
        "tab3": "💹 رسوم السوق الحية",
        "tab4": "👤 عن المطور",
        "tab5": "💼 غرفة الدمج والاستحواذ والتقييم",
        "upload_text": "**قم بتحميل قالب الإكسيل المالي الخاص بشركتك لفتح لوحة التحليل.**",
        "dl_template": "📥 تحميل القالب المطلوب",
        "variance": "📋 تحليل التباين المستورد",
        "ratios": "📊 مؤشرات الأداء الرئيسية",
        "diagnosis": "💡 التشخيص المالي للخبراء",
        "whatif": "🎛️ تحليل الحساسية (ماذا لو)",
        "sim_rev": "الإيرادات المحاكية (درهم)",
        "sim_margin": "هامش الربح الصافي المحاكي",
        "dl_pdf": "📄 تحميل تقرير PDF الكامل",
        "lang_sel": "اختر لغة الواجهة:"
    }
}

lang = st.session_state.lang
lang_dict = t[lang]

# 2. Premium CSS & Full Width Banner & Animated Button
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
.block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 95% !important; margin: 0 auto; }
.full-width-banner { position: relative; width: 100%; height: 320px; background-image: url('https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=2500&q=80'); background-size: cover; background-position: center; margin-bottom: 2rem; border-radius: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.6); overflow: hidden; }
.banner-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(to right, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 100%); }
.banner-title-container { position: absolute; top: 50%; left: 5%; transform: translateY(-50%); color: white; z-index: 2; }
.banner-title-container h1 { font-size: 3.2rem; font-weight: 700; margin-bottom: 0px; letter-spacing: 1px; color: white; }
.banner-title-container p { font-size: 1.2rem; color: #b3b3b3; margin-top: 5px; font-weight: 400; }
.moroccan-badge { position: absolute; bottom: 25px; right: 30px; background: rgba(15, 15, 15, 0.9); color: white; padding: 12px 24px; border-radius: 8px; font-weight: 600; font-size: 16px; border-left: 4px solid #c1272d; display: flex; align-items: center; gap: 12px; }
.report-box { padding: 20px; border-radius: 10px; background-color: #1e1e1e; border-left: 5px solid; margin-top: 20px; }
.btn-animated-red { background: linear-gradient(45deg, #c1272d, #ff3b3b); color: white !important; padding: 15px 25px; text-align: center; text-decoration: none; display: block; font-size: 18px; font-weight: 700; border-radius: 8px; border: none; cursor: pointer; box-shadow: 0 4px 15px rgba(193, 39, 45, 0.4); transition: all 0.3s ease; animation: pulse 2s infinite; margin-top: 20px; }
.btn-animated-red:hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(193, 39, 45, 0.7); color: white !important; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(193, 39, 45, 0.7); } 70% { box-shadow: 0 0 0 15px rgba(193, 39, 45, 0); } 100% { box-shadow: 0 0 0 0 rgba(193, 39, 45, 0); } }
.metric-card { background-color: #1e1e1e; padding: 15px; border-radius: 8px; border-top: 3px solid #1f77b4; margin-bottom: 15px; }
.pe-card { background-color: #1e1e1e; padding: 15px; border-radius: 8px; border-top: 3px solid #9467bd; margin-bottom: 15px; }
</style>

<div class="full-width-banner">
    <div class="banner-overlay"></div>
    <div class="banner-title-container">
        <h1>Casablanca Stock Exchange</h1>
        <p>BTP Sector Equity Research & Financial Analytics Hub</p>
    </div>
    <div class="moroccan-badge">
        <img src="https://upload.wikimedia.org/wikipedia/commons/2/2c/Flag_of_Morocco.svg" width="28" style="border-radius:2px;">
        CSE Focus
    </div>
</div>
""", unsafe_allow_html=True)

st.title(f"📊 {lang_dict['maintitle']}")
st.markdown("---")

# ==========================================
# DATA ENGINE & HELPERS
# ==========================================
def generate_template():
    df_template = pd.DataFrame({"Line_Item": ["Revenue", "Net Income", "Current Assets", "Current Liabilities", "Inventory", "Total Assets", "Total Equity", "Total Debt"], "2024": [0]*8, "2025": [0]*8})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer: df_template.to_excel(writer, index=False)
    return output.getvalue()

@st.cache_data(ttl=60)
def get_live_market_data():
    try:
        df = pd.read_csv("btp_market_data.csv")
        df["Price_MAD"], df["PE_Ratio"] = pd.to_numeric(df["Price_MAD"], errors='coerce'), pd.to_numeric(df["PE_Ratio"], errors='coerce')
        np.random.seed(int(time.time() / 60))
        fluctuation = np.random.uniform(-0.02, 0.02, len(df))
        df["Live_Price_MAD"] = (df["Price_MAD"] * (1 + fluctuation)).round(2)
        df["Variation"] = (fluctuation * 100).round(2)
        return df
    except: return None

df_live = get_live_market_data()

# --- PREMIUM PDF GENERATOR WITH TABLE ---
def create_pdf(company_ratios, expert_diagnosis, sector_avg_pe, df_table, sim_data):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_fill_color(193, 39, 45)
    pdf.rect(0, 0, 210, 35, 'F')
    
    pdf.set_y(12)
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "FINANCIAL & EQUITY RESEARCH REPORT", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(45)
    pdf.set_font("Arial", 'I', 11)
    pdf.cell(0, 10, f"Generated automatically on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='R')
    pdf.ln(5)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, " 1. Financial Statement Variance Data", border=1, ln=True, fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(60, 8, "Line Item", border=1, align='C', fill=True)
    pdf.cell(45, 8, "2024", border=1, align='C', fill=True)
    pdf.cell(45, 8, "2025", border=1, align='C', fill=True)
    pdf.cell(40, 8, "YoY Growth (%)", border=1, ln=True, align='C', fill=True)
    
    pdf.set_font("Arial", '', 10)
    for index, row in df_table.iterrows():
        pdf.cell(60, 8, str(index), border=1)
        pdf.cell(45, 8, f"{row.iloc[0]:,.0f}", border=1, align='R')
        pdf.cell(45, 8, f"{row.iloc[1]:,.0f}", border=1, align='R')
        val = row['YoY Growth (%)']
        growth_str = f"{val:.2f}%" if pd.notna(val) else "N/A"
        pdf.cell(40, 8, growth_str, border=1, ln=True, align='R')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, " 2. Key Performance Ratios", border=1, ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    for key, value in company_ratios.items():
        pdf.cell(90, 8, f"{key}:", border=0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, f"{value}", border=0, ln=True)
        pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, " 3. Expert Diagnosis & Vulnerabilities", border=1, ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    for note in expert_diagnosis:
        pdf.multi_cell(0, 8, txt=f"> {note}")
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, " 4. Sensitivity Simulation & Market Benchmark", border=1, ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"- Simulated Future Revenue: {sim_data['rev']:,.2f} MAD", ln=True)
    pdf.cell(0, 8, f"- Simulated Future Net Margin: {sim_data['margin']:.2f}%", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 8, txt=f"The company's performance was evaluated against the Casablanca Stock Exchange (CSE) BTP sector. The average sector P/E Ratio currently stands at {sector_avg_pe:.2f}.")
    
    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "Report generated via Z. ELAIDI Automated Analytics Platform", align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# MAIN TABS (5 TABS NOW)
# ==========================================
tab1, tab2, tab5, tab3, tab4 = st.tabs([lang_dict["tab1"], lang_dict["tab2"], lang_dict["tab5"], lang_dict["tab3"], lang_dict["tab4"]])

# ==========================================
# TAB 1: SPLIT SCREEN LAYOUT
# ==========================================
with tab1:
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.markdown(lang_dict["upload_text"])
    with col_header2:
        st.download_button(label=lang_dict["dl_template"], data=generate_template(), file_name="Financial_Template_Standard.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    
    uploaded_file = st.file_uploader("Excel (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            df_finance = pd.read_excel(uploaded_file)
            df_finance.columns = [str(c).strip() for c in df_finance.columns]
            df_finance.iloc[:, 0] = df_finance.iloc[:, 0].astype(str).str.strip()
            df_finance.set_index(df_finance.columns[0], inplace=True)
            col_2024, col_2025 = [c for c in df_finance.columns if '2024' in str(c)][0], [c for c in df_finance.columns if '2025' in str(c)][0]
            
            # DUAL COLUMN
            left_col, right_col = st.columns([1.3, 1], gap="large")
            
            # LEFT COLUMN
            with left_col:
                st.subheader(lang_dict["variance"])
                df_display = df_finance.copy()
                df_display[col_2024], df_display[col_2025] = pd.to_numeric(df_display[col_2024], errors='coerce'), pd.to_numeric(df_display[col_2025], errors='coerce')
                df_display['YoY Growth (%)'] = ((df_display[col_2025] - df_display[col_2024]) / df_display[col_2024]) * 100
                
                def color_variance(row):
                    item, val = str(row.name).lower(), row['YoY Growth (%)']
                    if pd.isna(val): return [''] * len(row)
                    color = '#ff0000' if ('liability' in item or 'debt' in item) and val > 0 else '#00ff00' if val > 0 else '#ff0000'
                    return [f'color: {color}' if col == 'YoY Growth (%)' else '' for col in row.index]

                st.dataframe(df_display.style.apply(color_variance, axis=1).format({'YoY Growth (%)': "{:.2f}%"}), use_container_width=True)

                rev_25, net_25, ca_25, cl_25, eq_25 = float(df_finance.loc["Revenue", col_2025]), float(df_finance.loc["Net Income", col_2025]), float(df_finance.loc["Current Assets", col_2025]), float(df_finance.loc["Current Liabilities", col_2025]), float(df_finance.loc["Total Equity", col_2025])
                current_ratio_25, net_margin_25, roe_25 = ca_25 / cl_25, (net_25 / rev_25) * 100, (net_25 / eq_25) * 100
                
                st.subheader(lang_dict["ratios"])
                c1, c2, c3 = st.columns(3)
                fig1 = go.Figure(go.Indicator(mode="gauge+number", value=current_ratio_25, title={'text': "Current Ratio", 'font': {'size': 14}}, gauge={'axis': {'range': [0, 3]}, 'bar': {'color': "#2ca02c"}}))
                fig1.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
                c1.plotly_chart(fig1, use_container_width=True)
                
                fig2 = go.Figure(go.Indicator(mode="gauge+number", value=net_margin_25, number={'suffix': "%"}, title={'text': "Net Margin", 'font': {'size': 14}}, gauge={'axis': {'range': [0, 30]}, 'bar': {'color': "#1f77b4"}}))
                fig2.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
                c2.plotly_chart(fig2, use_container_width=True)
                
                fig3 = go.Figure(go.Indicator(mode="gauge+number", value=roe_25, number={'suffix': "%"}, title={'text': "ROE", 'font': {'size': 14}}, gauge={'axis': {'range': [0, 40]}, 'bar': {'color': "#9467bd"}}))
                fig3.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
                c3.plotly_chart(fig3, use_container_width=True)

                st.subheader(lang_dict["diagnosis"])
                score_positif = sum([current_ratio_25 >= 1.2, net_margin_25 >= 8.0, roe_25 >= 12.0])
                color, status, selected_nbs = ("#2ca02c", "Favorable Financial Situation (Key Strengths)", ["Excellent cash management. Easily self-finances operations.", "Strong operational profitability confirmed across the board.", "Optimal value creation for shareholders with a highly attractive ROE."]) if score_positif >= 2 else ("#d62728", "Critical Financial Situation (Vulnerabilities)", ["Severe liquidity drain: Imminent risk of short-term insolvency.", "Value destruction: ROE is too low to attract or retain investors.", "Current debt burden is too heavy compared to available liquidity."])
                    
                st.markdown(f"""
                <div class="report-box" style="border-color: {color};"><h4 style="color: {color}; margin-top: 0;">{status}</h4>
                <ul><li style="color: {color};"><b>N.B:</b> {selected_nbs[0]}</li><li style="color: {color};"><b>N.B:</b> {selected_nbs[1]}</li><li style="color: {color};"><b>N.B:</b> {selected_nbs[2]}</li></ul></div>
                """, unsafe_allow_html=True)

            # RIGHT COLUMN
            with right_col:
                st.subheader(lang_dict["whatif"])
                col_sl1, col_num1 = st.columns([3, 1])
                with col_sl1: sim_rev_slider = st.slider("Revenue Growth (%)", -30, 30, 0, step=1)
                with col_num1: sim_rev_exact = st.number_input("Exact %", -30, 30, sim_rev_slider, step=1, label_visibility="collapsed")
                
                col_sl2, col_num2 = st.columns([3, 1])
                with col_sl2: sim_cost_slider = st.slider("Cost Reduction (%)", 0, 30, 0, step=1)
                with col_num2: sim_cost_exact = st.number_input("Exact %", 0, 30, sim_cost_slider, step=1, key="cost_ex", label_visibility="collapsed")
                
                st.caption("💡 *Tip: Use the sliders or type exact numbers in the boxes on the right.*")
                
                sim_rev = rev_25 * (1 + (sim_rev_exact/100))
                sim_costs = (rev_25 - net_25) * (1 - (sim_cost_exact/100))
                sim_net = sim_rev - sim_costs
                sim_margin = (sim_net / sim_rev * 100) if sim_rev > 0 else 0
                
                st.markdown(f"""
                <div class="metric-card"><p style="margin:0; color:#b3b3b3; font-size:14px;">{lang_dict["sim_rev"]}</p><h3 style="margin:0; color:#00ff00;">{sim_rev:,.2f}</h3></div>
                <div class="metric-card"><p style="margin:0; color:#b3b3b3; font-size:14px;">{lang_dict["sim_margin"]}</p><h3 style="margin:0; color:#1f77b4;">{sim_margin:.2f}%</h3></div>
                """, unsafe_allow_html=True)
                
                sector_pe = df_live['PE_Ratio'].mean() if df_live is not None else 15.0

                # --- ANIMATED RED PDF DOWNLOAD BUTTON ---
                st.markdown("<br><br>", unsafe_allow_html=True)
                ratios_dict = {"Revenue": f"{rev_25:,.2f} MAD", "Net Margin": f"{net_margin_25:.2f}%", "ROE": f"{roe_25:.2f}%", "Current Ratio": f"{current_ratio_25:.2f}"}
                
                try:
                    pdf_bytes = create_pdf(ratios_dict, selected_nbs, sector_pe, df_display, {"rev": sim_rev, "margin": sim_margin})
                    b64_pdf = base64.b64encode(pdf_bytes).decode('latin-1')
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="Financial_Report_Z_ELAIDI.pdf" class="btn-animated-red">{lang_dict["dl_pdf"]}</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e: st.error("Error generating PDF. Ensure fpdf is installed.")

        except Exception as e: st.error(f"⚠️ Format Error.")

# ==========================================
# TAB 2
# ==========================================
with tab2:
    if df_live is not None:
        def color_variation(val): return f"color: {'#00ff00' if val > 0 else '#ff0000' if val < 0 else 'white'}"
        st.dataframe(df_live[["Company", "Live_Price_MAD", "Variation", "Market_Cap_Billion", "PE_Ratio", "Dividend_Yield"]].style.map(color_variation, subset=['Variation']).highlight_max(axis=0, subset=["Market_Cap_Billion"], color="#1f77b4"), use_container_width=True)
        fig = px.bar(df_live, x="Company", y="Live_Price_MAD", color="Variation", title="Live Stock Prices (MAD) & Intraday Variation", color_continuous_scale="RdYlGn", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ==========================================
# TAB 5: M&A & VALUATION DEAL ROOM (NEW)
# ==========================================
with tab5:
    st.header("💼 M&A & Private Equity Deal Room")
    st.markdown("Advanced Intrinsic Valuation (DCF) & Leveraged Buyout (LBO) Modeling.")

    has_data = 'rev_25' in locals() and 'net_25' in locals()
    if not has_data:
        st.info("💡 Upload your Financial Template in Tab 1 to automatically populate these models with your company's data. Using standard proxy data for now.")
    
    base_rev = rev_25 if has_data else 5000000.0
    base_ebitda = net_25 * 1.3 if has_data else 1200000.0 # Proxy EBITDA

    col_dcf, col_lbo = st.columns(2, gap="large")

    with col_dcf:
        st.subheader("📊 DCF Valuation Engine")
        wacc = st.slider("WACC (Discount Rate) %", 5.0, 20.0, 10.0, 0.5) / 100
        tg = st.slider("Terminal Growth Rate %", 0.0, 5.0, 2.0, 0.1) / 100
        proj_growth = st.slider("Projected Annual Growth %", -10.0, 30.0, 5.0, 1.0) / 100
        margin = st.slider("Target Cash Flow Margin %", 1.0, 30.0, 15.0, 1.0) / 100

        cfs = [base_rev * ((1 + proj_growth)**i) * margin for i in range(1, 6)]
        pv_cfs = sum([cf / ((1 + wacc)**(i+1)) for i, cf in enumerate(cfs)])
        tv = (cfs[-1] * (1 + tg)) / (wacc - tg) if wacc > tg else 0
        pv_tv = tv / ((1 + wacc)**5)
        ev = pv_cfs + pv_tv

        st.markdown(f"""
        <div class="metric-card">
            <p style="margin:0; color:#b3b3b3; font-size:14px;">Implied Enterprise Value (EV)</p>
            <h2 style="margin:0; color:#00ff00;">{ev:,.2f} MAD</h2>
        </div>
        """, unsafe_allow_html=True)

    with col_lbo:
        st.subheader("💰 LBO Quick-Modeler")
        
        c_l1, c_l2 = st.columns(2)
        with c_l1: entry_mult = st.number_input("Entry Multiple (x)", 3.0, 15.0, 6.0, 0.5)
        with c_l2: exit_mult = st.number_input("Exit Multiple (x)", 3.0, 15.0, 6.0, 0.5)
        
        debt_pct = st.slider("Debt Funding %", 0.0, 90.0, 60.0, 5.0) / 100

        entry_ev = base_ebitda * entry_mult
        debt_amount = entry_ev * debt_pct
        equity_amount = entry_ev - debt_amount

        total_cf = sum(cfs)
        debt_paydown = min(total_cf * 0.5, debt_amount) 
        remaining_debt = debt_amount - debt_paydown

        exit_ebitda = base_ebitda * ((1 + proj_growth)**5)
        exit_ev = exit_ebitda * exit_mult
        exit_equity = exit_ev - remaining_debt

        moic = exit_equity / equity_amount if equity_amount > 0 else 0
        irr = (moic**(1/5) - 1) * 100 if moic > 0 else 0
        color_irr = "#00ff00" if irr >= 20 else ("#ffbb00" if irr >= 10 else "#ff0000")

        st.markdown(f"""
        <div class="pe-card">
            <p style="margin:0; color:#b3b3b3; font-size:14px;">Private Equity IRR (5-Year)</p>
            <h2 style="margin:0; color:{color_irr};">{irr:.2f}%</h2>
            <p style="margin:0; color:#b3b3b3; font-size:14px;">MoIC (Multiple on Invested Capital): <b>{moic:.2f}x</b></p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 3
# ==========================================
with tab3:
    if df_live is not None:
        c_sel1, c_sel2, c_sel3 = st.columns(3)
        with c_sel1: selected_company = st.selectbox("Company:", df_live["Company"].tolist())
        with c_sel2: time_period = st.selectbox("Timeframe:", ["1 Month (30 Days)", "3 Months (90 Days)", "6 Months (180 Days)"])
        with c_sel3: chart_type = st.radio("Style:", ["Candlesticks", "Line Chart"], horizontal=True)
        
        num_days = {"1 Month (30 Days)": 30, "3 Months (90 Days)": 90, "6 Months (180 Days)": 180}[time_period]
        base_price = df_live[df_live["Company"] == selected_company]["Live_Price_MAD"].values[0]
        dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=num_days)
        
        np.random.seed(42 + len(selected_company) + num_days)
        vol = base_price * 0.05
        changes = np.random.normal(0, vol, size=num_days)
        closes = base_price - np.cumsum(changes[::-1])[::-1] 
        opens = closes - np.random.normal(0, vol, size=num_days)
        highs, lows = np.maximum(opens, closes) + np.abs(np.random.normal(0, vol*1.2, size=num_days)), np.minimum(opens, closes) - np.abs(np.random.normal(0, vol*1.2, size=num_days))
        
        if chart_type == "Candlesticks": fig_m = go.Figure(data=[go.Candlestick(x=dates, open=opens, high=highs, low=lows, close=closes, increasing_line_color='#00ff00', decreasing_line_color='#ff0000')])
        else: fig_m = go.Figure(data=[go.Scatter(x=dates, y=closes, mode='lines+markers', line=dict(color='#1f77b4', width=2))])
            
        fig_m.update_layout(height=450, title=f"Price - {selected_company}", template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_m, use_container_width=True)

# ==========================================
# TAB 4
# ==========================================
with tab4:
    st.header("👤 About the Creator")
    col_about1, col_about2 = st.columns([2, 1])
    with col_about1:
        st.markdown("""
        ### **Zakaria Elaidi** | *Financial Analyst*
        
        Zakaria is a dedicated financial analyst currently specializing in Finance at the prestigious **Ecole Nationale de Commerce et de Gestion (ENCG) in El Jadida**. 
        
        With a strong background in corporate finance and data analysis, Zakaria operates as a successful freelance financial consultant. He has a proven track record, having delivered over **150 financial modeling and consulting projects** for a global client base.
        
        **Platform Vision:**
        This platform bridges the gap between traditional equity research and automated data visualization. By utilizing Python, this tool aims to transform manual financial assessments into rapid, data-driven insights.
        """)
        st.info("💡 **Core Expertise:** Equity Research, Corporate Finance, Data Automation, Financial Modeling.")
    with col_about2:
        st.markdown('<div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; text-align: center; border-top: 4px solid #c1272d;"><h3 style="margin-top:0;">Professional Network</h3><p>Open for financial consulting opportunities, equity research projects, and professional networking.</p><br><a href="https://www.linkedin.com/in/zakaria-elaidi/" target="_blank" style="background-color: #0077b5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Connect on LinkedIn</a></div>', unsafe_allow_html=True)

# ==========================================
# FOOTER & BOTTOM LANGUAGE SELECTOR
# ==========================================
st.markdown("---")

col_foot1, col_foot2, col_foot3 = st.columns([1, 2, 1])
with col_foot2:
    st.markdown(f"<p style='text-align: center; color: #b3b3b3; margin-bottom: 5px;'>🌐 <b>{lang_dict['lang_sel']}</b></p>", unsafe_allow_html=True)
    sel_lang = st.radio("Lang", ["English", "Français", "Arabic"], index=["English", "Français", "Arabic"].index(st.session_state.lang), horizontal=True, label_visibility="collapsed")
    if sel_lang != st.session_state.lang:
        st.session_state.lang = sel_lang
        st.rerun()

st.markdown("<div style='text-align: center; color: #a0a0a0; font-size: 15px; margin-top: 20px;'>© 2026 | Automated Financial Analytics Platform | <b>Designed & Built by ELAIDI ZAKARIA</b></div>", unsafe_allow_html=True)
