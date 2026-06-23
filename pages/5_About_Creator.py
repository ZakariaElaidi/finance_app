import streamlit as st
import pandas as pd
import numpy as np

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
        "banner_h": "👤 Executive Profile", "banner_desc": "Corporate Finance, Financial Modeling, and M&A/PE Advisory Desk.",
        "name": "Zakaria Elaidi",
        "sub_name": "Financial Analyst & M&A / Private Equity Specialist",
        "desc1": "Currently pursuing a Master's degree in Finance (Programme Grande École) at **ENCG El Jadida**, Zakaria specializes in advanced financial analysis, corporate finance, and investment valuation.",
        "desc2": "With a strategic focus on targeting roles in **M&A, Investment Banking, and Private Equity**, he bridges the gap between traditional equity research and modern data science tools (Python, Pandas, SQL).",
        "bg_title": "🚀 Professional Track Record",
        "exp1_title": "Consulting Expertise:", "exp1_desc": "Successfully delivered over 150 financial modeling and analysis projects globally as a freelance consultant.",
        "exp2_title": "Corporate Exposure:", "exp2_desc": "Completed the rigorous KPMG UK Audit Job Simulation and completed comprehensive Investment Risk Management training.",
        "exp3_title": "Technical Arsenal:", "exp3_desc": "Advanced DCF Valuation, LBO Modeling, Market Finance (Marché des Capitaux), SQL, Algorithmic Training, and Python (NumPy, Pandas, Matplotlib).",
        "net_title": "Professional Network",
        "net_desc": "Open to networking, M&A discussions, and equity research collaborations.",
        "net_btn": "Connect on LinkedIn", "cv_btn": "📄 Download Executive CV (PDF)"
    },
    "Français": {
        "banner_h": "👤 Profil Exécutif", "banner_desc": "Finance d'Entreprise, Modélisation Financière et Bureau de Conseil M&A/PE.",
        "name": "Zakaria Elaidi",
        "sub_name": "Analyste Financier & Spécialiste M&A / Private Equity",
        "desc1": "Actuellement en Master Finance (Programme Grande École) à **l'ENCG El Jadida**, Zakaria est spécialisé dans l'analyse financière avancée, la finance d'entreprise et la valorisation des investissements.",
        "desc2": "Avec un objectif stratégique ciblant les rôles en **M&A, Banque d'Investissement et Private Equity**, il fait le pont entre la recherche en actions traditionnelle et les outils modernes de Data Science (Python, Pandas, SQL).",
        "bg_title": "🚀 Parcours & Réalisations",
        "exp1_title": "Expertise en Conseil :", "exp1_desc": "A livré avec succès plus de 150 projets de modélisation et d'analyse financière à l'échelle mondiale en tant que consultant indépendant.",
        "exp2_title": "Exposition en Entreprise :", "exp2_desc": "A complété la rigoureuse simulation de poste en audit chez KPMG UK et une formation approfondie en gestion des risques d'investissement.",
        "exp3_title": "Arsenal Technique :", "exp3_desc": "Valorisation DCF avancée, Modélisation LBO, Finance de Marché (Marché des Capitaux), SQL, algorithmique et Python (NumPy, Pandas, Matplotlib).",
        "net_title": "Réseau Professionnel",
        "net_desc": "Ouvert au networking, aux discussions M&A et aux collaborations en recherche d'actions.",
        "net_btn": "Se connecter sur LinkedIn", "cv_btn": "📄 Télécharger le CV (PDF)"
    },
    "Español": {
        "banner_h": "👤 Perfil Ejecutivo", "banner_desc": "Finanzas Corporativas, Modelado Financiero y Asesoría en M&A/PE.",
        "name": "Zakaria Elaidi",
        "sub_name": "Analista Financiero y Especialista en M&A / Private Equity",
        "desc1": "Actualmente cursando un Máster en Finanzas (Programme Grande École) en **ENCG El Jadida**, Zakaria se especializa en análisis financiero avanzado, finanzas corporativas y valoración de inversiones.",
        "desc2": "Con un enfoque estratégico en roles de **M&A, Banca de Inversión y Capital Privado (Private Equity)**, une la investigación tradicional de acciones con herramientas modernas de ciencia de datos (Python, Pandas, SQL).",
        "bg_title": "🚀 Trayectoria Profesional",
        "exp1_title": "Experiencia en Consultoría:", "exp1_desc": "Entregó con éxito más de 150 proyectos de modelado y análisis financiero a nivel global como consultor independiente.",
        "exp2_title": "Exposición Corporativa:", "exp2_desc": "Completó la rigurosa simulación de auditoría de KPMG UK y formación integral en gestión de riesgos de inversión.",
        "exp3_title": "Arsenal Técnico:", "exp3_desc": "Valoración DCF, Modelado LBO, Finanzas de Mercado (Marché des Capitaux), SQL, entrenamiento algorítmico y Python (NumPy, Pandas, Matplotlib).",
        "net_title": "Red Profesional",
        "net_desc": "Abierto al networking, discusiones sobre M&A y colaboraciones en investigación de acciones.",
        "net_btn": "Conectar en LinkedIn", "cv_btn": "📄 Descargar CV Ejecutivo (PDF)"
    },
    "العربية": {
        "banner_h": "👤 الملف المهني والتنفيذي", "banner_desc": "تمويل الشركات، النمذجة المالية، ومكتب استشارات الاندماج والاستحواذ والأسهم الخاصة.",
        "name": "زكرياء العيدي",
        "sub_name": "محلل مالي ومتخصص في الاندماج والاستحواذ (M&A) والأسهم الخاصة (PE)",
        "desc1": "يتابع حالياً دراسة الماستر في تخصص المالية (برنامج المدارس الوطنية للتجارة والتسيير) بـ **ENCG الجديدة**، وهو متخصص في التحليل المالي المتقدم، تمويل الشركات، وتقييم الاستثمارات.",
        "desc2": "مع تركيز استراتيجي على شغل مناصب في **عمليات الاندماج والاستحواذ (M&A)، البنوك الاستثمارية، والأسهم الخاصة**، يجمع بين أبحاث الأسهم التقليدية وأدوات علوم البيانات الحديثة (Python, Pandas, SQL).",
        "bg_title": "🚀 سجل الإنجازات المهنية",
        "exp1_title": "الخبرة الاستشارية:", "exp1_desc": "أنجز بنجاح أكثر من 150 مشروعاً في النمذجة والتحليل المالي على مستوى العالم كمستشار مستقل.",
        "exp2_title": "الخبرة في الشركات:", "exp2_desc": "أكمل بنجاح المحاكاة الوظيفية للتدقيق في KPMG UK وحاصل على تدريب متقدم في إدارة مخاطر الاستثمار.",
        "exp3_title": "الترسانة التقنية:", "exp3_desc": "تقييم التدفقات النقدية المخصومة (DCF)، نمذجة LBO، أسواق المال، تحليل البيانات المالية، SQL، وPython (NumPy, Pandas, Matplotlib).",
        "net_title": "الشبكة المهنية",
        "net_desc": "متاح للتواصل المهني، والنقاشات حول الاندماج والاستحواذ، والتعاون في أبحاث الأسهم.",
        "net_btn": "تواصل عبر لينكد إن", "cv_btn": "📄 تحميل السيرة الذاتية التنفيذية (PDF)"
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
    
    /* About Me Banner Styling (Charcoal / Platinum Slate Theme) */
    .full-width-banner {{ position: relative; width: 100%; height: 250px; background-image: url('https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=2070&auto=format&fit=crop'); background-size: cover; background-position: center; margin-bottom: 25px; border-radius: 10px; border-left: 5px solid #495057; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
    .banner-overlay {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, rgba(14,17,23,0.95) 0%, rgba(14,17,23,0.7) 50%, rgba(73,80,87,0.3) 100%); }}
    .banner-content {{ position: absolute; top: 50%; left: 30px; transform: translateY(-50%); z-index: 2; }}
    
    .network-box {{ background-color: #161a22; padding: 25px; border-radius: 8px; border-top: 4px solid #495057; text-align: center; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
    .btn-linkedin {{ background-color: #0077b5; color: white !important; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: block; margin-top: 20px; transition: 0.3s; text-align: center; }}
    .btn-linkedin:hover {{ background-color: #005582; text-decoration: none; }}
    
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

# --- PAGE CONTENT ---
col_text, col_network = st.columns([2, 1], gap="large")

with col_text:
    st.markdown(f"## {txt['name']}")
    st.markdown(f"#### *{txt['sub_name']}*")
    st.write(txt["desc1"])
    st.write(txt["desc2"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### {txt['bg_title']}")
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Placeholder byte data to prevent empty file download crashes
    mock_cv_data = b"Zakaria Elaidi - Executive CV Placeholder Data"
    st.download_button(
        label=txt["cv_btn"],
        data=mock_cv_data,
        file_name="Zakaria_Elaidi_Executive_CV.pdf",
        mime="application/pdf",
        use_container_width=True
    )
