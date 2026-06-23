import streamlit as st

# --- SECURITY ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

# --- GLOBAL STATE INITIALIZATION ---
lang = st.session_state.get("lang", "English")

# --- TRANSLATION DICTIONARY ---
t = {
    "English": {
        "banner_h": "📖 Methodology & Docs", "banner_desc": "Technical specifications and financial formulas powering the analytics engine.",
        "intro": "This documentation outlines the core financial theories and mathematical models integrated into the platform's valuation algorithms.",
        "wacc_title": "1. Cost of Capital (WACC) & CAPM",
        "wacc_desc": "The Weighted Average Cost of Capital (WACC) is used as the primary discount rate for Free Cash Flows. The Cost of Equity ($K_e$) is derived using the Capital Asset Pricing Model (CAPM). For Moroccan benchmarks, the Risk-Free Rate ($R_f$) is typically pegged to the 10-Year Moroccan Treasury Bond.",
        "dcf_title": "2. Discounted Cash Flow (DCF)",
        "dcf_desc": "The DCF engine projects Free Cash Flows to the Firm (FCFF) over a 5-year explicit forecast period. The Terminal Value (TV) is calculated using the Gordon Growth Model, assuming a perpetual growth rate ($g$) that reflects long-term macroeconomic inflation.",
        "lbo_title": "3. Leveraged Buyout (LBO) Metrics",
        "lbo_desc": "The LBO quick-modeler evaluates the feasibility of a sponsor-backed buyout assuming a 5-year holding horizon. Value creation is measured through debt paydown and EBITDA multiple expansion. The primary return metrics are the Internal Rate of Return (IRR) and Multiple on Invested Capital (MoIC).",
        "comps_title": "4. Comparable Company Analysis (CCA)",
        "comps_desc": "Relative valuation is performed by benchmarking target metrics against Moroccan BTP sector peers. Key multiples tracked include EV/EBITDA, P/E (Price-to-Earnings), and Price-to-Book (P/B)."
    },
    "Français": {
        "banner_h": "📖 Méthodologie & Docs", "banner_desc": "Spécifications techniques et formules financières alimentant le moteur d'analyse.",
        "intro": "Cette documentation détaille les théories financières et les modèles mathématiques intégrés dans les algorithmes de valorisation de la plateforme.",
        "wacc_title": "1. Coût du Capital (CMPC) & MEDAF",
        "wacc_desc": "Le Coût Moyen Pondéré du Capital (CMPC) est utilisé comme taux d'actualisation principal. Le coût des capitaux propres ($K_e$) est calculé via le MEDAF. Pour le marché marocain, le taux sans risque ($R_f$) est basé sur les Bons du Trésor à 10 ans.",
        "dcf_title": "2. Actualisation des Flux de Trésorerie (DCF)",
        "dcf_desc": "Le modèle DCF projette les flux de trésorerie disponibles (FCFF) sur 5 ans. La Valeur Terminale (TV) est calculée avec le modèle de Gordon Shapiro, supposant un taux de croissance perpétuelle ($g$).",
        "lbo_title": "3. Métriques LBO (Rachat par Effet de Levier)",
        "lbo_desc": "Le modèle LBO évalue la faisabilité d'un rachat sur un horizon de 5 ans. La création de valeur est mesurée par le remboursement de la dette. Les rendements sont évalués via le TRI (Taux de Rentabilité Interne) et le Multiple de Capital Investi (MoIC).",
        "comps_title": "4. Analyse des Comparables Boursiers",
        "comps_desc": "La valorisation relative est effectuée en comparant les cibles aux pairs du secteur BTP marocain (EV/EBITDA, P/E, P/B)."
    },
    "Español": {
        "banner_h": "📖 Metodología y Docs", "banner_desc": "Especificaciones técnicas y fórmulas financieras del motor de análisis.",
        "intro": "Esta documentación describe las teorías financieras y los modelos matemáticos integrados en los algoritmos de valoración de la plataforma.",
        "wacc_title": "1. Costo de Capital (WACC) y CAPM",
        "wacc_desc": "El Costo Promedio Ponderado de Capital (WACC) se usa como tasa de descuento. El Costo de Capital ($K_e$) se calcula mediante el CAPM. Para el mercado marroquí, la Tasa Libre de Riesgo ($R_f$) se basa en los Bonos del Tesoro a 10 años.",
        "dcf_title": "2. Flujo de Caja Descontado (DCF)",
        "dcf_desc": "El motor DCF proyecta los Flujos de Caja Libres (FCFF) a 5 años. El Valor Terminal (TV) se calcula utilizando el Modelo de Crecimiento de Gordon.",
        "lbo_title": "3. Métricas de Compra Apalancada (LBO)",
        "lbo_desc": "El modelo LBO evalúa la viabilidad de una compra con un horizonte de 5 años. Las métricas de retorno principales son la Tasa Interna de Retorno (TIR) y el Múltiplo sobre el Capital Invertido (MoIC).",
        "comps_title": "4. Análisis de Empresas Comparables",
        "comps_desc": "La valoración relativa se realiza comparando métricas con pares del sector BTP marroquí (EV/EBITDA, P/E, P/B)."
    },
    "العربية": {
        "banner_h": "📖 المنهجية والوثائق", "banner_desc": "المواصفات التقنية والمعادلات المالية التي تشغل محرك التحليل.",
        "intro": "توضح هذه الوثيقة النظريات المالية والنماذج الرياضية المدمجة في خوارزميات التقييم الخاصة بالمنصة.",
        "wacc_title": "1. تكلفة رأس المال (WACC) و نموذج تسعير الأصول (CAPM)",
        "wacc_desc": "يُستخدم المتوسط المرجح لتكلفة رأس المال (WACC) كمعدل خصم أساسي. يتم اشتقاق تكلفة حقوق الملكية باستخدام نموذج (CAPM). بالنسبة للسوق المغربي، يُربط المعدل الخالي من المخاطر غالباً بسندات الخزينة لأجل 10 سنوات.",
        "dcf_title": "2. خصم التدفقات النقدية (DCF)",
        "dcf_desc": "يتوقع محرك DCF التدفقات النقدية الحرة لمدة 5 سنوات. يتم حساب القيمة النهائية باستخدام نموذج جوردون للنمو، بافتراض معدل نمو دائم يعكس التضخم طويل الأجل.",
        "lbo_title": "3. مقاييس الاستحواذ المدعوم بالقروض (LBO)",
        "lbo_desc": "يقيم نموذج LBO جدوى الاستحواذ بافتراض أفق احتفاظ يبلغ 5 سنوات. تُقاس القيمة من خلال سداد الديون. مقاييس العائد الأساسية هي معدل العائد الداخلي (IRR) ومضاعف رأس المال المستثمر (MoIC).",
        "comps_title": "4. تحليل الشركات المقارنة",
        "comps_desc": "يتم إجراء التقييم النسبي من خلال مقارنة المقاييس مع نظيراتها في قطاع البناء المغربي (EV/EBITDA، مكرر الربحية)."
    }
}
txt = t[lang]

# --- UI STYLING & CSS ---
rtl_css = ""
if lang == "العربية":
    rtl_css = """
    .block-container { direction: rtl; text-align: right; }
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"], [data-testid="stHeader"] { direction: ltr !important; text-align: left !important; }
    """

st.markdown(f"""
<style>
    /* Fade-in Animation */
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .block-container {{ animation: fadeIn 0.5s ease-out; }}
    
    [data-testid="stSidebarNav"] li:first-child a span {{ display: none !important; }}
    [data-testid="stSidebarNav"] li:first-child a::after {{ content: "🏠 Home"; font-size: 15px; margin-left: 0px; }}
    
    /* Clean Academic Banner */
    .full-width-banner {{ position: relative; width: 100%; height: 200px; background-image: url('https://images.unsplash.com/photo-1450101499163-c8848c66ca85?q=80&w=2070&auto=format&fit=crop'); background-size: cover; background-position: center; margin-bottom: 30px; border-radius: 10px; border-left: 5px solid #d4af37; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
    .banner-overlay {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, rgba(14,17,23,0.95) 0%, rgba(14,17,23,0.8) 50%, rgba(212,175,55,0.2) 100%); }}
    .banner-content {{ position: absolute; top: 50%; left: 30px; transform: translateY(-50%); z-index: 2; }}
    
    /* Methodology Content Styling */
    .meth-box {{ background-color: rgba(255, 255, 255, 0.03); padding: 25px; border-radius: 8px; border-top: 2px solid #333; margin-bottom: 25px; transition: all 0.3s ease; }}
    .meth-box:hover {{ background-color: rgba(255, 255, 255, 0.05); border-top: 2px solid #d4af37; }}
    
    {rtl_css}
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {{
        .block-container {{ padding-top: 2rem !important; padding-left: 0.8rem !important; padding-right: 0.8rem !important; }}
        .banner-content h1 {{ font-size: 1.8rem !important; }}
        .banner-content p {{ font-size: 0.95rem !important; }}
        [data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; margin-bottom: 15px !important; }}
    }}
</style>
""", unsafe_allow_html=True)

# --- BANNER ---
st.markdown(f"""
<div class="full-width-banner">
    <div class="banner-overlay"></div>
    <div class="banner-content" {'dir="rtl"' if lang=="العربية" else ''}>
        <h1 style="color: white; margin: 0; font-size: 2.5rem; letter-spacing: 1px;">{txt['banner_h']}</h1>
        <p style="color:#e0e0e0; font-size:1.1rem; margin-top: 8px;">{txt['banner_desc']}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- INTRO ---
st.markdown(f"<p style='font-size: 1.1rem; color: #b3b3b3; margin-bottom: 30px;' {'dir=\"rtl\"' if lang=='العربية' else ''}>{txt['intro']}</p>", unsafe_allow_html=True)

# --- SECTION 1: WACC ---
st.markdown(f"<div class='meth-box' {'dir=\"rtl\"' if lang=='العربية' else ''}><h3>{txt['wacc_title']}</h3><p>{txt['wacc_desc']}</p></div>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.latex(r"K_e = R_f + \beta \times (R_m - R_f)")
with c2:
    st.latex(r"WACC = \left(\frac{E}{V} \times K_e\right) + \left(\frac{D}{V} \times K_d \times (1 - t)\right)")

st.markdown("<br>", unsafe_allow_html=True)

# --- SECTION 2: DCF ---
st.markdown(f"<div class='meth-box' {'dir=\"rtl\"' if lang=='العربية' else ''}><h3>{txt['dcf_title']}</h3><p>{txt['dcf_desc']}</p></div>", unsafe_allow_html=True)
c3, c4 = st.columns(2)
with c3:
    st.latex(r"DCF = \sum_{t=1}^{n} \frac{FCF_t}{(1 + WACC)^t} + \frac{TV}{(1 + WACC)^n}")
with c4:
    st.latex(r"TV = \frac{FCF_n \times (1 + g)}{WACC - g}")

st.markdown("<br>", unsafe_allow_html=True)

# --- SECTION 3: LBO ---
st.markdown(f"<div class='meth-box' {'dir=\"rtl\"' if lang=='العربية' else ''}><h3>{txt['lbo_title']}</h3><p>{txt['lbo_desc']}</p></div>", unsafe_allow_html=True)
c5, c6 = st.columns(2)
with c5:
    st.latex(r"MoIC = \frac{\text{Exit Equity Value}}{\text{Entry Equity Value}}")
with c6:
    st.latex(r"IRR = \left( MoIC \right)^{\frac{1}{Years}} - 1")

st.markdown("<br>", unsafe_allow_html=True)

# --- SECTION 4: COMPS ---
st.markdown(f"<div class='meth-box' {'dir=\"rtl\"' if lang=='العربية' else ''}><h3>{txt['comps_title']}</h3><p>{txt['comps_desc']}</p></div>", unsafe_allow_html=True)
st.latex(r"EV = \text{Market Cap} + \text{Total Debt} - \text{Cash & Equivalents}")
