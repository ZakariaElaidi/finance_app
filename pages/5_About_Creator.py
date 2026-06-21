import streamlit as st

# --- SECURITY ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

# --- GLOBAL STATE INITIALIZATION ---
lang = st.session_state.get("lang", "English")

# --- TRANSLATION DICTIONARY ---
t = {
    "English": {
        "title": "👤 About Creator",
        "name": "Zakaria Elaidi | *Financial Analyst & M&A Specialist*",
        "desc1": "Currently pursuing a Master's degree in Finance (Programme Grande École) at **ENCG El Jadida**, Zakaria specializes in advanced financial analysis, corporate finance, and investment valuation.",
        "desc2": "With a strategic focus on targeting roles in **M&A, Investment Banking, and Private Equity**, he bridges the gap between traditional equity research and modern data science tools (Python, Pandas, SQL).",
        "bg_title": "Professional Background",
        "exp1_title": "Consulting Experience:", "exp1_desc": "Successfully delivered over 150 financial modeling and analysis projects globally as a freelance consultant.",
        "exp2_title": "Corporate Exposure:", "exp2_desc": "Completed the rigorous KPMG UK Audit Job Simulation and actively preparing for a professional placement at OCP Group.",
        "exp3_title": "Core Expertise:", "exp3_desc": "DCF Valuation, LBO Modeling, Market Finance, Marché des Capitaux, and Financial Statement Analysis.",
        "net_title": "Professional Network",
        "net_desc": "Open to networking, M&A discussions, and equity research collaborations.",
        "net_btn": "Connect on LinkedIn"
    },
    "Français": {
        "title": "👤 À propos du Créateur",
        "name": "Zakaria Elaidi | *Analyste Financier & Spécialiste M&A*",
        "desc1": "Actuellement en Master Finance (Programme Grande École) à **l'ENCG El Jadida**, Zakaria est spécialisé dans l'analyse financière avancée, la finance d'entreprise et la valorisation des investissements.",
        "desc2": "Avec un objectif stratégique ciblant les rôles en **M&A, Banque d'Investissement et Private Equity**, il fait le pont entre la recherche en actions traditionnelle et les outils modernes de Data Science (Python, Pandas, SQL).",
        "bg_title": "Parcours Professionnel",
        "exp1_title": "Expérience en Conseil :", "exp1_desc": "A livré avec succès plus de 150 projets de modélisation et d'analyse financière à l'échelle mondiale en tant que consultant indépendant.",
        "exp2_title": "Exposition en Entreprise :", "exp2_desc": "A complété la rigoureuse simulation de poste en audit chez KPMG UK et se prépare activement pour un stage professionnel au sein du Groupe OCP.",
        "exp3_title": "Expertise Principale :", "exp3_desc": "Valorisation DCF, Modélisation LBO, Finance de Marché, Marché des Capitaux et Analyse des États Financiers.",
        "net_title": "Réseau Professionnel",
        "net_desc": "Ouvert au networking, aux discussions M&A et aux collaborations en recherche d'actions.",
        "net_btn": "Se connecter sur LinkedIn"
    },
    "Español": {
        "title": "👤 Sobre el Creador",
        "name": "Zakaria Elaidi | *Analista Financiero y Especialista en M&A*",
        "desc1": "Actualmente cursando un Máster en Finanzas (Programme Grande École) en **ENCG El Jadida**, Zakaria se especializa en análisis financiero avanzado, finanzas corporativas y valoración de inversiones.",
        "desc2": "Con un enfoque estratégico en roles de **M&A, Banca de Inversión y Capital Privado (Private Equity)**, une la investigación tradicional de acciones con herramientas modernas de ciencia de datos (Python, Pandas, SQL).",
        "bg_title": "Trayectoria Profesional",
        "exp1_title": "Experiencia en Consultoría:", "exp1_desc": "Entregó con éxito más de 150 proyectos de modelado y análisis financiero a nivel global como consultor independiente.",
        "exp2_title": "Exposición Corporativa:", "exp2_desc": "Completó la rigurosa simulación de auditoría de KPMG UK y se prepara activamente para unas prácticas profesionales en el Grupo OCP.",
        "exp3_title": "Experiencia Principal:", "exp3_desc": "Valoración DCF, Modelado LBO, Finanzas de Mercado, Marché des Capitaux y Análisis de Estados Financieros.",
        "net_title": "Red Profesional",
        "net_desc": "Abierto al networking, discusiones sobre M&A y colaboraciones en investigación de acciones.",
        "net_btn": "Conectar en LinkedIn"
    },
    "العربية": {
        "title": "👤 عن المطور",
        "name": "زكرياء العيدي | *محلل مالي ومتخصص في الاندماج والاستحواذ*",
        "desc1": "يتابع حالياً دراسة الماستر في تخصص المالية (برنامج المدارس الوطنية للتجارة والتسيير) بـ **ENCG الجديدة**، وهو متخصص في التحليل المالي المتقدم، تمويل الشركات، وتقييم الاستثمارات.",
        "desc2": "مع تركيز استراتيجي على شغل مناصب في **عمليات الاندماج والاستحواذ (M&A)، البنوك الاستثمارية، والأسهم الخاصة**، يجمع زكرياء بين أبحاث الأسهم التقليدية وأدوات علوم البيانات الحديثة (Python, Pandas, SQL).",
        "bg_title": "الخلفية المهنية",
        "exp1_title": "الخبرة الاستشارية:", "exp1_desc": "أنجز بنجاح أكثر من 150 مشروعاً في النمذجة والتحليل المالي على مستوى العالم كمستشار مستقل.",
        "exp2_title": "الخبرة في الشركات:", "exp2_desc": "أكمل بنجاح المحاكاة الوظيفية للتدقيق في KPMG UK ويستعد حالياً لتدريب مهني في مجموعة OCP.",
        "exp3_title": "الخبرات الأساسية:", "exp3_desc": "تقييم التدفقات النقدية المخصومة (DCF)، نمذجة الاستحواذ المدعوم بالقروض (LBO)، أسواق المال، وتحليل البيانات المالية.",
        "net_title": "الشبكة المهنية",
        "net_desc": "متاح للتواصل المهني، والنقاشات حول الاندماج والاستحواذ، والتعاون في أبحاث الأسهم.",
        "net_btn": "تواصل عبر لينكد إن"
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
    [data-testid="stSidebarNav"] li:first-child a span {{ display: none !important; }}
    [data-testid="stSidebarNav"] li:first-child a::after {{ content: "🏠 Home"; font-size: 15px; margin-left: 0px; }}
    
    .network-box {{ background-color: #0e1117; padding: 25px; border-radius: 8px; border-top: 4px solid #c1272d; text-align: center; height: 100%; }}
    .btn-linkedin {{ background-color: #0077b5; color: white !important; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: block; margin-top: 20px; transition: 0.3s; }}
    .btn-linkedin:hover {{ background-color: #005582; text-decoration: none; }}
    
    {rtl_css}
</style>
""", unsafe_allow_html=True)

# --- PAGE CONTENT ---
st.title(txt["title"])
st.markdown("<br>", unsafe_allow_html=True)

col_text, col_network = st.columns([2, 1], gap="large")

with col_text:
    st.markdown(f"### {txt['name']}")
    st.write(txt["desc1"])
    st.write(txt["desc2"])
    
    st.markdown(f"#### {txt['bg_title']}")
    st.markdown(f"- **{txt['exp1_title']}** {txt['exp1_desc']}")
    st.markdown(f"- **{txt['exp2_title']}** {txt['exp2_desc']}")
    st.markdown(f"- **{txt['exp3_title']}** {txt['exp3_desc']}")

with col_network:
    st.markdown(f"""
    <div class="network-box">
        <h3 style="margin-top:0; color:#fff;">{txt['net_title']}</h3>
        <p style="color:#b3b3b3; font-size: 0.95rem;">{txt['net_desc']}</p>
        <a href="https://www.linkedin.com/in/zakaria-elaidi/" target="_blank" class="btn-linkedin">{txt['net_btn']}</a>
    </div>
    """, unsafe_allow_html=True)
