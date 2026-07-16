import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import json
from datetime import datetime
from fpdf import FPDF
from supabase import create_client, ClientOptions

# --- SECURITY & STATE ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

lang = st.session_state.get("lang", "English")
curr = st.session_state.get("currency", "MAD")
rates = st.session_state.get("rates", {"MAD": 1.0, "USD": 0.10, "EUR": 0.09})
syms = st.session_state.get("sym", {"MAD": "MAD", "USD": "$", "EUR": "€"})

rate = rates[curr]
sym = syms[curr]

# --- INSTITUTIONAL TRANSLATION DICTIONARY ---
t = {
    "English": {
        "phase": "PHASE 2: VALUATION & ADVISORY",
        "title": "Standalone Valuation Engine",
        "desc": "Upload target historicals. Execute standalone variance analysis and implied DCF sensitivity.",
        "upload": "Upload Target's Financial Statements (Excel Template)", "dl_temp": "📥 Download Standard Template",
        "var_title": "📋 Historical Variance Analysis", "sens_title": "🎛️ Margin & Growth Sensitivity", 
        "rev_growth": "Projected Rev Growth (%)", "cost_red": "Target Cost Synergies (%)",
        "sim_rev": "Simulated Projected Revenue", "sim_margin": "Simulated EBITDA Margin",
        "kpi_title": "📊 Target Operational Health", "cr": "Liquidity Ratio (Current)", "nm": "EBITDA Margin", "roe": "Return on Equity (ROE)",
        "diag_title": "💡 M&A Advisory Verdict", "fav": "Favorable Target Profile", "crit": "High-Risk Target Profile",
        "fav_n1": "Strong short-term solvency and liquidity buffer.", "fav_n2": "Operational margins indicate strong pricing power.", "fav_n3": "Shareholder value creation verified (Attractive ROE).",
        "crit_n1": "Liquidity distress: High risk of working capital deficit.", "crit_n2": "Margin compression: Target operates below sector efficiency.", "crit_n3": "Sub-optimal capital structure or poor asset utilization.",
        "yoy_title": "📈 Target Earnings Trajectory (YoY)", "rev": "Top-line Revenue", "net": "Bottom-line Net Income",
        "act_title": "💾 Deal Room Actions & Export", "save": "💾 Log to Deal History", "dl_pdf": "📄 Generate Advisory Pitchbook (PDF)", "dl_xlsx": "📥 Export Databook (Excel)",
        "success_save": "✅ Target data logged successfully!", "fail_save": "⚠️ Transaction log failed.", "err_file": "⚠️ Model parsing error. Ensure strict adherence to the template format.",
        # PDF specific
        "pdf_head": "M&A ADVISORY: STANDALONE VALUATION REPORT", "pdf_gen": "Generated", "pdf_s1": "1. Historical Financials & Variance",
        "pdf_col1": "Line Item", "pdf_col2": "YoY Var (%)", "pdf_s2": "2. Target Operational KPIs",
        "pdf_s3": "3. Pro-Forma Sensitivity Outlook", "pdf_sim_rev": "- Implied Forward Revenue:", "pdf_sim_mar": "- Implied Forward Margin:",
        "pdf_s4": "4. Strategic Advisory Verdict", "pdf_foot": "Strictly Confidential | M&A Advisory Desk - Z.ELAIDI Financial Hub"
    },
    "Français": {
        "phase": "PHASE 2: VALORISATION & CONSEIL",
        "title": "Moteur de Valorisation Indépendante",
        "desc": "Importez l'historique de la cible. Exécutez l'analyse des écarts et la sensibilité DCF.",
        "upload": "Importez les États Financiers de la Cible (Modèle Excel)", "dl_temp": "📥 Télécharger le Modèle Standard",
        "var_title": "📋 Analyse Historique des Écarts", "sens_title": "🎛️ Sensibilité (Croissance & Marges)", 
        "rev_growth": "Croissance Projetée (%)", "cost_red": "Synergies de Coûts (%)",
        "sim_rev": "Revenus Projetés Simulés", "sim_margin": "Marge EBITDA Simulée",
        "kpi_title": "📊 Santé Opérationnelle de la Cible", "cr": "Ratio de Liquidité", "nm": "Marge EBITDA", "roe": "Rentabilité des Capitaux (ROE)",
        "diag_title": "💡 Verdict Conseil M&A", "fav": "Profil de Cible Favorable", "crit": "Profil de Cible à Haut Risque",
        "fav_n1": "Forte solvabilité à court terme et réserve de liquidité.", "fav_n2": "Marges opérationnelles indiquant un fort pouvoir de fixation des prix.", "fav_n3": "Création de valeur vérifiée pour les actionnaires (ROE).",
        "crit_n1": "Détresse de liquidité : Risque élevé de déficit en fonds de roulement.", "crit_n2": "Compression des marges : La cible opère sous l'efficacité du secteur.", "crit_n3": "Structure de capital sous-optimale ou faible rotation des actifs.",
        "yoy_title": "📈 Trajectoire des Bénéfices (Annuel)", "rev": "Chiffre d'Affaires", "net": "Résultat Net",
        "act_title": "💾 Actions Data Room & Export", "save": "💾 Enregistrer dans l'Historique", "dl_pdf": "📄 Générer Pitchbook Conseil (PDF)", "dl_xlsx": "📥 Exporter Databook (Excel)",
        "success_save": "✅ Données enregistrées avec succès !", "fail_save": "⚠️ Échec de l'enregistrement.", "err_file": "⚠️ Erreur de parsing. Assurez-vous du respect strict du modèle.",
        # PDF specific
        "pdf_head": "CONSEIL M&A : RAPPORT DE VALORISATION", "pdf_gen": "Généré le", "pdf_s1": "1. Historique Financier et Écarts",
        "pdf_col1": "Poste", "pdf_col2": "Var Annuelle (%)", "pdf_s2": "2. KPIs Opérationnels de la Cible",
        "pdf_s3": "3. Perspectives de Sensibilité Pro-Forma", "pdf_sim_rev": "- Revenus Futurs Implicites :", "pdf_sim_mar": "- Marge Future Implicite :",
        "pdf_s4": "4. Verdict de Conseil Stratégique", "pdf_foot": "Strictement Confidentiel | Bureau de Conseil M&A - Z.ELAIDI Financial Hub"
    },
    "Español": {
        "phase": "FASE 2: VALORACIÓN Y ASESORÍA",
        "title": "Motor de Valoración Independiente",
        "desc": "Sube el historial del objetivo. Ejecuta análisis de varianza y sensibilidad DCF implícita.",
        "upload": "Sube los Estados Financieros del Objetivo (Plantilla Excel)", "dl_temp": "📥 Descargar Plantilla Estándar",
        "var_title": "📋 Análisis Histórico de Variaciones", "sens_title": "🎛️ Sensibilidad (Crecimiento y Márgenes)", 
        "rev_growth": "Crecimiento Proyectado (%)", "cost_red": "Sinergias de Costos (%)",
        "sim_rev": "Ingresos Proyectados Simulados", "sim_margin": "Margen EBITDA Simulado",
        "kpi_title": "📊 Salud Operativa del Objetivo", "cr": "Ratio de Liquidez", "nm": "Margen EBITDA", "roe": "Retorno sobre el Capital (ROE)",
        "diag_title": "💡 Veredicto de Asesoría M&A", "fav": "Perfil de Objetivo Favorable", "crit": "Perfil de Objetivo de Alto Riesgo",
        "fav_n1": "Fuerte solvencia a corto plazo y reserva de liquidez.", "fav_n2": "Márgenes operativos indican un fuerte poder de fijación de precios.", "fav_n3": "Creación de valor verificada para los accionistas (ROE).",
        "crit_n1": "Problemas de liquidez: Alto riesgo de déficit de capital de trabajo.", "crit_n2": "Compresión de márgenes: El objetivo opera por debajo de la eficiencia del sector.", "crit_n3": "Estructura de capital subóptima.",
        "yoy_title": "📈 Trayectoria de Ganancias (Anual)", "rev": "Ingresos Totales", "net": "Ingreso Neto",
        "act_title": "💾 Acciones y Exportación", "save": "💾 Registrar en Historial", "dl_pdf": "📄 Generar Pitchbook (PDF)", "dl_xlsx": "📥 Exportar Databook (Excel)",
        "success_save": "✅ ¡Datos registrados exitosamente!", "fail_save": "⚠️ Error al registrar.", "err_file": "⚠️ Error de lectura. Asegure el cumplimiento estricto de la plantilla.",
        # PDF specific
        "pdf_head": "ASESORÍA M&A: INFORME DE VALORACIÓN", "pdf_gen": "Generado", "pdf_s1": "1. Finanzas Históricas y Varianza",
        "pdf_col1": "Partida", "pdf_col2": "Var Anual (%)", "pdf_s2": "2. KPIs Operativos del Objetivo",
        "pdf_s3": "3. Perspectivas de Sensibilidad", "pdf_sim_rev": "- Ingresos Implícitos Futuros:", "pdf_sim_mar": "- Margen Implícito Futuro:",
        "pdf_s4": "4. Veredicto Estratégico", "pdf_foot": "Estrictamente Confidencial | Asesoría M&A - Z.ELAIDI Financial Hub"
    },
    "العربية": {
        "phase": "المرحلة الثانية: التقييم والاستشارات",
        "title": "محرك التقييم المالي المستقل",
        "desc": "رفع البيانات التاريخية للشركة المستهدفة. تنفيذ تحليل التغيرات وحساسية التدفقات النقدية المخصومة.",
        "upload": "قم برفع البيانات المالية للشركة المستهدفة (نموذج الإكسل)", "dl_temp": "📥 تنزيل النموذج القياسي",
        "var_title": "📋 تحليل التغيرات التاريخية", "sens_title": "🎛️ حساسية النمو والهوامش", 
        "rev_growth": "نمو الإيرادات المتوقع (%)", "cost_red": "تآزر التكاليف المستهدف (%)",
        "sim_rev": "الإيرادات المستقبلية المحاكية", "sim_margin": "هامش الأرباح (EBITDA) المحاكى",
        "kpi_title": "📊 الصحة التشغيلية للشركة المستهدفة", "cr": "نسبة السيولة المتداولة", "nm": "هامش الأرباح التشغيلية", "roe": "العائد على حقوق المساهمين",
        "diag_title": "💡 حكم استشاري لعملية الاستحواذ", "fav": "ملف الشركة المستهدفة: إيجابي", "crit": "ملف الشركة المستهدفة: عالي المخاطر",
        "fav_n1": "ملاءة مالية قوية واحتياطي سيولة ممتاز على المدى القصير.", "fav_n2": "هوامش التشغيل تؤكد قدرة قوية على التسعير التنافسي.", "fav_n3": "تم التحقق من خلق القيمة للمساهمين (عائد جذاب).",
        "crit_n1": "ضائقة سيولة: خطر كبير بحدوث عجز في رأس المال العامل.", "crit_n2": "تآكل الهوامش: تعمل الشركة بكفاءة أقل من متوسط القطاع.", "crit_n3": "هيكل رأس مال غير مثالي أو ضعف في استغلال الأصول.",
        "yoy_title": "📈 مسار أرباح الشركة المستهدفة (سنوياً)", "rev": "إجمالي الإيرادات", "net": "صافي الدخل",
        "act_title": "💾 إجراءات التصدير والحفظ", "save": "💾 تسجيل الصفقة في السجل", "dl_pdf": "📄 استخراج تقرير الاستشارات (PDF)", "dl_xlsx": "📥 تصدير البيانات التفصيلية (Excel)",
        "success_save": "✅ تم حفظ بيانات الشركة المستهدفة بنجاح!", "fail_save": "⚠️ فشل في تسجيل البيانات.", "err_file": "⚠️ خطأ في قراءة النموذج. تأكد من الالتزام التام بالصيغة.",
        # PDF specific
        "pdf_head": "استشارات الاستحواذ: تقرير التقييم المستقل", "pdf_gen": "تم الإنشاء في", "pdf_s1": "1. البيانات المالية التاريخية والتغيرات",
        "pdf_col1": "البند المالي", "pdf_col2": "التغير السنوي (%)", "pdf_s2": "2. مؤشرات الأداء التشغيلي للهدف",
        "pdf_s3": "3. التوقعات المالية والحساسية", "pdf_sim_rev": "- الإيرادات المستقبلية الضمنية:", "pdf_sim_mar": "- هامش الربح المستقبلي الضمني:",
        "pdf_s4": "4. التوصية الاستراتيجية", "pdf_foot": "سري للغاية | قسم استشارات الاندماج والاستحواذ - منصة ز. العيدي"
    }
}

txt = t[lang]
pdf_lang = lang if lang != "العربية" else "English"
pdf_txt = t[pdf_lang]

# --- ADVANCED CSS INJECTION (Spacing & Phase 2 Green Theme) ---
rtl_css = """
.block-container { direction: rtl; text-align: right; }
[data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"], [data-testid="stHeader"] { direction: ltr !important; text-align: left !important; }
""" if lang == "العربية" else ""

st.markdown(f"""
<style>
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    
    /* OVERRIDING MAX-WIDTH TO FILL EMPTY SPACE */
    .block-container {{ 
        animation: fadeIn 0.5s ease-out; 
        overflow-x: hidden; 
        max-width: 100% !important; 
        padding-top: 2rem !important; 
        padding-bottom: 5rem !important; 
        padding-left: 3rem !important; 
        padding-right: 3rem !important; 
    }}
    
    /* Institutional Header - Phase 2 Theme (Green) */
    .inst-header {{ background: linear-gradient(145deg, #0e1117, #161b22); border-left: 4px solid #2ca02c; padding: 30px 40px; border-radius: 8px; margin-bottom: 40px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
    .inst-phase {{ color: #2ca02c; font-size: 0.9rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; display: block; }}
    .inst-title {{ color: #ffffff; font-size: 2.5rem; font-weight: 700; margin: 0; padding: 0; letter-spacing: -0.5px; }}
    .inst-desc {{ color: #8b949e; font-size: 1.1rem; margin-top: 10px; }}
    
    /* Box Spacing */
    .metric-box {{ background-color: rgba(30, 34, 43, 0.5); padding: 25px; border-radius: 8px; border-top: 4px solid #2ca02c; margin-bottom: 20px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}
    .report-box {{ padding: 25px; border-radius: 8px; background-color: rgba(30, 34, 43, 0.5); border-left: 5px solid; margin-top: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}
    
    /* Input Container Padding */
    div[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 8px !important; background: rgba(22,26,34,0.4); padding: 2rem !important; margin-bottom: 2.5rem !important; }}
    
    [data-testid="stSidebarNav"] li:first-child a span {{ display: none !important; }}
    [data-testid="stSidebarNav"] li:first-child a::after {{ content: "🏠 Home"; font-size: 15px; margin-left: 0px; }}
    
    {rtl_css}
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown(f"""
<div class="inst-header" {'dir="rtl"' if lang=="العربية" else ''}>
    <span class="inst-phase">{txt['phase']}</span>
    <h1 class="inst-title">{txt['title']}</h1>
    <p class="inst-desc">{txt['desc']}</p>
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

# --- RICH DETAILED PDF GENERATOR (Green Theme) ---
def create_rich_pdf(df_display, net_margin, roe, current_ratio, sim_rev, sim_margin, diagnosis, p_txt, p_sym):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    # Phase 2 Green Banner
    pdf.set_fill_color(44, 160, 44) 
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_y(12)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, p_txt["pdf_head"].encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
    pdf.set_font("Arial", '', 10)
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

# --- UPLOAD SECTION ---
with st.container(border=True):
    c1, c2 = st.columns([3, 1], vertical_alignment="center")
    with c1: 
        st.markdown(f"**{txt['upload']}**")
    with c2: 
        st.download_button(txt["dl_temp"], data=generate_template(), file_name="Target_Template.xlsx", use_container_width=True)

    uploaded_file = st.file_uploader("", type=["xlsx"], label_visibility="collapsed")

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

        st.markdown("<br>", unsafe_allow_html=True)
        
        # ROW 1: Variance & Sensitivity
        left_col, right_col = st.columns([1.5, 1], gap="large")
        
        with left_col:
            st.subheader(txt["var_title"])
            st.dataframe(df_display.style.apply(color_variance, axis=1).format({col_24: f"{{:,.0f}} {sym}", col_25: f"{{:,.0f}} {sym}", 'YoY Growth (%)': "{:.2f}%"}), use_container_width=True, height=350)

            rev_24, rev_25 = float(df_display.loc["Revenue", col_24]), float(df_display.loc["Revenue", col_25])
            net_24, net_25 = float(df_display.loc["Net Income", col_24]), float(df_display.loc["Net Income", col_25])
            ca_25, cl_25 = float(df_display.loc["Current Assets", col_25]), float(df_display.loc["Current Liabilities", col_25])
            eq_25 = float(df_display.loc["Total Equity", col_25])
            
            user_net_margin = (net_25 / rev_25) * 100 if rev_25 > 0 else 0
            user_roe = (net_25 / eq_25) * 100 if eq_25 > 0 else 0
            current_ratio = ca_25 / cl_25 if cl_25 > 0 else 0

        with right_col:
            st.subheader(txt["sens_title"])
            with st.container(border=True):
                sim_rev_exact = st.number_input(txt["rev_growth"], -30, 30, 5, step=1)
                sim_cost_exact = st.number_input(txt["cost_red"], 0, 30, 2, step=1)
            
            sim_rev = rev_25 * (1 + (sim_rev_exact/100))
            sim_costs = (rev_25 - net_25) * (1 - (sim_cost_exact/100))
            sim_net = sim_rev - sim_costs
            sim_margin = (sim_net / sim_rev * 100) if sim_rev > 0 else 0
            
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown(f"""
                <div class="metric-box">
                    <p style="margin:0; color:#8b949e; font-size:0.85rem; text-transform:uppercase;">{txt['sim_rev']}</p>
                    <h3 style="margin:0; color:#2ca02c; font-size: 1.8rem;">{sim_rev:,.0f} <span style="font-size:1rem;">{sym}</span></h3>
                </div>
                """, unsafe_allow_html=True)
            with sc2:
                st.markdown(f"""
                <div class="metric-box">
                    <p style="margin:0; color:#8b949e; font-size:0.85rem; text-transform:uppercase;">{txt['sim_margin']}</p>
                    <h3 style="margin:0; color:#1f77b4; font-size: 1.8rem;">{sim_margin:.2f}%</h3>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        
        # ROW 2: Heatmap & Charts
        col_heat, col_kpi = st.columns([1.2, 1], gap="large")
        
        with col_heat:
            st.subheader("📊 Implied Enterprise Value Matrix")
            import numpy as np
            
            wacc_range = np.linspace(0.06, 0.15, 10)  # 6% to 15%
            growth_range = np.linspace(0.01, 0.05, 10) # 1% to 5%
            
            z_data = [[(rev_25 * 0.15) / (w - g) for g in growth_range] for w in wacc_range]
            
            fig_heat = go.Figure(data=go.Heatmap(
                z=z_data, 
                x=np.round(growth_range*100, 1), 
                y=np.round(wacc_range*100, 1), 
                colorscale='RdYlGn', 
                colorbar=dict(title=f"EV ({sym})"),
                hovertemplate="Growth: %{x}%<br>WACC: %{y}%<br>Implied EV: %{z:,.0f} " + sym + "<extra></extra>"
            ))
            
            fig_heat.update_layout(
                xaxis_title="Terminal Growth Rate (g) %", 
                yaxis_title="Weighted Avg Cost of Capital (WACC) %", 
                template="plotly_dark", 
                height=450,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_heat, use_container_width=True)

        with col_kpi:
            st.subheader(txt["yoy_title"])
            fig_yoy = go.Figure()
            fig_yoy.add_trace(go.Bar(x=['2024', '2025'], y=[rev_24, rev_25], name=txt['rev'], marker_color='#1f77b4'))
            fig_yoy.add_trace(go.Bar(x=['2024', '2025'], y=[net_24, net_25], name=txt['net'], marker_color='#2ca02c'))
            fig_yoy.update_layout(barmode='group', template="plotly_dark", height=450, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_yoy, use_container_width=True)

        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        
        # ROW 3: KPIs & Diagnosis
        st.subheader(txt["kpi_title"])
        cr1, cr2, cr3 = st.columns(3, gap="large")
        cr1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=current_ratio, title={'text': txt['cr']}, gauge={'axis': {'range': [0, 3]}, 'bar': {'color': "#2ca02c"}})).update_layout(height=220, margin=dict(l=20, r=20, t=40, b=20), template="plotly_dark"), use_container_width=True)
        cr2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=user_net_margin, number={'suffix': "%"}, title={'text': txt['nm']}, gauge={'axis': {'range': [0, 30]}, 'bar': {'color': "#1f77b4"}})).update_layout(height=220, margin=dict(l=20, r=20, t=40, b=20), template="plotly_dark"), use_container_width=True)
        cr3.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=user_roe, number={'suffix': "%"}, title={'text': txt['roe']}, gauge={'axis': {'range': [0, 40]}, 'bar': {'color': "#9467bd"}})).update_layout(height=220, margin=dict(l=20, r=20, t=40, b=20), template="plotly_dark"), use_container_width=True)

        col_diag, col_export = st.columns([1.5, 1], gap="large")
        
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
            <div class="report-box" style="border-left-color: {color};">
                <h4 style="color: {color}; margin-top: 0; font-size: 1.4rem;">{status}</h4>
                <ul style="padding-inline-start: 20px; margin-bottom: 0;">
                    <li style="color: #b3b3b3; font-size: 1.1rem; margin-bottom: 8px;">{selected_nbs[0]}</li>
                    <li style="color: #b3b3b3; font-size: 1.1rem; margin-bottom: 8px;">{selected_nbs[1]}</li>
                    <li style="color: #b3b3b3; font-size: 1.1rem;">{selected_nbs[2]}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col_export:
            st.subheader(txt["act_title"])
            with st.container(border=True):
                if st.button(txt["save"], use_container_width=True):
                    if hasattr(st.session_state.user, 'email') and st.session_state.user.email == 'guest@portfolio.com':
                        st.warning("🔒 Sign up for a free account to save your analysis history!")
                    else:
                        session_data = {
                            "Session_Name": f"Target Val - {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                            "Revenue": rev_25, "Net Margin": round(user_net_margin, 2), "ROE": round(user_roe, 2), 
                            "Current Ratio": round(current_ratio, 2), "Date": datetime.now().strftime('%Y-%m-%d %H:%M')
                        }
                        if save_history(st.session_state.user.id, st.session_state.user.email, session_data): st.success(txt["success_save"])
                        else: st.error(txt["fail_save"])
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                pdf_bytes = create_rich_pdf(df_display, user_net_margin, user_roe, current_ratio, sim_rev, sim_margin, pdf_notes, pdf_txt, sym)
                st.download_button(label=txt["dl_pdf"], data=pdf_bytes, file_name="MA_Advisory_Report.pdf", mime="application/pdf", use_container_width=True, type="primary")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                output_excel = io.BytesIO()
                with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
                    df_display.to_excel(writer, sheet_name="Target_Databook")
                    workbook = writer.book
                    worksheet = writer.sheets["Target_Databook"]
                    header_format = workbook.add_format({'bold': True, 'bg_color': '#2ca02c', 'font_color': 'white', 'border': 1})
                    cell_format = workbook.add_format({'border': 1})
                    
                    for col_num, value in enumerate(["Line Item"] + list(df_display.columns)):
                        worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(col_num, col_num, 20)
                    
                    for row_num, (index_val, row_data) in enumerate(df_display.iterrows(), start=1):
                        worksheet.write(row_num, 0, str(index_val), cell_format)
                        for col_num, val in enumerate(row_data, start=1):
                            if pd.isna(val): worksheet.write_blank(row_num, col_num, "", cell_format)
                            else: worksheet.write(row_num, col_num, val, cell_format)
                
                st.download_button(label=txt["dl_xlsx"], data=output_excel.getvalue(), file_name="Target_Databook.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                
    except Exception as e:
        st.error(f"{txt['err_file']} {str(e)}")
