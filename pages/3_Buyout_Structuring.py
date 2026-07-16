import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import io
import random
from datetime import datetime

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
        "phase": "PHASE 3: BUYOUT STRUCTURING & RISK",
        "title": "Private Equity Deal Room",
        "desc": "Execute Leveraged Buyout scenarios, advanced cost of capital, and Monte Carlo risk simulations.",
        "glos_title": "ℹ️ Glossary & Advanced Definitions",
        "glos_mc": "- **Monte Carlo Simulation:** A computational algorithm that relies on repeated random sampling to understand the impact of risk and uncertainty in the valuation.",
        "glos_moic": "- **MoIC (Multiple on Invested Capital):** Shows how much value an investment has generated (Exit Equity / Entry Equity).",
        "sb_title": "🏢 Target Base Financials", "sb_info": "Input the target company's base financials here (in MAD).",
        "b_rev": "Base Revenue (MAD)", "b_ebitda": "Base EBITDA (MAD)",
        "capm_title": "⚙️ Advanced WACC Calculator",
        "capm_def": "**Capital Asset Pricing Model (CAPM):** The CAPM is a financial model used to calculate the expected Return on Equity ($K_e$). It establishes a linear relationship between the required return of an investment and its systematic risk ($\\beta$).\n\n**Formula:** $K_e = R_f + \\beta \\times (R_m - R_f)$",
        "rf": "Risk-Free Rate (%)", "rm": "Market Return (%)", "beta": "Beta (β)", "tax": "Tax Rate (%)", "kd": "Cost of Debt (%)", "w_debt": "Debt Weighting (%)",
        "ke_res": "Cost of Equity (Ke)", "kd_res": "Cost of Debt post-tax (Kd)", "wacc_res": "Implied WACC",
        "capm_toggle": "Enable CAPM Calculation Mode", "wacc_slider": "WACC %",
        "dcf_title": "📊 Standard DCF Engine",
        "tg": "Terminal Growth %", "pg": "Projected Growth %", "fcfm": "FCF Margin %", "ev": "Implied Enterprise Value (EV)",
        "mc_btn": "🎲 Run Monte Carlo Simulation (10k Iterations)", "mc_run": "Running 10,000 simulations...",
        "mc_chart": "Enterprise Value Probability Distribution", "freq": "Frequency", "ci": "75% Confidence Interval",
        "lbo_title": "💰 LBO Structuring Engine",
        "entry_m": "Entry Multiple (x)", "exit_m": "Exit Multiple (x)", "debt_f": "Debt Funding %", "int_rate": "Blended Interest (%)",
        "pe_metrics": "Private Equity Returns (5-Year)", "irr": "IRR", "moic": "MoIC",
        "sens_hm": "📊 EV Sensitivity (WACC vs Terminal Growth)", "dl_val_xlsx": "📥 Export Structuring Model (Excel)",
        "sb_tools": "🛠️ Structuring Tools", "fx_title": "🌍 FX Rates (Base MAD)", "calc_title": "🧮 Quick CAGR Calc",
        "pv": "Present Value", "fv": "Future Value", "yrs": "Years", "cagr_res": "CAGR:", 
        "scratch_title": "📝 Deal Notes", "scratch_ph": "Jot down your structuring notes here...",
        "insight": "Structuring Verdict",
        "capm_good_1": "Highly Favorable! The target boasts a low cost of capital. Future cash flows will add significant premium to the investor's portfolio value.",
        "capm_good_2": "Excellent financing structure. The required return on equity is easily beatable, creating an immediate valuation cushion for the buyer.",
        "capm_good_3": "Low systematic risk detected. The cheap capital structure protects the investor's initial layout and boosts enterprise value upside.",
        "capm_bad_1": "Unfavorable structure. The high cost of capital discounts future cash flows aggressively, reducing the final net asset value for the investor.",
        "capm_bad_2": "Caution required: Expensive funding hurdle. Operational growth must accelerate significantly to cover this high required return.",
        "capm_bad_3": "Elevated systematic risk limits upside. The investor faces compressed spreads unless the capital structure is heavily optimized.",
        "lbo_good_1": "Outstanding yield! The projected IRR comfortably beats private equity thresholds. Exceptional value creation for the general partners.",
        "lbo_good_2": "Premium Buyout Opportunity. Rapid debt paydown and operational efficiency guarantee a massive return multiple on invested capital.",
        "lbo_good_3": "Strong operational cushion. The financial structure allows the investor to multiply initial equity stake with limited downside risk.",
        "lbo_bad_1": "Suboptimal return profile. Projected IRR falls short of standard PE benchmarks; entry terms must be completely renegotiated.",
        "lbo_bad_2": "Value Trap Warning: High entry multiples coupled with expensive debt burden are heavily crushing the investor's equity return.",
        "lbo_bad_3": "Weak investor returns detected. Operational leverage is insufficient to generate attractive cash-on-cash multiples at exit."
    },
    "Français": {
        "phase": "PHASE 3: STRUCTURATION BUYOUT & RISQUE",
        "title": "Salle des Marchés Private Equity",
        "desc": "Exécutez des scénarios LBO, le coût du capital avancé et des simulations Monte Carlo.",
        "glos_title": "ℹ️ Glossaire et Définitions",
        "glos_mc": "- **Simulation Monte Carlo :** Algorithme informatique basé sur un échantillonnage aléatoire répété pour évaluer l'impact du risque.",
        "glos_moic": "- **MoIC (Multiple sur le Capital Investi) :** Indique la valeur générée par un investissement.",
        "sb_title": "🏢 Données Financières de Base", "sb_info": "Saisissez les données financières de la cible (en MAD).",
        "b_rev": "Revenus de Base (MAD)", "b_ebitda": "EBITDA de Base (MAD)",
        "capm_title": "⚙️ Calculateur WACC Avancé",
        "capm_def": "**Considérations MEDAF :** Le modèle calcule la rentabilité attendue des capitaux propres ($K_e$).\n\n**Formule :** $K_e = R_f + \\beta \\times (R_m - R_f)$",
        "rf": "Taux Sans Risque (%)", "rm": "Rendement Marché (%)", "beta": "Bêta (β)", "tax": "Taux d'Imposition (%)", "kd": "Coût de la Dette (%)", "w_debt": "Pondération Dette (%)",
        "ke_res": "Coût des Capitaux Propres (Ke)", "kd_res": "Coût de la Dette net (Kd)", "wacc_res": "CMPC Implicite (WACC)",
        "capm_toggle": "Activer le Mode MEDAF", "wacc_slider": "CMPC (WACC) %",
        "dcf_title": "📊 Moteur DCF Standard",
        "tg": "Croissance Terminale %", "pg": "Croissance Projetée %", "fcfm": "Marge FCF %", "ev": "Valeur d'Entreprise (VE)",
        "mc_btn": "🎲 Lancer Simulation Monte Carlo", "mc_run": "Exécution de 10 000 simulations...",
        "mc_chart": "Distribution de Probabilité VE", "freq": "Fréquence", "ci": "Intervalle de Confiance 75%",
        "lbo_title": "💰 Moteur de Structuration LBO",
        "entry_m": "Multiple d'Entrée (x)", "exit_m": "Multiple de Sortie (x)", "debt_f": "Financement Dette %", "int_rate": "Taux d'Intérêt (%)",
        "pe_metrics": "Rendements PE (Horizon 5 ans)", "irr": "TRI (IRR)", "moic": "Multiple (MoIC)",
        "sens_hm": "📊 Sensibilité VE (WACC vs Croissance)", "dl_val_xlsx": "📥 Exporter Modèle de Structuration",
        "sb_tools": "🛠️ Outils de Structuration", "fx_title": "🌍 Taux de Change", "calc_title": "🧮 Calculateur CAGR",
        "pv": "Valeur Actuelle", "fv": "Valeur Future", "yrs": "Années", "cagr_res": "TCAM :", 
        "scratch_title": "📝 Notes de Deal", "scratch_ph": "Prenez vos notes de structuration ici...",
        "insight": "Verdict de Structuration",
        "capm_good_1": "Situation favorable ! Cible avec coût du capital bas.",
        "capm_good_2": "Structure de financement optimale. Taux de rendement surmontable.",
        "capm_good_3": "Faible risque systématique. Coût modéré sécurise l'investissement.",
        "capm_bad_1": "Structure défavorable. Coût du capital élevé pénalisant l'actualisation.",
        "capm_bad_2": "Prudence : Financement lourd. Croissance agressive obligatoire.",
        "capm_bad_3": "Risque élevé. L'investisseur subira des spreads compressés.",
        "lbo_good_1": "Excellent rendement ! Le TRI dépasse les exigences standards.",
        "lbo_good_2": "Opportunité de rachat. Remboursement rapide assure un fort multiple.",
        "lbo_good_3": "Marge de sécurité. Le modèle multiplie le capital avec un risque maîtrisé.",
        "lbo_bad_1": "Rendement insuffisant. Conditions d'entrée à renégocier.",
        "lbo_bad_2": "Piège de valeur : Multiple cher et dette détruisent le ROI.",
        "lbo_bad_3": "Faible performance. Levier opérationnel insuffisant."
    },
    "Español": {
        "phase": "FASE 3: ESTRUCTURACIÓN BUYOUT Y RIESGO",
        "title": "Sala de Capital Privado",
        "desc": "Ejecute escenarios LBO, costo de capital y simulaciones Monte Carlo.",
        "glos_title": "ℹ️ Glosario y Definiciones",
        "glos_mc": "- **Simulación Monte Carlo:** Algoritmo computacional para comprender el impacto del riesgo.",
        "glos_moic": "- **MoIC:** Muestra cuánto valor ha generado una inversión.",
        "sb_title": "🏢 Finanzas Base", "sb_info": "Ingrese las finanzas de la empresa objetivo aquí.",
        "b_rev": "Ingresos Base (MAD)", "b_ebitda": "EBITDA Base (MAD)",
        "capm_title": "⚙️ Calculadora WACC Avanzada",
        "capm_def": "**CAPM:** Modelo para calcular la rentabilidad esperada del capital ($K_e$).\n\n**Fórmula:** $K_e = R_f + \\beta \\times (R_m - R_f)$",
        "rf": "Tasa Libre Riesgo (%)", "rm": "Retorno Mercado (%)", "beta": "Beta (β)", "tax": "Impuesto (%)", "kd": "Costo Deuda (%)", "w_debt": "Deuda (%)",
        "ke_res": "Costo Capital (Ke)", "kd_res": "Costo Deuda Neta (Kd)", "wacc_res": "WACC Implícito",
        "capm_toggle": "Habilitar CAPM", "wacc_slider": "WACC %",
        "dcf_title": "📊 Motor DCF Estándar",
        "tg": "Crecimiento Terminal %", "pg": "Crecimiento Proyectado %", "fcfm": "Margen FCF %", "ev": "Valor Empresarial (EV)",
        "mc_btn": "🎲 Ejecutar Simulación Monte Carlo", "mc_run": "Ejecutando 10,000 simulaciones...",
        "mc_chart": "Distribución Valor Empresarial", "freq": "Frecuencia", "ci": "Intervalo Confianza 75%",
        "lbo_title": "💰 Motor de Estructuración LBO",
        "entry_m": "Múltiplo Entrada (x)", "exit_m": "Múltiplo Salida (x)", "debt_f": "Financiamiento Deuda %", "int_rate": "Tasa de Interés (%)",
        "pe_metrics": "Retornos PE (5 años)", "irr": "TIR (IRR)", "moic": "Múltiplo (MoIC)",
        "sens_hm": "📊 Sensibilidad EV", "dl_val_xlsx": "📥 Exportar Modelo Estructuración",
        "sb_tools": "🛠️ Herramientas", "fx_title": "🌍 Tipos de Cambio", "calc_title": "🧮 Calculadora CAGR",
        "pv": "Valor Presente", "fv": "Valor Futuro", "yrs": "Años", "cagr_res": "CAGR:", 
        "scratch_title": "📝 Notas de Acuerdo", "scratch_ph": "Tome sus notas aquí...",
        "insight": "Veredicto de Estructuración",
        "capm_good_1": "Estructura óptima. Costo de capital bajo.",
        "capm_good_2": "Perfil sólido. El retorno requerido es superable.",
        "capm_good_3": "Bajo riesgo sistemático que protege la inversión.",
        "capm_bad_1": "Estructura desfavorable. Alto costo descuenta flujos.",
        "capm_bad_2": "Precaución: Financiamiento costoso.",
        "capm_bad_3": "Alto riesgo limita valoración. Optimización de deuda requerida.",
        "lbo_good_1": "Rendimiento excelente. La TIR supera expectativas.",
        "lbo_good_2": "Oportunidad de compra. Rápido pago asegura retornos.",
        "lbo_good_3": "Fuerte colchón financiero con bajo riesgo.",
        "lbo_bad_1": "Retornos subóptimos. Renegociar condiciones.",
        "lbo_bad_2": "Trampa de valor: Múltiplos caros destruyen el capital.",
        "lbo_bad_3": "Rendimiento débil. Apalancamiento insuficiente."
    },
    "العربية": {
        "phase": "المرحلة الثالثة: هيكلة الاستحواذ والمخاطر",
        "title": "غرفة صفقات الملكية الخاصة",
        "desc": "تنفيذ سيناريوهات الاستحواذ المدعوم بالقروض (LBO)، حساب تكلفة رأس المال المتقدمة، ومحاكاة مونت كارلو.",
        "glos_title": "ℹ️ مسرد المصطلحات والتعاريف المتقدمة",
        "glos_mc": "- **محاكاة مونت كارلو:** خوارزمية حسابية لفهم تأثير المخاطر في التقييم.",
        "glos_moic": "- **مضاعف رأس المال المستثمر (MoIC):** يوضح مقدار القيمة التي حققها الاستثمار.",
        "sb_title": "🏢 البيانات الأساسية للشركة", "sb_info": "أدخل البيانات المالية للشركة المستهدفة هنا.",
        "b_rev": "الإيرادات الأساسية", "b_ebitda": "الأرباح التشغيلية",
        "capm_title": "⚙️ حاسبة WACC المتقدمة",
        "capm_def": "**نموذج CAPM:** يُستخدم لحساب العائد المتوقع على حقوق الملكية ($K_e$).\n\n**المعادلة:** $K_e = R_f + \\beta \\times (R_m - R_f)$",
        "rf": "المعدل الخالي من المخاطر (%)", "rm": "عائد السوق (%)", "beta": "بيتا (β)", "tax": "الضريبة (%)", "kd": "تكلفة الدين (%)", "w_debt": "وزن الدين (%)",
        "ke_res": "تكلفة حقوق الملكية", "kd_res": "تكلفة الدين الصافية", "wacc_res": "WACC المرجح",
        "capm_toggle": "تمكين وضع CAPM", "wacc_slider": "WACC %",
        "dcf_title": "📊 محرك DCF القياسي",
        "tg": "النمو النهائي %", "pg": "النمو المتوقع %", "fcfm": "هامش التدفق النقدي %", "ev": "القيمة المؤسسية (EV)",
        "mc_btn": "🎲 تشغيل محاكاة مونت كارلو", "mc_run": "تشغيل 10,000 محاكاة...",
        "mc_chart": "التوزيع الاحتمالي للقيمة المؤسسية", "freq": "التردد", "ci": "فترة ثقة 75%",
        "lbo_title": "💰 محرك هيكلة LBO",
        "entry_m": "مضاعف الدخول (x)", "exit_m": "مضاعف التخارج (x)", "debt_f": "نسبة تمويل الديون %", "int_rate": "معدل الفائدة المدمج (%)",
        "pe_metrics": "عوائد الملكية الخاصة (5 سنوات)", "irr": "معدل العائد الداخلي", "moic": "مضاعف رأس المال",
        "sens_hm": "📊 تحليل حساسية القيمة", "dl_val_xlsx": "📥 تصدير نموذج الهيكلة",
        "sb_tools": "🛠️ أدوات الهيكلة", "fx_title": "🌍 أسعار الصرف", "calc_title": "🧮 حاسبة النمو",
        "pv": "القيمة الحالية", "fv": "القيمة المستقبلية", "yrs": "السنوات", "cagr_res": "معدل النمو:", 
        "scratch_title": "📝 مذكرة الصفقة", "scratch_ph": "دون ملاحظات الهيكلة هنا...",
        "insight": "قرار الهيكلة",
        "capm_good_1": "هيكل تمويل مثالي! تكلفة رأس مال منخفضة تضمن قيمة مضافة.",
        "capm_good_2": "ملف استثماري مريح. العائد المطلوب منخفض يحمي أموال المشتري.",
        "capm_good_3": "مخاطر منهجية منخفضة تدعم فرص التقييم التصاعدي.",
        "capm_bad_1": "هيكل غير ملائم. تكلفة رأس المال المرتفعة تلتهم التدفقات.",
        "capm_bad_2": "تحذير: عبء تمويلي باهظ. الشركة ملزمة بتحقيق نمو تشغيلي قوي.",
        "capm_bad_3": "المخاطر المرتفعة تضيق هوامش الربح المتوقعة للمستثمر.",
        "lbo_good_1": "عائد استثنائي! معدل العائد الداخلي يتجاوز متطلبات الصناديق الكبرى.",
        "lbo_good_2": "فرصة استحواذ ممتازة. السداد السريع للديون يضمن تضخيم القيمة.",
        "lbo_good_3": "هامش أمان مالي متميز يتيح مضاعفة رأس المال بمخاطر مسيطر عليها.",
        "lbo_bad_1": "عوائد غير كافية. يجب إعادة التفاوض على شروط الدخول.",
        "lbo_bad_2": "فخ القيمة: مضاعفات مرتفعة مع ديون مكلفة تسحق عوائد المستثمر.",
        "lbo_bad_3": "عوائد ضعيفة بسبب عدم كفاية الرافعات التشغيلية لإنتاج تخارج جذاب."
    }
}
txt = t[lang]

# --- FULL WIDTH CSS INJECTION (Purple Theme) ---
rtl_css = """
.block-container { direction: rtl; text-align: right; }
[data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"], [data-testid="stHeader"] { direction: ltr !important; text-align: left !important; }
""" if lang == "العربية" else ""

st.markdown(f"""
<style>
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    
    .block-container {{ 
        animation: fadeIn 0.5s ease-out; 
        overflow-x: hidden; 
        max-width: 100% !important; 
        padding-top: 2rem !important; 
        padding-bottom: 5rem !important; 
        padding-left: 3rem !important; 
        padding-right: 3rem !important; 
    }}
    
    .inst-header {{ background: linear-gradient(145deg, #0e1117, #161b22); border-left: 4px solid #9467bd; padding: 30px 40px; border-radius: 8px; margin-bottom: 40px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
    .inst-phase {{ color: #9467bd; font-size: 0.9rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; display: block; }}
    .inst-title {{ color: #ffffff; font-size: 2.5rem; font-weight: 700; margin: 0; padding: 0; letter-spacing: -0.5px; }}
    .inst-desc {{ color: #8b949e; font-size: 1.1rem; margin-top: 10px; }}
    
    .stat-card-ma {{ background: rgba(30, 34, 43, 0.5); padding: 25px; border-radius: 8px; border-top: 4px solid #1f77b4; margin-top: 20px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}
    .stat-card-ma.lbo-card {{ border-top: 4px solid #9467bd; }}
    .ma-card-title {{ color: #8b949e; font-size: 0.9rem; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 1px; }}
    .ma-card-value {{ color: white; font-size: 2.2rem; font-weight: 700; margin: 0; }}
    .ma-highlight {{ color: #9467bd; }}
    
    div[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 8px !important; background: rgba(22,26,34,0.4); padding: 1.5rem !important; margin-bottom: 2rem !important; }}
    
    [data-testid="stSidebarNav"] li:first-child a span {{ display: none !important; }}
    [data-testid="stSidebarNav"] li:first-child a::after {{ content: "🏠 Home"; font-size: 15px; margin-left: 0px; }}
    
    {rtl_css}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR TOOLS ---
with st.sidebar:
    st.markdown("---")
    st.markdown(f"<h3 style='color: #9467bd;'>{txt['sb_tools']}</h3>", unsafe_allow_html=True)
    
    with st.expander(txt['fx_title'], expanded=True):
        usd_mad = 1 / st.session_state.rates.get("USD", 0.10)
        eur_mad = 1 / st.session_state.rates.get("EUR", 0.09)
        st.markdown(f"🇺🇸 **1 USD** = `{usd_mad:.2f} MAD`")
        st.markdown(f"🇪🇺 **1 EUR** = `{eur_mad:.2f} MAD`")
        
    with st.expander(txt['calc_title'], expanded=False):
        pv = st.number_input(txt['pv'], value=1000.0, step=100.0)
        fv = st.number_input(txt['fv'], value=1500.0, step=100.0)
        yrs = st.number_input(txt['yrs'], value=5, min_value=1)
        if pv > 0 and yrs > 0:
            cagr = ((fv / pv) ** (1 / yrs) - 1) * 100
            st.success(f"**{txt['cagr_res']}** {cagr:.2f}%")
            
    with st.expander(txt['scratch_title'], expanded=False):
        st.text_area("", placeholder=txt['scratch_ph'], height=150, label_visibility="collapsed")

# --- HEADER SECTION ---
st.markdown(f"""
<div class="inst-header" {'dir="rtl"' if lang=="العربية" else ''}>
    <span class="inst-phase">{txt['phase']}</span>
    <h1 class="inst-title">{txt['title']}</h1>
    <p class="inst-desc">{txt['desc']}</p>
</div>
""", unsafe_allow_html=True)

with st.expander(txt["glos_title"]):
    st.markdown(txt["glos_mc"])
    st.markdown(txt["glos_moic"])

# --- 1. MAIN PAGE INPUTS ---
with st.container(border=True):
    st.markdown(f"### {txt['sb_title']}")
    st.info(txt["sb_info"])
    c_b1, c_b2 = st.columns(2, gap="large")
    with c_b1: base_rev = st.number_input(txt["b_rev"], value=5000000.0, step=100000.0)
    with c_b2: base_ebitda = st.number_input(txt["b_ebitda"], value=1200000.0, step=50000.0)

st.markdown("<br>", unsafe_allow_html=True)

# --- 2. ADVANCED WACC CALCULATOR (CAPM) ---
with st.container(border=True):
    st.markdown(f"### {txt['capm_title']}")
    st.info(txt["capm_def"])
    use_capm = st.toggle(txt["capm_toggle"])

    if use_capm:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4, gap="medium")
        rf = c1.number_input(txt["rf"], value=4.0) / 100
        rm = c2.number_input(txt["rm"], value=10.0) / 100
        beta = c3.number_input(txt["beta"], value=1.2)
        tax = c4.number_input(txt["tax"], value=30.0) / 100
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        c5, c6 = st.columns(2, gap="large")
        kd_raw = c5.number_input(txt["kd"], value=6.0) / 100
        debt_weight = c6.slider(txt["w_debt"], 0.0, 100.0, 40.0) / 100
        equity_weight = 1 - debt_weight
        
        ke = rf + beta * (rm - rf)
        kd = kd_raw * (1 - tax)
        wacc = (ke * equity_weight) + (kd * debt_weight)
        
        st.success(f"**{txt['ke_res']}:** {ke*100:.2f}% &nbsp; | &nbsp; **{txt['kd_res']}:** {kd*100:.2f}%")
        st.markdown(f"<h3 style='text-align:center; color:#1f77b4;'>🎯 {txt['wacc_res']}: {wacc*100:.2f}%</h3>", unsafe_allow_html=True)
    else:
        wacc = st.slider(txt["wacc_slider"], 5.0, 20.0, 10.0, 0.5) / 100
        
    param_seed = int((wacc * 1000) + base_rev)
    random.seed(param_seed)
    
    if wacc < 0.10:
        c_color, c_bg = "#2ca02c", "44, 160, 44"
        c_text = random.choice([txt['capm_good_1'], txt['capm_good_2'], txt['capm_good_3']])
    else:
        c_color, c_bg = "#d62728", "214, 39, 40"
        c_text = random.choice([txt['capm_bad_1'], txt['capm_bad_2'], txt['capm_bad_3']])
        
    st.markdown(f"""
    <div style="padding: 18px; border-radius: 8px; background-color: rgba({c_bg}, 0.08); border-left: 5px solid {c_color}; margin-top: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
        <p style="color: {c_color}; margin: 0; font-size: 1rem;"><b>💡 {txt['insight']}:</b> {c_text}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 3. VALUATION ENGINES ---
col_dcf, col_lbo = st.columns(2, gap="large")

with col_dcf:
    with st.container(border=True):
        st.markdown(f"<h3 style='color:#1f77b4;'>{txt['dcf_title']}</h3>", unsafe_allow_html=True)
        tg = st.slider(txt["tg"], 0.0, 5.0, 2.0, 0.1) / 100
        proj_growth = st.slider(txt["pg"], -10.0, 30.0, 5.0, 1.0) / 100
        margin = st.slider(txt["fcfm"], 1.0, 30.0, 15.0, 1.0) / 100

        # DCF Math
        cfs = [base_rev * ((1 + proj_growth)**i) * margin for i in range(1, 6)]
        terminal_value = ((cfs[-1] * (1 + tg)) / (wacc - tg)) if wacc > tg else 0
        ev = sum([cf / ((1 + wacc)**(i+1)) for i, cf in enumerate(cfs)]) + (terminal_value / ((1 + wacc)**5))
        
        ev_converted = ev * rate
        
        st.markdown(f"""
        <div class="stat-card-ma">
            <p class="ma-card-title">{txt['ev']}</p>
            <p class="ma-card-value" style="color: #4da8da;">{ev_converted:,.2f} <span style="font-size: 1.2rem;">{sym}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        # 🎲 MONTE CARLO SIMULATION
        if st.button(txt["mc_btn"], use_container_width=True, type="primary"):
            with st.spinner(txt["mc_run"]):
                np.random.seed(42)
                sim_growths = np.random.normal(proj_growth, 0.02, 10000) 
                sim_margins = np.random.normal(margin, 0.02, 10000) 
                
                sim_evs = []
                for g, m in zip(sim_growths, sim_margins):
                    s_cfs = [base_rev * ((1 + g)**i) * m for i in range(1, 6)]
                    s_tv = ((s_cfs[-1] * (1 + tg)) / (wacc - tg)) if wacc > tg else 0
                    s_ev = sum([cf / ((1 + wacc)**(i+1)) for i, cf in enumerate(s_cfs)]) + (s_tv / ((1 + wacc)**5))
                    sim_evs.append(s_ev * rate)
                
                fig_mc = go.Figure(data=[go.Histogram(x=sim_evs, nbinsx=50, marker_color='#9467bd')])
                fig_mc.update_layout(title=txt["mc_chart"], template="plotly_dark", xaxis_title=f"EV ({sym})", yaxis_title=txt["freq"], height=350, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig_mc, use_container_width=True)
                
                perc_25, perc_75 = np.percentile(sim_evs, 25), np.percentile(sim_evs, 75)
                st.caption(f"**{txt['ci']}:** {perc_25:,.0f} {sym} - {perc_75:,.0f} {sym}")

with col_lbo:
    with st.container(border=True):
        st.markdown(f"<h3 style='color:#9467bd;'>{txt['lbo_title']}</h3>", unsafe_allow_html=True)
        c_l1, c_l2 = st.columns(2, gap="medium")
        with c_l1: entry_mult = st.number_input(txt["entry_m"], 3.0, 15.0, 6.0, 0.5)
        with c_l2: exit_mult = st.number_input(txt["exit_m"], 3.0, 15.0, 6.0, 0.5)
        
        c_l3, c_l4 = st.columns(2, gap="medium")
        with c_l3: debt_pct = st.slider(txt["debt_f"], 0.0, 90.0, 60.0, 5.0) / 100
        with c_l4: int_rate = st.slider(txt["int_rate"], 1.0, 20.0, 8.0, 0.5) / 100

        # LBO Math (Upgraded Rigor with Dynamic Amortization Loop)
        entry_ev = base_ebitda * entry_mult
        debt_quantum = entry_ev * debt_pct
        sponsor_equity = entry_ev - debt_quantum
        
        current_debt = debt_quantum
        for cf in cfs:
            interest_expense = current_debt * int_rate
            cads = cf - interest_expense # Cash Available for Debt Service
            if cads > 0:
                principal_paydown = cads * 1.0 # 100% cash sweep assumption
                current_debt = max(0, current_debt - principal_paydown)
            else:
                # Debt capitalizes (PIK) if FCF cannot cover interest
                current_debt += abs(cads)
                
        remaining_debt = current_debt
        
        exit_ebitda = base_ebitda * ((1 + proj_growth)**5)
        exit_ev = exit_ebitda * exit_mult
        exit_equity = exit_ev - remaining_debt

        moic = exit_equity / sponsor_equity if sponsor_equity > 0 else 0
        irr = ((moic**(1/5) - 1) * 100) if moic > 0 else 0
        
        st.markdown(f"""
        <div class="stat-card-ma lbo-card">
            <p class="ma-card-title">{txt['pe_metrics']}</p>
            <p class="ma-card-value">{txt['irr']}: <span class="ma-highlight">{irr:.2f}%</span></p>
            <p class="ma-card-value" style="font-size: 22px; margin-top: 10px;">{txt['moic']}: <span class="ma-highlight">{moic:.2f}x</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        # --- DYNAMIC LBO INTERPRETATION ---
        lbo_seed = int((irr * 100) + entry_mult)
        random.seed(lbo_seed)
        
        if irr >= 20.0:
            l_color, l_bg = "#9467bd", "148, 103, 189" 
            l_text = random.choice([txt['lbo_good_1'], txt['lbo_good_2'], txt['lbo_good_3']])
        else:
            l_color, l_bg = "#d62728", "214, 39, 40"
            l_text = random.choice([txt['lbo_bad_1'], txt['lbo_bad_2'], txt['lbo_bad_3']])
            
        st.markdown(f"""
        <div style="padding: 18px; border-radius: 8px; background-color: rgba({l_bg}, 0.08); border-left: 5px solid {l_color}; margin-top: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            <p style="color: {l_color}; margin: 0; font-size: 1rem;"><b>💡 {txt['insight']}:</b> {l_text}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- 4. DCF SENSITIVITY HEATMAP ---
st.subheader(txt["sens_hm"])

wacc_range_dcf = np.linspace(max(0.06, wacc - 0.02), max(0.10, wacc + 0.02), 7)
tg_range_dcf = np.linspace(max(0.01, tg - 0.01), min(0.05, tg + 0.01), 7)

z_data_dcf = []
for w in wacc_range_dcf:
    row_ev = []
    for t_g in tg_range_dcf:
        if w > t_g:
            tv_matrix = ((cfs[-1] * (1 + t_g)) / (w - t_g))
            ev_matrix = sum([cf / ((1 + w)**(i+1)) for i, cf in enumerate(cfs)]) + (tv_matrix / ((1 + w)**5))
        else:
            ev_matrix = 0
        row_ev.append(ev_matrix * rate)
    z_data_dcf.append(row_ev)

fig_heat_dcf = go.Figure(data=go.Heatmap(
    z=z_data_dcf, 
    x=np.round(tg_range_dcf*100, 2), 
    y=np.round(wacc_range_dcf*100, 2), 
    colorscale='Purples', 
    colorbar=dict(title=sym),
    hovertemplate="Growth: %{x}%<br>WACC: %{y}%<br>EV: %{z:,.0f} " + sym + "<extra></extra>"
))
fig_heat_dcf.update_layout(xaxis_title="Terminal Growth %", yaxis_title="WACC %", template="plotly_dark", height=500, margin=dict(l=20, r=20, t=30, b=20))
st.plotly_chart(fig_heat_dcf, use_container_width=True)

st.markdown("---")

# --- 5. EXPORT TO EXCEL ---
output_val = io.BytesIO()
with pd.ExcelWriter(output_val, engine='xlsxwriter') as writer:
    workbook = writer.book
    
    worksheet = workbook.add_worksheet('Structuring_Summary')
    header_format = workbook.add_format({'bold': True, 'bg_color': '#9467bd', 'font_color': 'white', 'border': 1})
    cell_format = workbook.add_format({'border': 1})
    
    worksheet.write('A1', 'Metric', header_format)
    worksheet.write('B1', 'Value', header_format)
    worksheet.set_column('A:B', 25)
    
    data_val = [
        ("Base Revenue", f"{base_rev * rate:,.2f} {sym}"),
        ("Base EBITDA", f"{base_ebitda * rate:,.2f} {sym}"),
        ("Implied WACC", f"{wacc*100:.2f}%"),
        ("Terminal Growth", f"{tg*100:.2f}%"),
        ("Enterprise Value (DCF)", f"{ev_converted:,.2f} {sym}"),
        ("LBO Entry EV", f"{entry_ev * rate:,.2f} {sym}"),
        ("LBO Entry Multiple", f"{entry_mult:.1f}x"),
        ("LBO Exit Multiple", f"{exit_mult:.1f}x"),
        ("Debt Quantum (Entry)", f"{debt_quantum * rate:,.2f} {sym}"),
        ("Implied IRR", f"{irr:.2f}%"),
        ("Implied MoIC", f"{moic:.2f}x")
    ]
    
    for row_num, (metric, val) in enumerate(data_val, start=1):
        worksheet.write(row_num, 0, metric, cell_format)
        worksheet.write(row_num, 1, val, cell_format)
        
    worksheet.write('D1', 'Year', header_format)
    worksheet.write('E1', f'Projected FCF ({sym})', header_format)
    worksheet.set_column('D:E', 20)
    for i, cf in enumerate(cfs, start=1):
        worksheet.write(i, 3, f"Year {i}", cell_format)
        worksheet.write(i, 4, cf * rate, cell_format)
        
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({
        'name': 'Free Cash Flow',
        'categories': '=Structuring_Summary!$D$2:$D$6',
        'values': '=Structuring_Summary!$E$2:$E$6',
        'fill': {'color': '#9467bd'}
    })
    chart.set_title({'name': '5-Year Projected FCF'})
    worksheet.insert_chart('G2', chart)
    
    worksheet_hm = workbook.add_worksheet('Sensitivity_Heatmap')
    worksheet_hm.write(0, 0, 'WACC \\ Growth', header_format)
    
    for col_idx, t_g in enumerate(tg_range_dcf, start=1):
        worksheet_hm.write(0, col_idx, f"{t_g*100:.2f}%", header_format)
        worksheet_hm.set_column(col_idx, col_idx, 15)
        
    for row_idx, (w, row_data) in enumerate(zip(wacc_range_dcf, z_data_dcf), start=1):
        worksheet_hm.write(row_idx, 0, f"{w*100:.2f}%", header_format)
        for col_idx, val in enumerate(row_data, start=1):
            worksheet_hm.write(row_idx, col_idx, val, cell_format)
            
    worksheet_hm.set_column(0, 0, 18)
    worksheet_hm.conditional_format(1, 1, len(wacc_range_dcf), len(tg_range_dcf), {
        'type': '3_color_scale',
        'min_color': '#f2e6ff',
        'mid_color': '#b388ff',
        'max_color': '#6e40c9'
    })

st.download_button(
    label=txt["dl_val_xlsx"],
    data=output_val.getvalue(),
    file_name="Buyout_Structuring_Model.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    type="secondary"
)
