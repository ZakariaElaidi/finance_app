import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import json
from datetime import datetime
from fpdf import FPDF
from supabase import create_client, ClientOptions

# --- SECURITY ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

# --- GLOBAL STATE INITIALIZATION ---
lang = st.session_state.get("lang", "English")
curr = st.session_state.get("currency", "MAD")
rates = st.session_state.get("rates", {"MAD": 1.0, "USD": 0.10, "EUR": 0.09})
syms = st.session_state.get("sym", {"MAD": "MAD", "USD": "$", "EUR": "€"})

rate = rates[curr]
sym = syms[curr]

# --- TRANSLATION DICTIONARY ---
t = {
    "English": {
        "title": "📈 Corporate Analysis", "banner_desc": "Upload financial models, run variance analysis, and generate expert diagnostics.",
        "upload": "Upload your company's financial Excel template.", "dl_temp": "📥 Download Template",
        "var_title": "📋 Variance Analysis", "sens_title": "🎛️ Sensitivity (What-If)", 
        "rev_growth": "Revenue Growth (%)", "cost_red": "Cost Reduction (%)",
        "sim_rev": "Simulated Revenue", "sim_margin": "Simulated Net Margin",
        "kpi_title": "📊 Key Performance Ratios", "cr": "Current Ratio", "nm": "Net Margin", "roe": "ROE",
        "diag_title": "💡 Expert Diagnosis", "fav": "Favorable Financial Situation", "crit": "Critical Financial Situation",
        "fav_n1": "Excellent liquidity management.", "fav_n2": "Strong operational profitability confirmed.", "fav_n3": "Optimal value creation for shareholders with attractive ROE.",
        "crit_n1": "Potential liquidity drain: Monitor short-term solvency.", "crit_n2": "Value destruction: Margins are below sector standards.", "crit_n3": "High dependency on debt or low operational efficiency.",
        "yoy_title": "📈 YoY Progression", "rev": "Revenue", "net": "Net Income",
        "act_title": "💾 Actions & Reports", "save": "💾 Save to History", "dl_pdf": "📄 Download as a PDF", "dl_xlsx": "📥 Export Detailed Excel (with Charts)",
        "success_save": "✅ Saved successfully!", "fail_save": "⚠️ Failed to save.", "err_file": "⚠️ Error processing file. Ensure strict template format.",
        # PDF specific (English)
        "pdf_head": "COMPREHENSIVE FINANCIAL REPORT", "pdf_gen": "Generated on", "pdf_s1": "1. Financial Statements Overview & Variance",
        "pdf_col1": "Line Item", "pdf_col2": "YoY Growth (%)", "pdf_s2": "2. Key Performance Indicators",
        "pdf_s3": "3. Scenario & Sensitivity Outlook", "pdf_sim_rev": "- Simulated Projected Revenue:", "pdf_sim_mar": "- Simulated Projected Net Margin:",
        "pdf_s4": "4. Expert Diagnosis & Recommendations", "pdf_foot": "Strictly Confidential | M&A Advisory Desk - Z.ELAIDI Financial Hub"
    },
    "Français": {
        "title": "📈 Analyse d'Entreprise", "banner_desc": "Importez des modèles financiers, analysez les écarts et générez des diagnostics.",
        "upload": "Importez le modèle financier Excel de votre entreprise.", "dl_temp": "📥 Télécharger le Modèle",
        "var_title": "📋 Analyse des Écarts", "sens_title": "🎛️ Sensibilité (Simulations)", 
        "rev_growth": "Croissance des Revenus (%)", "cost_red": "Réduction des Coûts (%)",
        "sim_rev": "Revenus Simulés", "sim_margin": "Marge Nette Simulée",
        "kpi_title": "📊 Indicateurs de Performance", "cr": "Ratio de Liquidité", "nm": "Marge Nette", "roe": "ROE",
        "diag_title": "💡 Diagnostic d'Expert", "fav": "Situation Financière Favorable", "crit": "Situation Financière Critique",
        "fav_n1": "Excellente gestion de la liquidité.", "fav_n2": "Forte rentabilité opérationnelle confirmée.", "fav_n3": "Création de valeur optimale pour les actionnaires (ROE attractif).",
        "crit_n1": "Risque de liquidité potentiel : Surveillez la solvabilité à court terme.", "crit_n2": "Destruction de valeur : Les marges sont inférieures aux normes du secteur.", "crit_n3": "Forte dépendance à la dette ou faible efficacité opérationnelle.",
        "yoy_title": "📈 Progression Annuelle", "rev": "Revenus", "net": "Revenu Net",
        "act_title": "💾 Actions & Rapports", "save": "💾 Sauvegarder dans l'Historique", "dl_pdf": "📄 Télécharger en PDF", "dl_xlsx": "📥 Exporter en Excel (avec Graphiques)",
        "success_save": "✅ Sauvegardé avec succès !", "fail_save": "⚠️ Échec de la sauvegarde.", "err_file": "⚠️ Erreur de traitement. Assurez-vous du format du modèle.",
        # PDF specific (Français)
        "pdf_head": "RAPPORT FINANCIER COMPLET", "pdf_gen": "Généré le", "pdf_s1": "1. Aperçu des États Financiers et Écarts",
        "pdf_col1": "Poste", "pdf_col2": "Croissance Annuelle (%)", "pdf_s2": "2. Indicateurs Clés de Performance",
        "pdf_s3": "3. Perspectives de Sensibilité", "pdf_sim_rev": "- Revenus Projetés Simulés :", "pdf_sim_mar": "- Marge Nette Projetée Simulée :",
        "pdf_s4": "4. Diagnostic d'Expert et Recommandations", "pdf_foot": "Strictement Confidentiel | Bureau de Conseil M&A - Z.ELAIDI Financial Hub"
    },
    "Español": {
        "title": "📈 Análisis Corporativo", "banner_desc": "Sube modelos financieros, analiza variaciones y genera diagnósticos de expertos.",
        "upload": "Sube la plantilla financiera en Excel de tu empresa.", "dl_temp": "📥 Descargar Plantilla",
        "var_title": "📋 Análisis de Variaciones", "sens_title": "🎛️ Sensibilidad (Escenarios)", 
        "rev_growth": "Crecimiento de Ingresos (%)", "cost_red": "Reducción de Costes (%)",
        "sim_rev": "Ingresos Simulados", "sim_margin": "Margen Neto Simulado",
        "kpi_title": "📊 Ratios de Rendimiento", "cr": "Ratio de Liquidez", "nm": "Margen Neto", "roe": "ROE",
        "diag_title": "💡 Diagnóstico de Expertos", "fav": "Situación Financiera Favorable", "crit": "Situación Financiera Crítica",
        "fav_n1": "Excelente gestión de la liquidez.", "fav_n2": "Fuerte rentabilidad operativa confirmada.", "fav_n3": "Óptima creación de valor para los accionistas (ROE atractivo).",
        "crit_n1": "Riesgo de liquidez: Monitorear solvencia a corto plazo.", "crit_n2": "Destrucción de valor: Márgenes por debajo de los estándares del sector.", "crit_n3": "Alta dependencia de la deuda o baja eficiencia operativa.",
        "yoy_title": "📈 Progresión Interanual", "rev": "Ingresos", "net": "Ingreso Neto",
        "act_title": "💾 Acciones y Reportes", "save": "💾 Guardar en Historial", "dl_pdf": "📄 Descargar como PDF", "dl_xlsx": "📥 Excel Detallado (con Gráficos)",
        "success_save": "✅ ¡Guardado exitosamente!", "fail_save": "⚠️ Error al guardar.", "err_file": "⚠️ Error al procesar el archivo. Asegure el formato de la plantilla.",
        # PDF specific (Español)
        "pdf_head": "INFORME FINANCIERO COMPLETO", "pdf_gen": "Generado el", "pdf_s1": "1. Resumen de Estados Financieros y Variaciones",
        "pdf_col1": "Partida", "pdf_col2": "Crecimiento Interanual (%)", "pdf_s2": "2. Indicadores Clave de Rendimiento",
        "pdf_s3": "3. Perspectivas de Sensibilidad", "pdf_sim_rev": "- Ingresos Proyectados Simulados:", "pdf_sim_mar": "- Margen Neto Proyectado Simulado:",
        "pdf_s4": "4. Diagnóstico de Expertos y Recomendaciones", "pdf_foot": "Estrictamente Confidencial | Asesoría M&A - Z.ELAIDI Financial Hub"
    },
    "العربية": {
        "title": "📈 تحليل الشركات", "banner_desc": "رفع النماذج المالية، تحليل التغيرات، واستخراج تشخيصات الخبراء.",
        "upload": "قم برفع نموذج الإكسل المالي لشركتك.", "dl_temp": "📥 تنزيل النموذج",
        "var_title": "📋 تحليل التغيرات", "sens_title": "🎛️ تحليل الحساسية (محاكاة)", 
        "rev_growth": "نمو الإيرادات (%)", "cost_red": "تخفيض التكاليف (%)",
        "sim_rev": "الإيرادات المحاكية", "sim_margin": "هامش الربح الصافي المحاكى",
        "kpi_title": "📊 مؤشرات الأداء الرئيسية", "cr": "نسبة التداول (السيولة)", "nm": "هامش الربح الصافي", "roe": "العائد على حقوق المساهمين",
        "diag_title": "💡 تشخيص الخبراء", "fav": "وضع مالي ملائم", "crit": "وضع مالي حرج",
        "fav_n1": "إدارة ممتازة للسيولة النقدية.", "fav_n2": "ربحية تشغيلية قوية ومؤكدة.", "fav_n3": "خلق قيمة مثالية للمساهمين مع عائد جذاب.",
        "crit_n1": "استنزاف محتمل للسيولة: راقب الملاءة المالية قصيرة الأجل.", "crit_n2": "تدمير القيمة: هوامش الربح أقل من معايير القطاع.", "crit_n3": "اعتماد كبير على الديون أو كفاءة تشغيلية منخفضة.",
        "yoy_title": "📈 التطور السنوي", "rev": "الإيرادات", "net": "صافي الدخل",
        "act_title": "💾 الإجراءات والتقارير", "save": "💾 حفظ في السجل", "dl_pdf": "📄 تنزيل كملف PDF", "dl_xlsx": "📥 تنزيل تقرير Excel مفصل",
        "success_save": "✅ تم الحفظ بنجاح!", "fail_save": "⚠️ فشل الحفظ.", "err_file": "⚠️ خطأ في معالجة الملف. يرجى التأكد من التنسيق."
    }
}

txt = t[lang]

# PDF Fallback logic
pdf_lang = lang if lang != "العربية" else "English"
pdf_txt = t[pdf_lang]

# --- UI STYLING & CSS HACKS ---
rtl_css = ""
if lang == "العربية":
    rtl_css = """
    .block-container { direction: rtl; text-align: right; }
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"], [data-testid="stHeader"] { direction: ltr !important; text-align: left !important; }
    """

st.markdown(f"""
<style>
    /* Global Fade-in Animation */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(15px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .block-container {{ animation: fadeIn 0.6s ease-out; }}

    [data-testid="stSidebarNav"] li:first-child a span {{ display: none !important; }}
    [data-testid="stSidebarNav"] li:first-child a::after {{ content: "🏠 Home"; font-size: 15px; margin-left: 0px; }}
    .metric-box {{ background-color: #161a22; padding: 15px; border-radius: 8px; border-top: 3px solid #1f77b4; margin-bottom: 15px; text-align: center; }}
    .report-box {{ padding: 20px; border-radius: 10px; background-color: #161a22; border-left: 5px solid; margin-top: 20px; }}
    
    /* Corporate Banner Styling (Blue Theme) */
    .full-width-banner {{ position: relative; width: 100%; height: 250px; background-image: url('https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=2015&auto=format&fit=crop'); background-size: cover; background-position: center; margin-bottom: 25px; border-radius: 10px; border-left: 5px solid #1f77b4; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
    .banner-overlay {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, rgba(14,17,23,1) 0%, rgba(14,17,23,0.8) 40%, rgba(31,119,180,0.3) 100%); }}
    .banner-content {{ position: absolute; top: 50%; left: 30px; transform: translateY(-50%); z-index: 2; }}
    
    {rtl_css}
    
    /* =========================================
       📱 MOBILE RESPONSIVENESS (SMART SCREENS)
       ========================================= */
    @media (max-width: 768px) {{
        .block-container {{ padding-top: 2rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }}
        [data-testid="stDataFrame"] {{ overflow-x: auto !important; max-width: 100% !important; }}
        .banner h1, .full-width-banner h1 {{ font-size: 1.6rem !important; }}
        .banner p, .full-width-banner p {{ font-size: 0.9rem !important; }}
        .js-plotly-plot, .plotly, .plot-container {{ max-width: 100% !important; }}
        [data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; margin-bottom: 15px !important; }}
    }}
</style>
""", unsafe_allow_html=True)

# --- BANNER (Replaces st.title) ---
st.markdown(f"""
<div class="full-width-banner">
    <div class="banner-overlay"></div>
    <div class="banner-content" {'dir="rtl"' if lang=="العربية" else ''}>
        <h1 style="color: white; margin: 0; font-size: 2.5rem; letter-spacing: 1px;">{txt['title']}</h1>
        <p style="color:#e0e0e0; font-size:1.1rem; margin-top: 8px;">{txt['banner_desc']}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SUPABASE INIT ---
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"], options=ClientOptions(postgrest_client_timeout=10))
except Exception:
    st.error("Database connection failed.")
    st.stop()

def save_history(user_id, email, data_dict):
    try:
        supabase.table("users_history").insert({"user_id": user_id, "email": email, "work_data": json.dumps(data_dict)}).execute()
        return True
    except Exception: return False

def generate_template():
    df_template = pd.DataFrame({"Line_Item": ["Revenue", "Net Income", "Current Assets", "Current Liabilities", "Inventory", "Total Assets", "Total Equity", "Total Debt"], "2024": [0]*8, "2025": [0]*8})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer: df_template.to_excel(writer, index=False)
    return output.getvalue()

# --- RICH DETAILED PDF GENERATOR ---
def create_rich_pdf(df_display, net_margin, roe, current_ratio, sim_rev, sim_margin, diagnosis, p_txt, p_sym):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    pdf.set_fill_color(31, 119, 180) 
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_y(12)
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, p_txt["pdf_head"].encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 6, f"{p_txt['pdf_gen']}: {datetime.now().strftime('%d %b %Y - %H:%M')}", ln=True, align='C')
    
    pdf.set_y(45)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, f" {p_txt['pdf_s1']}", border=1, ln=True, fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(65, 8, p_txt["pdf_col1"], border=1)
    pdf.cell(35, 8, f"FY 2024 ({p_sym})", border=1, align='C')
    pdf.cell(35, 8, f"FY 2025 ({p_sym})", border=1, align='C')
    pdf.cell(45, 8, p_txt["pdf_col2"], border=1, align='C', ln=True)
    
    pdf.set_font("Arial", '', 10)
    for index, row in df_display.iterrows():
        safe_index = str(index).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(65, 8, safe_index, border=1)
        pdf.cell(35, 8, f"{row.iloc[0]:,.0f}", border=1, align='R')
        pdf.cell(35, 8, f"{row.iloc[1]:,.0f}", border=1, align='R')
        
        val = row['YoY Growth (%)']
        var_text = f"{val:.2f}%" if pd.notnull(val) else "N/A"
        pdf.cell(45, 8, var_text, border=1, align='R', ln=True)
        
    pdf.ln(8)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f" {p_txt['pdf_s2']} (FY 2025)", border=1, ln=True, fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(50, 8, f"{p_txt['nm']}:", border=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"{net_margin:.2f}%", border=0, ln=True)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(50, 8, f"{p_txt['roe']}:", border=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"{roe:.2f}%", border=0, ln=True)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(50, 8, f"{p_txt['cr']}:", border=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"{current_ratio:.2f}x", border=0, ln=True)
    pdf.ln(8)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f" {p_txt['pdf_s3']}", border=1, ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 7, f"{p_txt['pdf_sim_rev']} {sim_rev:,.2f} {p_sym}", ln=True)
    pdf.cell(0, 7, f"{p_txt['pdf_sim_mar']} {sim_margin:.2f}%", ln=True)
    pdf.ln(8)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f" {p_txt['pdf_s4']}", border=1, ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    
    for note in diagnosis:
        pdf.set_x(15)
        safe_note = note.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, txt=f"- {safe_note}")
        
    pdf.set_y(-20)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.line(15, 275, 195, 275)
    pdf.cell(0, 10, p_txt["pdf_foot"].encode('latin-1', 'replace').decode('latin-1'), align='C')
    
    return bytes(pdf.output())

# --- APP LOGIC ---
c1, c2 = st.columns([3, 1])
with c1: st.write(txt["upload"])
with c2: st.download_button(txt["dl_temp"], data=generate_template(), file_name="Template.xlsx", use_container_width=True)

uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"], label_visibility="collapsed")

if uploaded_file:
    try:
        # DATA VALIDATOR
        df_finance = pd.read_excel(uploaded_file, index_col=0)
        df_finance.index = df_finance.index.str.strip()
        
        required_cols = ["Revenue", "Net Income", "Current Assets", "Current Liabilities", "Total Equity"]
        missing = [col for col in required_cols if col not in df_finance.index]
        if missing:
            st.error(f"⚠️ {txt['err_file']} Missing rows: {', '.join(missing)}")
            st.stop()
        
        col_24, col_25 = df_finance.columns[0], df_finance.columns[1]
        
        df_display = df_finance.copy()
        df_display[col_24] = pd.to_numeric(df_display[col_24], errors='coerce') * rate
        df_display[col_25] = pd.to_numeric(df_display[col_25], errors='coerce') * rate
        df_display['YoY Growth (%)'] = ((df_display[col_25] - df_display[col_24]) / df_display[col_24]) * 100
        
        def color_variance(row):
            item = str(row.name).lower()
            val = row['YoY Growth (%)']
            if pd.isna(val): return [''] * len(row)
            if ('liability' in item or 'debt' in item) and val > 0: color = '#d62728'
            elif val > 0: color = '#2ca02c'
            else: color = '#d62728'
            return [f'color: {color}' if col == 'YoY Growth (%)' else '' for col in row.index]

        left_col, right_col = st.columns([1.5, 1], gap="large")
        
        with left_col:
            st.subheader(txt["var_title"])
            st.dataframe(df_display.style.apply(color_variance, axis=1).format({col_24: f"{{:,.0f}} {sym}", col_25: f"{{:,.0f}} {sym}", 'YoY Growth (%)': "{:.2f}%"}), use_container_width=True)

            rev_24, rev_25 = float(df_display.loc["Revenue", col_24]), float(df_display.loc["Revenue", col_25])
            net_24, net_25 = float(df_display.loc["Net Income", col_24]), float(df_display.loc["Net Income", col_25])
            ca_25, cl_25 = float(df_display.loc["Current Assets", col_25]), float(df_display.loc["Current Liabilities", col_25])
            eq_25 = float(df_display.loc["Total Equity", col_25])
            
            user_net_margin = (net_25 / rev_25) * 100 if rev_25 > 0 else 0
            user_roe = (net_25 / eq_25) * 100 if eq_25 > 0 else 0
            current_ratio = ca_25 / cl_25 if cl_25 > 0 else 0

        with right_col:
            st.subheader(txt["sens_title"])
            sim_rev_exact = st.number_input(txt["rev_growth"], -30, 30, 0, step=1)
            sim_cost_exact = st.number_input(txt["cost_red"], 0, 30, 0, step=1)
            
            sim_rev = rev_25 * (1 + (sim_rev_exact/100))
            sim_costs = (rev_25 - net_25) * (1 - (sim_cost_exact/100))
            sim_net = sim_rev - sim_costs
            sim_margin = (sim_net / sim_rev * 100) if sim_rev > 0 else 0
            
            st.markdown(f"""
            <div class="metric-box">
                <p style="margin:0; color:#b3b3b3; font-size:14px;">{txt['sim_rev']} ({sym})</p>
                <h3 style="margin:0; color:#2ca02c;">{sim_rev:,.2f}</h3>
            </div>
            <div class="metric-box">
                <p style="margin:0; color:#b3b3b3; font-size:14px;">{txt['sim_margin']}</p>
                <h3 style="margin:0; color:#1f77b4;">{sim_margin:.2f}%</h3>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # 1. SENSITIVITY HEATMAP (FIXED MATH & COLOR SCALE)
        st.subheader("📊 Sensitivity Heatmap (WACC vs Growth)")
        import numpy as np
        
        # Ranges adjusted so WACC is ALWAYS strictly greater than Terminal Growth
        wacc_range = np.linspace(0.06, 0.15, 10)  # 6% to 15%
        growth_range = np.linspace(0.01, 0.05, 10) # 1% to 5%
        
        z_data = [[(rev_25 * 0.15) / (w - g) for g in growth_range] for w in wacc_range]
        
        # Native smooth color scale 'RdYlGn' (Red to Yellow to Green)
        fig_heat = go.Figure(data=go.Heatmap(
            z=z_data, 
            x=np.round(growth_range*100, 1), 
            y=np.round(wacc_range*100, 1), 
            colorscale='RdYlGn', 
            colorbar=dict(title=f"EV ({sym})"),
            hovertemplate="Growth: %{x}%<br>WACC: %{y}%<br>EV: %{z:,.0f} " + sym + "<extra></extra>"
        ))
        
        fig_heat.update_layout(
            title="Enterprise Value Sensitivity Matrix", 
            xaxis_title="Terminal Growth %", 
            yaxis_title="WACC %", 
            template="plotly_dark", 
            height=450
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("---")
        
        st.subheader(txt["kpi_title"])
        cr1, cr2, cr3 = st.columns(3)
        cr1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=current_ratio, title={'text': txt['cr']}, gauge={'axis': {'range': [0, 3]}, 'bar': {'color': "#2ca02c"}})).update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark"), use_container_width=True)
        cr2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=user_net_margin, number={'suffix': "%"}, title={'text': txt['nm']}, gauge={'axis': {'range': [0, 30]}, 'bar': {'color': "#1f77b4"}})).update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark"), use_container_width=True)
        cr3.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=user_roe, number={'suffix': "%"}, title={'text': txt['roe']}, gauge={'axis': {'range': [0, 40]}, 'bar': {'color': "#9467bd"}})).update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark"), use_container_width=True)

        st.markdown("---")

        col_diag, col_chart = st.columns([1, 1], gap="large")
        with col_diag:
            st.subheader(txt["diag_title"])
            score_positif = sum([current_ratio >= 1.2, user_net_margin >= 8.0, user_roe >= 12.0])
            if score_positif >= 2:
                color, status = "#2ca02c", txt["fav"]
                selected_nbs = [txt["fav_n1"], txt["fav_n2"], txt["fav_n3"]]
                pdf_notes = [pdf_txt["fav_n1"], pdf_txt["fav_n2"], pdf_txt["fav_n3"]]
            else:
                color, status = "#d62728", txt["crit"]
                selected_nbs = [txt["crit_n1"], txt["crit_n2"], txt["crit_n3"]]
                pdf_notes = [pdf_txt["crit_n1"], pdf_txt["crit_n2"], pdf_txt["crit_n3"]]
                
            st.markdown(f"""
            <div class="report-box" style="border-color: {color};">
                <h4 style="color: {color}; margin-top: 0;">{status}</h4>
                <ul style="padding-inline-start: 20px;">
                    <li style="color: #b3b3b3;">{selected_nbs[0]}</li>
                    <li style="color: #b3b3b3;">{selected_nbs[1]}</li>
                    <li style="color: #b3b3b3;">{selected_nbs[2]}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col_chart:
            st.subheader(txt["yoy_title"])
            fig_yoy = go.Figure()
            fig_yoy.add_trace(go.Bar(x=['2024', '2025'], y=[rev_24, rev_25], name=txt['rev'], marker_color='#1f77b4'))
            fig_yoy.add_trace(go.Bar(x=['2024', '2025'], y=[net_24, net_25], name=txt['net'], marker_color='#2ca02c'))
            fig_yoy.update_layout(barmode='group', template="plotly_dark", height=250, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_yoy, use_container_width=True)

        st.markdown("---")
        st.subheader(txt["act_title"])
        
        c_action1, c_action2 = st.columns(2)
        
        with c_action1:
            if st.button(txt["save"], use_container_width=True):
                # GUEST MODE LOCK
                if hasattr(st.session_state.user, 'email') and st.session_state.user.email == 'guest@portfolio.com':
                    guest_warnings = {
                        "English": "🔒 Sign up for a free account to save your analysis history!",
                        "Français": "🔒 Créez un compte gratuit pour sauvegarder votre historique d'analyse !",
                        "Español": "🔒 ¡Regístrate gratis para guardar tu historial de análisis!",
                        "العربية": "🔒 قم بإنشاء حساب مجاني لحفظ سجل تحليلاتك!"
                    }
                    st.warning(guest_warnings.get(lang, guest_warnings["English"]))
                else:
                    session_data = {
                        "Session_Name": f"Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                        "Revenue": rev_25, 
                        "Net Margin": round(user_net_margin, 2), 
                        "ROE": round(user_roe, 2), 
                        "Current Ratio": round(current_ratio, 2), 
                        "Date": datetime.now().strftime('%Y-%m-%d %H:%M')
                    }
                    if save_history(st.session_state.user.id, st.session_state.user.email, session_data): st.success(txt["success_save"])
                    else: st.error(txt["fail_save"])
                    
        with c_action2:
            pdf_bytes = create_rich_pdf(df_display, user_net_margin, user_roe, current_ratio, sim_rev, sim_margin, pdf_notes, pdf_txt, sym)
            st.download_button(
                label=txt["dl_pdf"],
                data=pdf_bytes,
                file_name="Detailed_Financial_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
            
            # --- PROFESSIONAL EXCEL EXPORT (ENCADRE) ---
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
                df_display.to_excel(writer, sheet_name="Financial_Dashboard")
                workbook = writer.book
                worksheet = writer.sheets["Financial_Dashboard"]
                
                # Formats
                header_format = workbook.add_format({'bold': True, 'bg_color': '#c1272d', 'font_color': 'white', 'border': 1})
                cell_format = workbook.add_format({'border': 1})
                
                # Apply Header Format to Table 1
                for col_num, value in enumerate(["Line Item"] + list(df_display.columns)):
                    worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column(col_num, col_num, 20)
                
                # Apply Borders to Table 1 Data Cells
                for row_num, (index_val, row_data) in enumerate(df_display.iterrows(), start=1):
                    worksheet.write(row_num, 0, str(index_val), cell_format)
                    for col_num, val in enumerate(row_data, start=1):
                        if pd.isna(val):
                            worksheet.write_blank(row_num, col_num, "", cell_format)
                        else:
                            worksheet.write(row_num, col_num, val, cell_format)
                
                # Table 2: KPIs (Encadre)
                kpi_start_row = len(df_display) + 4
                worksheet.write(kpi_start_row, 0, "Key Performance Indicators", header_format)
                worksheet.write(kpi_start_row, 1, "", header_format) # Fill header border
                
                worksheet.write(kpi_start_row + 1, 0, txt["nm"], cell_format)
                worksheet.write(kpi_start_row + 1, 1, f"{user_net_margin:.2f}%", cell_format)
                worksheet.write(kpi_start_row + 2, 0, txt["roe"], cell_format)
                worksheet.write(kpi_start_row + 2, 1, f"{user_roe:.2f}%", cell_format)
                worksheet.write(kpi_start_row + 3, 0, txt["cr"], cell_format)
                worksheet.write(kpi_start_row + 3, 1, f"{current_ratio:.2f}x", cell_format)
                
                # Diagnosis Notes
                diag_start_row = kpi_start_row + 6
                worksheet.write(diag_start_row, 0, "Expert Diagnosis", header_format)
                for i, note in enumerate(selected_nbs):
                    worksheet.write(diag_start_row + 1 + i, 0, note)
                
                # --- NATIVE EXCEL CHART ---
                chart = workbook.add_chart({'type': 'column'})
                chart.add_series({
                    'name': str(col_24),
                    'categories': '=Financial_Dashboard!$A$2:$A$3',
                    'values': '=Financial_Dashboard!$B$2:$B$3',
                    'fill': {'color': '#1f77b4'}
                })
                chart.add_series({
                    'name': str(col_25),
                    'categories': '=Financial_Dashboard!$A$2:$A$3',
                    'values': '=Financial_Dashboard!$C$2:$C$3',
                    'fill': {'color': '#2ca02c'}
                })
                chart.set_title({'name': 'Revenue vs Net Income (YoY)'})
                chart.set_y_axis({'name': f'Value ({sym})'})
                
                # Insert chart far away from the tables to keep it clean
                worksheet.insert_chart('E2', chart)
                
            st.download_button(
                label=txt["dl_xlsx"],
                data=output_excel.getvalue(),
                file_name="Detailed_Analysis_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
            
    except Exception as e:
        st.error(f"{txt['err_file']} {str(e)}")
