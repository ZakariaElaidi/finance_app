import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import json
import base64
from datetime import datetime
from fpdf import FPDF
from supabase import create_client, ClientOptions

# --- SECURITY: Redirect if not logged in ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

st.markdown("""
<style>
.metric-box { background-color: #161a22; padding: 15px; border-radius: 8px; border-top: 3px solid #1f77b4; margin-bottom: 15px; text-align: center; }
.report-box { padding: 20px; border-radius: 10px; background-color: #161a22; border-left: 5px solid; margin-top: 20px; }
.btn-pdf-teaser { background-color: #f5b041; color: #000 !important; padding: 12px 15px; text-align: center; display: block; border-radius: 5px; text-decoration: none !important; font-weight: bold; margin-top: 10px; transition: 0.3s; }
.btn-pdf-teaser:hover { background-color: #d68910; color: #000 !important; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Corporate Analysis")

# --- SUPABASE INIT ---
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"], options=ClientOptions(postgrest_client_timeout=10))
except:
    st.error("Database connection failed.")
    st.stop()

def save_history(user_id, email, data_dict):
    try:
        supabase.table("users_history").insert({"user_id": user_id, "email": email, "work_data": json.dumps(data_dict)}).execute()
        return True
    except: return False

def generate_template():
    df_template = pd.DataFrame({"Line_Item": ["Revenue", "Net Income", "Current Assets", "Current Liabilities", "Inventory", "Total Assets", "Total Equity", "Total Debt"], "2024": [0]*8, "2025": [0]*8})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer: df_template.to_excel(writer, index=False)
    return output.getvalue()

# --- M&A TEASER GENERATOR (ONE-PAGER) ---
def create_teaser_pdf(ratios, diagnosis, rev_sim, margin_sim):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 20, 15)
    
    # Teaser Header
    pdf.set_fill_color(31, 119, 180) # Pro Blue
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_y(15)
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "INVESTMENT TEASER (PROJECT ALPHA)", ln=True, align='C')
    
    pdf.set_y(50)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Executive Summary", border=0, ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, "This document presents a high-level overview of a prospective target operating within the Moroccan BTP sector. The target demonstrates specific financial characteristics making it a subject of interest for M&A / Private Equity evaluation.")
    pdf.ln(8)
    
    # Financial Highlights Box
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, " Key Financial Highlights (FY 2025)", border=1, ln=True, fill=True)
    pdf.ln(5)
    
    for k, v in ratios.items():
        pdf.set_font("Arial", '', 12)
        pdf.cell(60, 9, f"{k}:", border=0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 9, f"{v}", border=0, ln=True)
    pdf.ln(8)
    
    # Sensitivity Outlook
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, " Forward-Looking Outlook (Simulated)", border=1, ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    pdf.cell(60, 8, "Projected Revenue:", border=0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"{rev_sim:,.2f} MAD", border=0, ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(60, 8, "Projected Margin:", border=0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"{margin_sim:.2f}%", border=0, ln=True)
    pdf.ln(8)

    # Investment Merits
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, " Investment Merits & Diagnosis", border=1, ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    for note in diagnosis:
        pdf.multi_cell(0, 8, txt=f" \x95 {note}")
        
    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.line(15, 275, 195, 275)
    pdf.cell(0, 10, "Strictly Confidential | M&A Advisory Desk - Z.ELAIDI Financial Hub", align='C')
    return bytes(pdf.output())

# --- THE UI ---
c1, c2 = st.columns([3, 1])
with c1: st.write("Upload your company's financial Excel template.")
with c2: st.download_button("📥 Download Template", data=generate_template(), file_name="Template.xlsx", use_container_width=True)

uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"], label_visibility="collapsed")

if uploaded_file:
    try:
        df_finance = pd.read_excel(uploaded_file)
        df_finance.columns = [str(c).strip() for c in df_finance.columns]
        df_finance.set_index(df_finance.columns[0], inplace=True)
        
        col_24, col_25 = df_finance.columns[0], df_finance.columns[1]
        
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
            ca_25, cl_25 = float(df_finance.loc["Current Assets", col_25]), float(df_finance.loc["Current Liabilities", col_25])
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
                <p style="margin:0; color:#b3b3b3; font-size:14px;">Simulated Revenue (MAD)</p><h3 style="margin:0; color:#2ca02c;">{sim_rev:,.2f}</h3>
            </div>
            <div class="metric-box">
                <p style="margin:0; color:#b3b3b3; font-size:14px;">Simulated Net Margin</p><h3 style="margin:0; color:#1f77b4;">{sim_margin:.2f}%</h3>
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
            if st.button("💾 Save to History", use_container_width=True):
                session_data = {"Session_Name": f"Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M')}", "Revenue": rev_25, "Net Margin": round(user_net_margin, 2), "ROE": round(user_roe, 2), "Current Ratio": round(current_ratio, 2), "Date": datetime.now().strftime('%Y-%m-%d %H:%M')}
                if save_history(st.session_state.user.id, st.session_state.user.email, session_data): st.success("✅ Saved successfully!")
                else: st.error("⚠️ Failed to save.")
                
        with c_action2:
            ratios_dict = {"Revenue": f"{rev_25:,.2f} MAD", "Net Margin": f"{user_net_margin:.2f}%", "ROE": f"{user_roe:.2f}%", "Current Ratio": f"{current_ratio:.2f}"}
            pdf_bytes = create_teaser_pdf(ratios_dict, selected_nbs, sim_rev, sim_margin)
            b64_pdf = base64.b64encode(pdf_bytes).decode('latin-1')
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="MA_Teaser_Project_Alpha.pdf" class="btn-pdf-teaser">📑 Download M&A Teaser</a>'
            st.markdown(href, unsafe_allow_html=True)
            

    except Exception as e:
        st.error(f"⚠️ Error processing file. Ensure strict template format. Details: {str(e)}")
