import streamlit as st
import pandas as pd
import numpy as np
import os

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
        "header_tag": "EXECUTIVE PROFILE",
        "banner_h": "Zakaria Elaidi", "banner_desc": "Corporate Finance, Financial Modeling, and M&A/PE Advisory Desk.",
        "sub_name": "Financial Analyst & M&A / Private Equity Specialist",
        "desc1": "Currently pursuing a Master's degree in Finance (Programme Grande École) at <strong>ENCG El Jadida</strong>, specializing in advanced financial analysis, corporate finance, and investment valuation.",
        "desc2": "With a strategic focus on targeting roles in <strong>M&A, Investment Banking, and Private Equity</strong>, Zakaria bridges the gap between traditional equity research and modern data science tools.",
        "bg_title": "🚀 Professional Track Record",
        "exp1_title": "Quantitative Architecture:", "exp1_desc": "Engineered and deployed a proprietary deal origination and structuring engine (Python, Pandas, Plotly) to automate LBO mechanics and DCF sensitivities.",
        "exp2_title": "Corporate Exposure:", "exp2_desc": "Completed the rigorous KPMG UK Audit Job Simulation and finalized comprehensive Investment Risk Management training.",
        "exp3_title": "Technical Arsenal:", "exp3_desc": "Advanced DCF Valuation, LBO Modeling, Market Finance (Marché des Capitaux), SQL, Algorithmic Trading Concepts, and Python.",
        "net_title": "Professional Network",
        "net_desc": "Open to networking, M&A discussions, and equity research collaborations.",
        "net_btn": "Connect on LinkedIn", "cv_btn": "📄 Download Executive CV (PDF)"
    },
    "Français": {
        "header_tag": "PROFIL EXÉCUTIF",
        "banner_h": "Zakaria Elaidi", "banner_desc": "Finance d'Entreprise, Modélisation Financière et Bureau de Conseil M&A/PE.",
        "sub_name": "Analyste Financier & Spécialiste M&A / Private Equity",
        "desc1": "Actuellement en Master Finance (Programme Grande École) à <strong>l'ENCG El Jadida</strong>, spécialisé dans l'analyse financière avancée, la finance d'entreprise et la valorisation des investissements.",
        "desc2": "Avec un objectif stratégique ciblant les rôles en <strong>M&A, Banque d'Investissement et Private Equity</strong>, Zakaria fait le pont entre la recherche en actions traditionnelle et les outils de Data Science.",
        "bg_title": "🚀 Parcours & Réalisations",
        "exp1_title": "Architecture Quantitative :", "exp1_desc": "A conçu et déployé un moteur propriétaire d'origination et de structuration de deals (Python, Pandas, Plotly) pour automatiser les LBO et les sensibilités DCF.",
        "exp2_title": "Exposition en Entreprise :", "exp2_desc": "A complété la rigoureuse simulation de poste en audit chez KPMG UK et une formation approfondie en gestion des risques.",
        "exp3_title": "Arsenal Technique :", "exp3_desc": "Valorisation DCF avancée, Modélisation LBO, Finance de Marché (Marché des Capitaux), SQL et Python.",
        "net_title": "Réseau Professionnel",
        "net_desc": "Ouvert au networking, aux discussions M&A et aux collaborations en recherche d'actions.",
        "net_btn": "Se connecter sur LinkedIn", "cv_btn": "📄 Télécharger le CV (PDF)"
    },
    "Español": {
        "header_tag": "PERFIL EJECUTIVO",
        "banner_h": "Zakaria Elaidi", "banner_desc": "Finanzas Corporativas, Modelado Financiero y Asesoría en M&A/PE.",
        "sub_name": "Analista Financiero y Especialista en M&A / Private Equity",
        "desc1": "Actualmente cursando un Máster en Finanzas (Programme Grande École) en <strong>ENCG El Jadida</strong>, especializado en análisis financiero avanzado, finanzas corporativas y valoración de inversiones.",
        "desc2": "Con un enfoque estratégico en roles de <strong>M&A, Banca de Inversión y Capital Privado</strong>, Zakaria une la investigación tradicional de acciones con herramientas de ciencia de datos.",
        "bg_title": "🚀 Trayectoria Profesional",
        "exp1_title": "Arquitectura Cuantitativa:", "exp1_desc": "Diseñó e implementó un motor patentado de originación y estructuración de acuerdos (Python, Pandas, Plotly) para automatizar LBO y DCF.",
        "exp2_title": "Exposición Corporativa:", "exp2_desc": "Completó la rigurosa simulación de auditoría de KPMG UK y formación en gestión de riesgos de inversión.",
        "exp3_title": "Arsenal Técnico:", "exp3_desc": "Valoración DCF, Modelado LBO, Finanzas de Mercado (Marché des Capitaux), SQL y Python.",
        "net_title": "Red Profesional",
        "net_desc": "Abierto al networking, discusiones sobre M&A y colaboraciones en investigación.",
        "net_btn": "Conectar en LinkedIn", "cv_btn": "📄 Descargar CV Ejecutivo (PDF)"
    },
    "العربية": {
        "header_tag": "الملف التنفيذي",
        "banner_h": "زكرياء العيدي", "banner_desc": "تمويل الشركات، النمذجة المالية، ومكتب استشارات الاندماج والاستحواذ والأسهم الخاصة.",
        "sub_name": "محلل مالي ومتخصص في الاندماج والاستحواذ (M&A) والأسهم الخاصة (PE)",
        "desc1": "يتابع حالياً دراسة الماستر في تخصص المالية (برنامج المدارس الوطنية للتجارة والتسيير) بـ <strong>ENCG الجديدة</strong>، ومتخصص في التحليل المالي المتقدم، تمويل الشركات، وتقييم الاستثمارات.",
        "desc2": "مع تركيز استراتيجي على شغل مناصب في <strong>عمليات الاندماج والاستحواذ، البنوك الاستثمارية، والأسهم الخاصة</strong>، يجمع زكرياء بين أبحاث الأسهم التقليدية وأدوات علوم البيانات.",
        "bg_title": "🚀 سجل الإنجازات المهنية",
        "exp1_title": "الهندسة الكمية:", "exp1_desc": "صمم ونفذ محركاً خاصاً لاكتشاف وهيكلة الصفقات (Python, Pandas, Plotly) لأتمتة آليات LBO وتحليل حساسية التدفقات النقدية المخصومة.",
        "exp2_title": "الخبرة في الشركات:", "exp2_desc": "أكمل بنجاح المحاكاة الوظيفية للتدقيق في KPMG UK وحاصل على تدريب في إدارة مخاطر الاستثمار.",
        "exp3_title": "الترسانة التقنية:", "exp3_desc": "تقييم DCF، نمذجة LBO، أسواق المال، SQL، وPython.",
        "net_title": "الشبكة المهنية",
        "net_desc": "متاح للتواصل المهني، والنقاشات حول الاندماج والاستحواذ، والتعاون في أبحاث الأسهم.",
        "net_btn": "تواصل عبر لينكد إن", "cv_btn": "📄 تحميل السيرة الذاتية (PDF)"
    }
}
txt = t[lang]

# --- FULL WIDTH CSS INJECTION (Cyan Theme) ---
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
    
    .inst-header {{ background: linear-gradient(145deg, #0e1117, #161b22); border-left: 4px solid #17becf; padding: 30px 40px; border-radius: 8px; margin-bottom: 40px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
    .inst-phase {{ color: #17becf; font-size: 0.9rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; display: block; }}
    .inst-title {{ color: #ffffff; font-size: 2.5rem; font-weight: 700; margin: 0; padding: 0; letter-spacing: -0.5px; }}
    .inst-desc {{ color: #8b949e; font-size: 1.1rem; margin-top: 10px; }}
    
    .network-box {{ background-color: rgba(30, 34, 43, 0.5); padding: 30px; border-radius: 8px; border-top: 4px solid #17becf; text-align: center; height: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}
    .btn-linkedin {{ background-color: #0077b5; color: white !important; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: block; margin-top: 20px; transition: 0.3s; text-align: center; }}
    .btn-linkedin:hover {{ background-color: #005582; text-decoration: none; }}
    
    .intro-box {{ background-color: rgba(22,26,34,0.4); padding: 25px 30px; border-radius: 8px; border-left: 4px solid #1f77b4; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
    
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

col_text, col_network = st.columns([2, 1], gap="large")

with col_text:
    st.markdown(f"#### *{txt['sub_name']}*")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="intro-box" {'dir="rtl"' if lang=="العربية" else ''}>
        <p style="color:#e0e0e0; font-size: 1.1rem; line-height: 1.6; margin-bottom: 15px;">{txt['desc1']}</p>
        <p style="color:#e0e0e0; font-size: 1.1rem; line-height: 1.6; margin-bottom: 0;">{txt['desc2']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### {txt['bg_title']}")
    st.markdown(f"- **{txt['exp1_title']}** {txt['exp1_desc']}")
    st.markdown(f"- **{txt['exp2_title']}** {txt['exp2_desc']}")
    st.markdown(f"- **{txt['exp3_title']}** {txt['exp3_desc']}")

with col_network:
    st.markdown(f"""
    <div class="network-box">
        <h3 style="margin-top:0; color:#fff;">{txt['net_title']}</h3>
        <p style="color:#8b949e; font-size: 0.95rem; margin-bottom: 25px;">{txt['net_desc']}</p>
        <a href="https://www.linkedin.com/in/zakaria-elaidi/" target="_blank" class="btn-linkedin">{txt['net_btn']}</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    cv_file_name = "Zakaria_Elaidi_CV.pdf"
    if os.path.exists(cv_file_name):
        with open(cv_file_name, "rb") as f:
            cv_data = f.read()
    else:
        cv_data = b""

    st.download_button(
        label=txt["cv_btn"],
        data=cv_data,
        file_name="Zakaria_Elaidi_CV.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary"
    )
