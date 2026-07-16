import streamlit as st

# --- SECURITY & STATE ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

lang = st.session_state.get("lang", "English")

# --- INSTITUTIONAL TRANSLATION DICTIONARY ---
t = {
    "English": {
        "header_tag": "TECHNICAL DOCUMENTATION",
        "banner_h": "Methodology & Framework", "banner_desc": "Technical specifications and financial formulas powering the analytics engine.",
        "intro": "This documentation outlines the core financial theories and mathematical models integrated into the platform's proprietary valuation algorithms.",
        "wacc_title": "1. Cost of Capital (WACC) & CAPM",
        "wacc_desc": "The Weighted Average Cost of Capital (WACC) serves as the primary discount rate for projecting future Free Cash Flows. The Cost of Equity ($K_e$) is derived using the Capital Asset Pricing Model (CAPM). For Moroccan benchmarks, the Risk-Free Rate ($R_f$) is typically pegged to the 10-Year Moroccan Treasury Bond.",
        "dcf_title": "2. Discounted Cash Flow (DCF) Engine",
        "dcf_desc": "The DCF engine projects Free Cash Flows to the Firm (FCFF) over a standard 5-year explicit forecast period. The Terminal Value (TV) is calculated via the Gordon Growth Model, assuming a perpetual growth rate ($g$) that reflects long-term macroeconomic inflation targets.",
        "lbo_title": "3. Leveraged Buyout (LBO) Mechanics",
        "lbo_desc": "The LBO quick-modeler evaluates the feasibility of a sponsor-backed buyout, assuming a 5-year holding horizon. Value creation is measured strictly through debt paydown and EBITDA multiple expansion. The primary return hurdles evaluated are the Internal Rate of Return (IRR) and Multiple on Invested Capital (MoIC).",
        "comps_title": "4. Comparable Company Analysis (CCA)",
        "comps_desc": "Relative valuation is executed by benchmarking target metrics against live Moroccan BTP sector peers. The engine tracks Enterprise Value (EV) multiples to normalize capital structure differences across public comparables."
    },
    "Français": {
        "header_tag": "DOCUMENTATION TECHNIQUE",
        "banner_h": "Méthodologie & Cadre", "banner_desc": "Spécifications techniques et formules financières alimentant le moteur d'analyse.",
        "intro": "Cette documentation détaille les théories financières et les modèles mathématiques intégrés dans les algorithmes de valorisation exclusifs de la plateforme.",
        "wacc_title": "1. Coût du Capital (CMPC) & MEDAF",
        "wacc_desc": "Le Coût Moyen Pondéré du Capital (CMPC) sert de taux d'actualisation principal. Le coût des capitaux propres ($K_e$) est calculé via le MEDAF. Pour le marché marocain, le taux sans risque ($R_f$) est basé sur les Bons du Trésor à 10 ans.",
        "dcf_title": "2. Moteur d'Actualisation des Flux (DCF)",
        "dcf_desc": "Le modèle DCF projette les flux de trésorerie disponibles (FCFF) sur 5 ans. La Valeur Terminale (TV) est calculée avec le modèle de Gordon Shapiro, supposant un taux de croissance perpétuelle ($g$).",
        "lbo_title": "3. Mécanique LBO (Rachat par Effet de Levier)",
        "lbo_desc": "Le modèle LBO évalue la faisabilité d'un rachat sur un horizon de 5 ans. La création de valeur est mesurée par le remboursement de la dette. Les rendements sont évalués via le TRI et le MoIC.",
        "comps_title": "4. Analyse des Comparables Boursiers (CCA)",
        "comps_desc": "La valorisation relative est effectuée en comparant les cibles aux pairs du secteur BTP marocain. Le moteur suit les multiples de Valeur d'Entreprise (VE)."
    },
    "Español": {
        "header_tag": "DOCUMENTACIÓN TÉCNICA",
        "banner_h": "Metodología y Marco", "banner_desc": "Especificaciones técnicas y fórmulas financieras del motor de análisis.",
        "intro": "Esta documentación describe las teorías financieras y los modelos matemáticos integrados en los algoritmos de valoración de la plataforma.",
        "wacc_title": "1. Costo de Capital (WACC) y CAPM",
        "wacc_desc": "El Costo Promedio Ponderado de Capital (WACC) sirve como tasa de descuento. El Costo de Capital ($K_e$) se calcula mediante el CAPM. Para el mercado marroquí, la Tasa Libre de Riesgo ($R_f$) se basa en los Bonos del Tesoro a 10 años.",
        "dcf_title": "2. Motor de Flujo de Caja Descontado (DCF)",
        "dcf_desc": "El motor DCF proyecta los Flujos de Caja Libres (FCFF) a 5 años. El Valor Terminal (TV) se calcula utilizando el Modelo de Crecimiento de Gordon.",
        "lbo_title": "3. Mecánica de Compra Apalancada (LBO)",
        "lbo_desc": "El modelo LBO evalúa la viabilidad de una compra con un horizonte de 5 años. La creación de valor se mide a través del pago de deuda. Los retornos se evalúan a través de TIR y MoIC.",
        "comps_title": "4. Análisis de Empresas Comparables (CCA)",
        "comps_desc": "La valoración relativa se realiza comparando métricas con pares del sector BTP marroquí. El motor rastrea múltiplos de Valor Empresarial (EV)."
    },
    "العربية": {
        "header_tag": "الوثائق التقنية",
        "banner_h": "المنهجية والإطار الفني", "banner_desc": "المواصفات التقنية والمعادلات المالية التي تشغل محركات التحليل.",
        "intro": "توضح هذه الوثيقة النظريات المالية والنماذج الرياضية المدمجة في خوارزميات التقييم الخاصة بالمنصة.",
        "wacc_title": "1. تكلفة رأس المال (WACC) و نموذج CAPM",
        "wacc_desc": "يُستخدم المتوسط المرجح لتكلفة رأس المال (WACC) كمعدل خصم أساسي. يتم اشتقاق تكلفة حقوق الملكية باستخدام نموذج (CAPM). بالنسبة للسوق المغربي، يُربط المعدل الخالي من المخاطر بسندات الخزينة لأجل 10 سنوات.",
        "dcf_title": "2. محرك خصم التدفقات النقدية (DCF)",
        "dcf_desc": "يتوقع محرك DCF التدفقات النقدية الحرة لمدة 5 سنوات. يتم حساب القيمة النهائية باستخدام نموذج جوردون للنمو، بافتراض معدل نمو دائم يعكس التضخم طويل الأجل.",
        "lbo_title": "3. آليات الاستحواذ المدعوم بالقروض (LBO)",
        "lbo_desc": "يقيم نموذج LBO جدوى الاستحواذ بافتراض أفق 5 سنوات. تُقاس القيمة من خلال سداد الديون. مقاييس العائد الأساسية هي معدل العائد الداخلي (IRR) ومضاعف رأس المال المستثمر (MoIC).",
        "comps_title": "4. تحليل الشركات المقارنة (CCA)",
        "comps_desc": "يتم إجراء التقييم النسبي من خلال مقارنة المقاييس مع نظيراتها في قطاع البناء المغربي. يتتبع المحرك مضاعفات القيمة المؤسسية (EV) لتحييد اختلافات هيكل رأس المال."
    }
}
txt = t[lang]

# --- FULL WIDTH CSS INJECTION (Slate/Silver Theme) ---
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
    
    .inst-header {{ background: linear-gradient(145deg, #0e1117, #161b22); border-left: 4px solid #8b949e; padding: 30px 40px; border-radius: 8px; margin-bottom: 40px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
    .inst-phase {{ color: #8b949e; font-size: 0.9rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; display: block; }}
    .inst-title {{ color: #ffffff; font-size: 2.5rem; font-weight: 700; margin: 0; padding: 0; letter-spacing: -0.5px; }}
    .inst-desc {{ color: #8b949e; font-size: 1.1rem; margin-top: 10px; }}
    
    .meth-box {{ background-color: rgba(22, 26, 34, 0.5); padding: 30px; border-radius: 8px; border-left: 4px solid #8b949e; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-top: 1px solid rgba(255,255,255,0.05); border-right: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); }}
    .meth-title {{ color: #ffffff; font-size: 1.4rem; font-weight: 600; margin-top: 0; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }}
    .meth-desc {{ color: #b3b3b3; font-size: 1.05rem; line-height: 1.6; margin-bottom: 25px; }}
    
    .latex-container {{ background-color: rgba(0,0,0,0.3); padding: 15px; border-radius: 6px; text-align: center; border: 1px solid rgba(255,255,255,0.05); }}
    
    [data-testid="stSidebarNav"] li:first-child a span {{ display: none !important; }}
    [data-testid="stSidebarNav"] li:first-child a::after {{ content: "🏠 Home"; font-size: 15px; margin-left: 0px; }}
    
    {rtl_css}
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown(f"""
<div class="inst-header" {'dir="rtl"' if lang=="العربية" else ''}>
    <span class="inst-phase">{txt['header_tag']}</span>
    <h1 class="inst-title">{txt['banner_h']}</h1>
    <p class="inst-desc">{txt['banner_desc']}</p>
</div>
""", unsafe_allow_html=True)

# --- INTRO ---
st.markdown(f"<p style='font-size: 1.1rem; color: #b3b3b3; margin-bottom: 40px; padding-left: 10px; border-left: 2px solid #8b949e;' {'dir=\"rtl\"' if lang=='العربية' else ''}>{txt['intro']}</p>", unsafe_allow_html=True)

# --- SECTION 1: WACC ---
st.markdown(f"""
<div class='meth-box' {'dir=\"rtl\"' if lang=='العربية' else ''}>
    <h3 class='meth-title'>{txt['wacc_title']}</h3>
    <p class='meth-desc'>{txt['wacc_desc']}</p>
</div>
""", unsafe_allow_html=True)
c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("<div class='latex-container'>", unsafe_allow_html=True)
    st.latex(r"K_e = R_f + \beta \times (R_m - R_f)")
    st.markdown("</div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='latex-container'>", unsafe_allow_html=True)
    st.latex(r"WACC = \left(\frac{E}{V} \times K_e\right) + \left(\frac{D}{V} \times K_d \times (1 - t)\right)")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- SECTION 2: DCF ---
st.markdown(f"""
<div class='meth-box' {'dir=\"rtl\"' if lang=='العربية' else ''}>
    <h3 class='meth-title'>{txt['dcf_title']}</h3>
    <p class='meth-desc'>{txt['dcf_desc']}</p>
</div>
""", unsafe_allow_html=True)
c3, c4 = st.columns(2, gap="large")
with c3:
    st.markdown("<div class='latex-container'>", unsafe_allow_html=True)
    st.latex(r"DCF = \sum_{t=1}^{n} \frac{FCF_t}{(1 + WACC)^t} + \frac{TV}{(1 + WACC)^n}")
    st.markdown("</div>", unsafe_allow_html=True)
with c4:
    st.markdown("<div class='latex-container'>", unsafe_allow_html=True)
    st.latex(r"TV = \frac{FCF_n \times (1 + g)}{WACC - g}")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- SECTION 3: LBO ---
st.markdown(f"""
<div class='meth-box' {'dir=\"rtl\"' if lang=='العربية' else ''}>
    <h3 class='meth-title'>{txt['lbo_title']}</h3>
    <p class='meth-desc'>{txt['lbo_desc']}</p>
</div>
""", unsafe_allow_html=True)
c5, c6 = st.columns(2, gap="large")
with c5:
    st.markdown("<div class='latex-container'>", unsafe_allow_html=True)
    st.latex(r"MoIC = \frac{\text{Exit Equity}}{\text{Entry Equity}}")
    st.markdown("</div>", unsafe_allow_html=True)
with c6:
    st.markdown("<div class='latex-container'>", unsafe_allow_html=True)
    st.latex(r"IRR = \left( MoIC \right)^{\frac{1}{\text{Holding Period}}} - 1")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- SECTION 4: COMPS ---
st.markdown(f"""
<div class='meth-box' {'dir=\"rtl\"' if lang=='العربية' else ''}>
    <h3 class='meth-title'>{txt['comps_title']}</h3>
    <p class='meth-desc'>{txt['comps_desc']}</p>
</div>
""", unsafe_allow_html=True)
st.markdown("<div class='latex-container'>", unsafe_allow_html=True)
st.latex(r"EV = \text{Market Cap} + \text{Total Debt} - \text{Cash \& Equivalents}")
st.markdown("</div>", unsafe_allow_html=True)
