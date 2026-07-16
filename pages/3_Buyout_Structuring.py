import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import io
import random

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
        "title": "💼 M&A & Private Equity Deal Room", "banner_desc": "Advanced Valuation, LBO Modeling & Risk Analysis",
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
        "lbo_title": "💰 LBO Quick-Modeler",
        "entry_m": "Entry Multiple (x)", "exit_m": "Exit Multiple (x)", "debt_f": "Debt Funding %",
        "pe_metrics": "Private Equity Metrics (5-Year)", "irr": "IRR", "moic": "MoIC",
        "sens_hm": "📊 EV Sensitivity (WACC vs Terminal Growth)", "dl_val_xlsx": "📥 Export Valuation Model (Excel + Charts)",
        "sb_tools": "🛠️ Analyst Tools", "fx_title": "🌍 FX Rates (Base MAD)", "calc_title": "🧮 Quick CAGR Calc",
        "pv": "Present Value", "fv": "Future Value", "yrs": "Years", "cagr_res": "CAGR:", 
        "scratch_title": "📝 Scratchpad", "scratch_ph": "Jot down your deal notes here...",
        "insight": "Analyst Lecture & Verdict",
        # Dynamic Conclusions (English)
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
        "title": "💼 Salle des Marchés M&A & Private Equity", "banner_desc": "Valorisation Avancée, Modélisation LBO & Analyse des Risques",
        "glos_title": "ℹ️ Glossaire et Définitions",
        "glos_mc": "- **Simulation Monte Carlo :** Algorithme informatique basé sur un échantillonnage aléatoire répété pour évaluer l'impact du risque et de l'incertitude.",
        "glos_moic": "- **MoIC (Multiple sur le Capital Investi) :** Indique la valeur générée par un investissement (Capitaux Propres de Sortie / Entrée).",
        "sb_title": "🏢 Données Financières de Base", "sb_info": "Saisissez les données financières de base de la cible (en MAD).",
        "b_rev": "Revenus de Base (MAD)", "b_ebitda": "EBITDA de Base (MAD)",
        "capm_title": "⚙️ Calculateur WACC Avancé (MEDAF)",
        "capm_def": "**Considérations MEDAF :** Le modèle calcule la rentabilité attendue des capitaux propres ($K_e$). Il établit une relation linéaire entre la rentabilité requise et le risque systématique ($\\beta$).\n\n**Formule :** $K_e = R_f + \\beta \\times (R_m - R_f)$",
        "rf": "Taux Sans Risque (%)", "rm": "Rendement du Marché (%)", "beta": "Bêta (β)", "tax": "Taux d'Imposition (%)", "kd": "Coût de la Dette (%)", "w_debt": "Pondération de la Dette (%)",
        "ke_res": "Coût des Capitaux Propres (Ke)", "kd_res": "Coût de la Dette après impôts (Kd)", "wacc_res": "CMPC Implicite (WACC)",
        "capm_toggle": "Activer le Mode de Calcul MEDAF", "wacc_slider": "CMPC (WACC) %",
        "dcf_title": "📊 Moteur DCF Standard",
        "tg": "Croissance Terminale %", "pg": "Croissance Projetée %", "fcfm": "Marge FCF %", "ev": "Valeur d'Entreprise Implicite (VE)",
        "mc_btn": "🎲 Lancer Simulation Monte Carlo (10k Itérations)", "mc_run": "Exécution de 10 000 simulations...",
        "mc_chart": "Distribution de Probabilité de la Valeur d'Entreprise", "freq": "Fréquence", "ci": "Intervalle de Confiance à 75 %",
        "lbo_title": "💰 Modélisateur LBO Rapide",
        "entry_m": "Multiple d'Entrée (x)", "exit_m": "Multiple de Sortie (x)", "debt_f": "Financement par Dette %",
        "pe_metrics": "Métriques Private Equity (Horizon 5 ans)", "irr": "TRI (IRR)", "moic": "Multiple (MoIC)",
        "sens_hm": "📊 Sensibilité de la VE (WACC vs Croissance)", "dl_val_xlsx": "📥 Exporter le Modèle de Valorisation",
        "sb_tools": "🛠️ Outils de l'Analyste", "fx_title": "🌍 Taux de Change", "calc_title": "🧮 Calculateur CAGR",
        "pv": "Valeur Actuelle", "fv": "Valeur Future", "yrs": "Années", "cagr_res": "TCAM :", 
        "scratch_title": "📝 Bloc-notes", "scratch_ph": "Prenez vos notes ici...",
        "insight": "Note de Lecture de l'Analyste",
        # Dynamic Conclusions (French)
        "capm_good_1": "Situation très favorable ! La cible bénéficie d'un coût du capital bas. Les flux financiers futurs ajouteront une prime nette de valeur pour l'investisseur.",
        "capm_good_2": "Structure de financement optimale. Le taux de rendement exigé est facilement surmontable, protégeant immédiatement la mise de l'acheteur.",
        "capm_good_3": "Faible risque systématique détecté. Le coût modéré du capital sécurise l'investissement et booste le potentiel de valorisation globale.",
        "capm_bad_1": "Structure défavorable. Le coût élevé du capital pénalise l'actualisation des flux futurs, réduisant fortement la valeur nette finale pour l'investisseur.",
        "capm_bad_2": "Prudence requise : Le coût de financement est trop lourd. Une croissance opérationnelle agressive est obligatoire pour justifier ce rendement.",
        "capm_bad_3": "Risque systématique élevé qui bride la valorisation. L'investisseur subira des spreads compressés sans restructuration du capital.",
        "lbo_good_1": "Excellent rendement en vue ! Le TRI projeté dépasse largement les exigences standards de l'industrie pour les actionnaires.",
        "lbo_good_2": "Opportunité de rachat de premier plan. Le remboursement rapide de la dette et la croissance de l'EBITDA assurent un fort multiple de sortie.",
        "lbo_good_3": "Excellente marge de sécurité financière. Le modèle permet de multiplier le capital de départ avec un profil de risque très maîtrisé.",
        "lbo_bad_1": "Rendement insuffisant. Le TRI prévisionnel est en dessous des exigences de performance du Private Equity ; conditions d'entrée à renégocier.",
        "lbo_bad_2": "Alerte piège de valeur : Un multiple d'entrée trop cher combiné au coût de la dette détruit le retour sur investissement des capitaux propres.",
        "lbo_bad_3": "Faible performance pour l'investisseur. Le levier opérationnel est insuffisant pour générer des multiples de sortie attractifs."
    },
    "Español": {
        "title": "💼 Sala de Fusiones y Capital Privado (M&A)", "banner_desc": "Valoración Avanzada, Modelado LBO y Análisis de Riesgos",
        "glos_title": "ℹ️ Glosario y Definiciones Avanzadas",
        "glos_mc": "- **Simulación Monte Carlo:** Algoritmo computacional basado en muestreo aleatorio repetido para comprender el impacto del riesgo.",
        "glos_moic": "- **MoIC (Múltiplo sobre Capital Invertido):** Muestra cuánto valor ha generado una inversión.",
        "sb_title": "🏢 Finanzas Base del Objetivo", "sb_info": "Ingrese las finanzas base de la empresa objetivo aquí (en MAD).",
        "b_rev": "Ingresos Base (MAD)", "b_ebitda": "EBITDA Base (MAD)",
        "capm_title": "⚙️ Calculadora WACC Avanzada",
        "capm_def": "**Modelo de Valoración de Activos de Capital (CAPM):** El CAPM es un modelo financiero utilizado para calcular la rentabilidad esperada del capital ($K_e$). Establece una relación lineal entre la rentabilidad y el riesgo sistemático ($\\beta$).\n\n**Fórmula:** $K_e = R_f + \\beta \\times (R_m - R_f)$",
        "rf": "Tasa Libre de Riesgo (%)", "rm": "Retorno del Mercado (%)", "beta": "Beta (β)", "tax": "Tasa Impositiva (%)", "kd": "Costo de la Deuda (%)", "w_debt": "Ponderación de Deuda (%)",
        "ke_res": "Costo del Capital (Ke)", "kd_res": "Costo de Deuda después de tiempos (Kd)", "wacc_res": "WACC Implícito",
        "capm_toggle": "Habilitar Modo de Cálculo CAPM", "wacc_slider": "WACC %",
        "dcf_title": "📊 Motor DCF Estándar",
        "tg": "Crecimiento Terminal %", "pg": "Crecimiento Proyectado %", "fcfm": "Margen FCF %", "ev": "Valor Empresarial Implícito (EV)",
        "mc_btn": "🎲 Ejecutar Simulación Monte Carlo", "mc_run": "Ejecutando 10,000 simulaciones...",
        "mc_chart": "Distribución de Probabilidad del Valor Empresarial", "freq": "Frecuencia", "ci": "Intervalo de Confianza del 75%",
        "lbo_title": "💰 Modelador LBO Rápido",
        "entry_m": "Múltiplo de Entrada (x)", "exit_m": "Múltiplo de Salida (x)", "debt_f": "Financiamiento de Deuda %",
        "pe_metrics": "Métricas PE (Horizonte 5 años)", "irr": "TIR (IRR)", "moic": "Múltiplo (MoIC)",
        "sens_hm": "📊 Sensibilidad del EV (WACC vs Crecimiento)", "dl_val_xlsx": "📥 Exportar Modelo de Valoración",
        "sb_tools": "🛠️ Herramientas de Análisis", "fx_title": "🌍 Tipos de Cambio", "calc_title": "🧮 Calculadora CAGR",
        "pv": "Valor Presente", "fv": "Valor Futuro", "yrs": "Años", "cagr_res": "CAGR:", 
        "scratch_title": "📝 Bloc de Notas", "scratch_ph": "Tome sus notas aquí...",
        "insight": "Análisis del Evaluador",
        "capm_good_1": "¡Estructura óptima! Costo de capital bajo que incrementa el valor neto para el inversor.",
        "capm_good_2": "Perfil de inversión sólido. El retorno requerido es fácilmente superable.",
        "capm_good_3": "Bajo riesgo sistemático detectado que protege la inversión inicial del comprador.",
        "capm_bad_1": "Estructura desfavorable. El alto costo descuenta agresivamente los flujos futuros.",
        "capm_bad_2": "Precaución: Financiamiento costoso. Se requiere un fuerte crecimiento operativo.",
        "capm_bad_3": "El alto riesgo limita la valoración. Se requiere optimización de la deuda.",
        "lbo_good_1": "¡Rendimiento excelente! La TIR proyectada supera con creces las expectativas.",
        "lbo_good_2": "Gran oportunidad de compra. El rápido pago de la deuda asegura buenos retornos.",
        "lbo_good_3": "Fuerte colchón financiero. Permite multiplicar el capital invertido con bajo riesgo.",
        "lbo_bad_1": "Retornos subóptimos. La TIR está por debajo de los estándares del mercado.",
        "lbo_bad_2": "Alerta de trampa de valor: Múltiplos caros destruyen el retorno de capital.",
        "lbo_bad_3": "Rendimiento débil para el inversor. El apalancamiento operativo es insuficiente."
    },
    "العربية": {
        "title": "💼 غرفة صفقات الاندماج والاستحواذ (M&A)", "banner_desc": "التقييم المتقدم، النمذجة المالية وتحليل المخاطر",
        "glos_title": "ℹ️ مسرد المصطلحات والتعاريف المتقدمة",
        "glos_mc": "- **محاكاة مونت كارلو:** خوارزمية حسابية تعتمد على أخذ عينات عشوائية متكررة لفهم تأثير المخاطر وعدم اليقين في التقييم.",
        "glos_moic": "- **مضاعف رأس المال المستثمر (MoIC):** يوضح مقدار القيمة التي حققها الاستثمار (حقوق الملكية عند التخارج / الدخول).",
        "sb_title": "🏢 البيانات المالية الأساسية للشركة", "sb_info": "أدخل البيانات المالية الأساسية للشركة المستهدفة هنا (بالدرهم المغربي).",
        "b_rev": "الإيرادات الأساسية (MAD)", "b_ebitda": "الأرباح التشغيلية EBITDA (MAD)",
        "capm_title": "⚙️ حاسبة WACC المتقدمة (CAPM)",
        "capm_def": "**نموذج تسعير الأصول الرأسمالية (CAPM):** هو نموذج مالي يُستخدم لحساب العائد المتوقع على حقوق الملكية ($K_e$). ويقيم علاقة خطية بين العائد المطلوب للاستثمار والمخاطر المنهجية ($\\beta$).\n\n**المعادلة:** $K_e = R_f + \\beta \\times (R_m - R_f)$",
        "rf": "المعدل الخالي من المخاطر (%)", "rm": "عائد السوق (%)", "beta": "بيتا (β)", "tax": "نسبة الضريبة (%)", "kd": "تكلفة الدين (%)", "w_debt": "وزن الدين (%)",
        "ke_res": "تكلفة حقوق الملكية (Ke)", "kd_res": "تكلفة الدين بعد الضريبة (Kd)", "wacc_res": "المتوسط المرجح لتكلفة رأس المال (WACC)",
        "capm_toggle": "تمكين وضع حساب CAPM", "wacc_slider": "المتوسط المرجح لتكلفة رأس المال (WACC) %",
        "dcf_title": "📊 محرك خصم التدفقات النقدية (DCF)",
        "tg": "النمو النهائي (Terminal Growth) %", "pg": "النمو المتوقع %", "fcfm": "هامش التدفق الندي الحر (FCF) %", "ev": "القيمة المؤسسية الضمنية (EV)",
        "mc_btn": "🎲 تشغيل محاكاة مونت كارلو", "mc_run": "يتم الآن تشغيل 10,000 محاكاة...",
        "mc_chart": "التوزيع الاحتمالي للقيمة المؤسسية", "freq": "التردد", "ci": "فترة ثقة 75%",
        "lbo_title": "💰 نموذج الاستحواذ المدعوم بالقروض (LBO)",
        "entry_m": "مضاعف الدخول (x)", "exit_m": "مضاعف التخارج (x)", "debt_f": "نسبة تمويل الديون %",
        "pe_metrics": "مقاييس الأسهم الخاصة (أفق 5 سنوات)", "irr": "معدل العائد الداخلي (IRR)", "moic": "مضاعف رأس المال (MoIC)",
        "sens_hm": "📊 تحليل الحساسية (WACC مقابل النمو)", "dl_val_xlsx": "📥 تصدير نموذج التقييم المتقدم (Excel)",
        "sb_tools": "🛠️ أدوات المحلل السريعة", "fx_title": "🌍 أسعار الصرف", "calc_title": "🧮 حاسبة النمو (CAGR)",
        "pv": "القيمة الحالية", "fv": "القيمة المستقبلية", "yrs": "السنوات", "cagr_res": "معدل النمو (CAGR):", 
        "scratch_title": "📝 مذكرة الملاحظات", "scratch_ph": "دون ملاحظاتك السريعة هنا...",
        "insight": "قراءة تحليلية للمستثمر",
        "capm_good_1": "هيكل تمويل مثالي! تكلفة رأس مال منخفضة تضمن تحقيق قيمة مضافة ممتازة لصافي أرباح المستثمر.",
        "capm_good_2": "ملف استثماري مريح جداً. العائد المطلوب على حقوق الملكية منخفض مما يحمي أموال المشتري.",
        "capm_good_3": "مخاطر منهجية منخفضة تؤمن الاستثمار التشغيلي وتدعم فرص التقييم التصاعدي.",
        "capm_bad_1": "هيكل غير ملائم. تكلفة رأس المال المرتفعة تلتهم التدفقات النقدية وتقلل القيمة الصافية للمستثمر.",
        "capm_bad_2": "تحذير: عبء تمويلي باهظ. الشركة ملزمة بتحقيق نمو تشغيلي قوي جداً لتغطية التكلفة.",
        "capm_bad_3": "المخاطر المنهجية المرتفعة تكبح جماح التقييم وتضيق هوامش الربح المتوقعة للمستثمر.",
        "lbo_good_1": "عائد استثنائي في الأفق! معدل IRR المتوقع يتجاوز متطلبات الصناديق الاستثمارية الكبرى بكثير.",
        "lbo_good_2": "فرصة استحواذ ممتازة. السداد السريع للديون يضمن تضخيم قيمة حقوق الملكية عند الخروج.",
        "lbo_good_3": "هامش أمان مالي متميز يتيح مضاعفة رأس المال الأولي بملف مخاطر خاضع للسيطرة تماماً.",
        "lbo_bad_1": "مستوى عوائد غير كافٍ. معدل IRR يقل عن معايير الاستحواذ؛ يجب إعادة التفاوض على شروط الدخول.",
        "lbo_bad_2": "تحذير من فخ القيمة: مضاعفات الدخول المرتفعة مع ديون مكلفة تسحق عوائد المستثمر تماماً.",
        "lbo_bad_3": "عوائد ضعيفة جداً للمستثمر بسبب عدم كفاية الرافعات التشغيلية لإنتاج مضاعفات تخارج جذابة."
    }
}
txt = t[lang]

# --- UI STYLING & CSS HACKS ---
rtl_css = ""
if lang == "العربية":
    rtl_css = """
    .block-container { direction: rtl; text-align: right; }
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"], [data-testid="stHeader"] { direction: ltr !important; text-align: left !important; }
    """

st.markdown(f"""
<style>
    /* Global Fade-in / Fade-up Animation */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(15px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .block-container {{ animation: fadeIn 0.6s ease-out; }}

    [data-testid="stSidebarNav"] li:first-child a span {{ display: none !important; }}
    [data-testid="stSidebarNav"] li:first-child a::after {{ content: "🏠 Home"; font-size: 15px; margin-left: 0px; }}
    
    /* M&A Banner Styling */
    .full-width-banner {{ position: relative; width: 100%; height: 250px; background-image: url('https://images.unsplash.com/photo-1600880292203-757bb62b4baf?q=80&w=2070&auto=format&fit=crop'); background-size: cover; background-position: center; margin-bottom: 25px; border-radius: 10px; border-left: 5px solid #9467bd; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
    .banner-overlay {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, rgba(14,17,23,0.95) 0%, rgba(14,17,23,0.6) 50%, rgba(148,103,189,0.3) 100%); }}
    .banner-content {{ position: absolute; top: 50%; left: 30px; transform: translateY(-50%); z-index: 2; }}
    
    /* Premium Glassmorphism Stat Cards */
    .stat-card-ma {{ background: rgba(22, 26, 34, 0.7); backdrop-filter: blur(12px); border-radius: 10px; padding: 25px; text-align: center; border-top: 4px solid #1f77b4; margin-top: 20px; margin-bottom: 10px; box-shadow: 0 8px 20px rgba(0,0,0,0.4); transition: transform 0.3s ease; }}
    .stat-card-ma:hover {{ transform: translateY(-5px); }}
    .stat-card-ma.lbo-card {{ border-top: 4px solid #9467bd; }}
    .ma-card-title {{ color: #a0aab5; font-size: 15px; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }}
    .ma-card-value {{ color: white; font-size: 30px; font-weight: 800; margin: 0; text-shadow: 0 0 15px rgba(255,255,255,0.15); }}
    .ma-highlight {{ color: #2ca02c; }}
    
    /* Highlighted Box for Inputs */
    .highlight-box {{ background-color: rgba(255, 255, 255, 0.03); padding: 20px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 25px; }}
    
    {rtl_css}
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {{
        .block-container {{ padding-top: 2rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }}
        .banner h1, .full-width-banner h1 {{ font-size: 1.6rem !important; }}
        .banner p, .full-width-banner p {{ font-size: 0.9rem !important; }}
        [data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; margin-bottom: 15px !important; }}
    }}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR TOOLS (QUICK ANALYST WIDGETS) ---
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

# --- BANNER ---
st.markdown(f"""
<div class="full-width-banner">
    <div class="banner-overlay"></div>
    <div class="banner-content" {'dir="rtl"' if lang=="العربية" else ''}>
        <h1 style="color: white; margin: 0; font-size: 2.5rem; letter-spacing: 1px;">{txt['title']}</h1>
        <p style="color:#e0e0e0; font-size:1.1rem; margin-top: 8px;">{txt['banner_desc']}</p>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander(txt["glos_title"]):
    st.markdown(txt["glos_mc"])
    st.markdown(txt["glos_moic"])

# --- 1. MAIN PAGE INPUTS ---
with st.container(border=True):
    st.markdown(f"### {txt['sb_title']}")
    st.info(txt["sb_info"])
    c_b1, c_b2 = st.columns(2)
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
        c1, c2, c3, c4 = st.columns(4)
        rf = c1.number_input(txt["rf"], value=4.0) / 100
        rm = c2.number_input(txt["rm"], value=10.0) / 100
        beta = c3.number_input(txt["beta"], value=1.2)
        tax = c4.number_input(txt["tax"], value=30.0) / 100
        
        st.markdown("---")
        
        c5, c6 = st.columns(2)
        kd_raw = c5.number_input(txt["kd"], value=6.0) / 100
        debt_weight = c6.slider(txt["w_debt"], 0.0, 100.0, 40.0) / 100
        equity_weight = 1 - debt_weight
        
        ke = rf + beta * (rm - rf)
        kd = kd_raw * (1 - tax)
        wacc = (ke * equity_weight) + (kd * debt_weight)
        
        st.success(f"**{txt['ke_res']}:** {ke*100:.2f}% &nbsp; | &nbsp; **{txt['kd_res']}:** {kd*100:.2f}%")
        st.markdown(f"<h3 style='text-align:center; color:#2ca02c;'>🎯 {txt['wacc_res']}: {wacc*100:.2f}%</h3>", unsafe_allow_html=True)
    else:
        wacc = st.slider(txt["wacc_slider"], 5.0, 20.0, 10.0, 0.5) / 100
        
    # --- DYNAMIC CAPM/WACC INTERPRETATION (3 GOOD / 3 BAD SCENARIOS) ---
    # Using a deterministic seed based on current parameters to prevent chaotic switching on every render
    param_seed = int((wacc * 1000) + base_rev)
    random.seed(param_seed)
    
    if wacc < 0.10:
        c_color, c_bg = "#2ca02c", "44, 160, 44"
        c_text = random.choice([txt['capm_good_1'], txt['capm_good_2'], txt['capm_good_3']])
    else:
        c_color, c_bg = "#d62728", "214, 39, 40"
        c_text = random.choice([txt['capm_bad_1'], txt['capm_bad_2'], txt['capm_bad_3']])
        
    st.markdown(f"""
    <div style="padding: 14px; border-radius: 8px; background-color: rgba({c_bg}, 0.08); border-left: 5px solid {c_color}; margin-top: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
        <p style="color: {c_color}; margin: 0; font-size: 0.95rem;"><b>💡 {txt['insight']}:</b> {c_text}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

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
            <p class="ma-card-value" style="color: #4da8da;">{ev_converted:,.2f} {sym}</p>
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
                
                fig_mc = go.Figure(data=[go.Histogram(x=sim_evs, nbinsx=50, marker_color='#c1272d')])
                fig_mc.update_layout(title=txt["mc_chart"], template="plotly_dark", xaxis_title=f"EV ({sym})", yaxis_title=txt["freq"], height=350)
                st.plotly_chart(fig_mc, use_container_width=True)
                
                perc_25, perc_75 = np.percentile(sim_evs, 25), np.percentile(sim_evs, 75)
                st.caption(f"**{txt['ci']}:** {perc_25:,.0f} {sym} - {perc_75:,.0f} {sym}")

with col_lbo:
    with st.container(border=True):
        st.markdown(f"<h3 style='color:#9467bd;'>{txt['lbo_title']}</h3>", unsafe_allow_html=True)
        c_l1, c_l2 = st.columns(2)
        with c_l1: entry_mult = st.number_input(txt["entry_m"], 3.0, 15.0, 6.0, 0.5)
        with c_l2: exit_mult = st.number_input(txt["exit_m"], 3.0, 15.0, 6.0, 0.5)
        debt_pct = st.slider(txt["debt_f"], 0.0, 90.0, 60.0, 5.0) / 100

        # LBO Math
        entry_ev = base_ebitda * entry_mult
        debt = entry_ev * debt_pct
        equity = entry_ev - debt
        exit_ev = (base_ebitda * ((1 + proj_growth)**5)) * exit_mult
        exit_equity = exit_ev - max(0, debt - sum(cfs)*0.5)

        moic = exit_equity / equity if equity > 0 else 0
        irr = ((moic**(1/5) - 1) * 100) if moic > 0 else 0
        
        st.markdown(f"""
        <div class="stat-card-ma lbo-card">
            <p class="ma-card-title">{txt['pe_metrics']}</p>
            <p class="ma-card-value">{txt['irr']}: <span class="ma-highlight">{irr:.2f}%</span></p>
            <p class="ma-card-value" style="font-size: 22px; margin-top: 5px;">{txt['moic']}: <span class="ma-highlight">{moic:.2f}x</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        # --- DYNAMIC LBO INTERPRETATION (3 GOOD / 3 BAD SCENARIOS) ---
        lbo_seed = int((irr * 100) + entry_mult)
        random.seed(lbo_seed)
        
        if irr >= 20.0:
            l_color, l_bg = "#2ca02c", "44, 160, 44"
            l_text = random.choice([txt['lbo_good_1'], txt['lbo_good_2'], txt['lbo_good_3']])
        else:
            l_color, l_bg = "#d62728", "214, 39, 40"
            l_text = random.choice([txt['lbo_bad_1'], txt['lbo_bad_2'], txt['lbo_bad_3']])
            
        st.markdown(f"""
        <div style="padding: 14px; border-radius: 8px; background-color: rgba({l_bg}, 0.08); border-left: 5px solid {l_color}; margin-top: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
            <p style="color: {l_color}; margin: 0; font-size: 0.95rem;"><b>💡 {txt['insight']}:</b> {l_text}</p>
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
    colorscale='RdYlGn', 
    colorbar=dict(title=sym),
    hovertemplate="Growth: %{x}%<br>WACC: %{y}%<br>EV: %{z:,.0f} " + sym + "<extra></extra>"
))
fig_heat_dcf.update_layout(xaxis_title="Terminal Growth %", yaxis_title="WACC %", template="plotly_dark", height=450)
st.plotly_chart(fig_heat_dcf, use_container_width=True)

st.markdown("---")

# --- 5. EXPORT TO EXCEL ---
output_val = io.BytesIO()
with pd.ExcelWriter(output_val, engine='xlsxwriter') as writer:
    workbook = writer.book
    
    worksheet = workbook.add_worksheet('Valuation_Summary')
    header_format = workbook.add_format({'bold': True, 'bg_color': '#1f77b4', 'font_color': 'white', 'border': 1})
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
        ("LBO Entry Multiple", f"{entry_mult:.1f}x"),
        ("LBO Exit Multiple", f"{exit_mult:.1f}x"),
        ("Debt Funding", f"{debt_pct*100:.1f}%"),
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
        'categories': '=Valuation_Summary!$D$2:$D$6',
        'values': '=Valuation_Summary!$E$2:$E$6',
        'fill': {'color': '#2ca02c'}
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
        'min_color': '#f8696b',
        'mid_color': '#ffeb84',
        'max_color': '#63be7b'
    })

st.download_button(
    label=txt["dl_val_xlsx"],
    data=output_val.getvalue(),
    file_name="Valuation_Model.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    type="secondary"
)
