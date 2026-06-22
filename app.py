import streamlit as st
import pandas as pd
from supabase import create_client, ClientOptions

# MUST BE THE FIRST LINE
st.set_page_config(
    page_title="Z.ELAIDI - Financial Hub", 
    layout="wide", 
    page_icon="📊", 
    initial_sidebar_state="collapsed" 
)

# ==========================================
# 1. GLOBAL STATE INITIALIZATION (LANG & CURRENCY)
# ==========================================
if "lang" not in st.session_state: st.session_state.lang = "English"
if "currency" not in st.session_state: st.session_state.currency = "MAD"
if "rates" not in st.session_state: st.session_state.rates = {"MAD": 1.0, "USD": 0.10, "EUR": 0.09}
if "sym" not in st.session_state: st.session_state.sym = {"MAD": "MAD", "USD": "$", "EUR": "€"}

# --- TRANSLATION DICTIONARY FOR APP.PY ---
t = {
    "English": {
        "login_title": "SYSTEM ACCESS", "email": "Corporate Email", "pass": "Password", "auth": "Authenticate", "sys": "**System**",
        "welcome": "👋 Welcome back,", "settings": "⚙️ Settings & Profile", "profile": "**User Profile**", "pref": "**Preferences**",
        "curr_lbl": "Default Currency", "lang_lbl": "Platform Language", "docs": "📖 Platform Docs", "logout": "🚪 Terminate Session",
        "cse": "Casablanca Stock Exchange", "subtitle": "BTP Sector Equity Research & Financial Analytics Hub", "badge": "🇲🇦 Moroccan Market Focus",
        "tracked": "Tracked Companies", "avg_pe": "Sector Average P/E", "top_stock": "Highest Priced Stock", "entities": "Entities",
        "nav": "🚀 Quick Navigation Modules",
        "ca_title": "📉 Corporate Analysis", "ca_desc": "Upload Excel models, run variance analysis, and generate investment teasers.",
        "bb_title": "⚖️ Sector Benchmark", "bb_desc": "Compare target operational margins, liquidity, and ROE against Moroccan peers.",
        "ma_title": "💼 M&A Deal Room", "ma_desc": "Execute LBO Quick-Models, Advanced CAPM, and Monte Carlo DCF simulations.",
        "lc_title": "💹 Live Charts", "lc_desc": "Track real-time market trends, volatility, and historical pricing data.",
        "mh_title": "🗄️ My History", "mh_desc": "Access, manage, and download your previously saved analysis sessions.",
        "ac_title": "👤 About Creator", "ac_desc": "Professional profile, academic background, and networking links.",
        "launch": "Launch Module",
        # Docs Section
        "doc_head": "📖 Financial Methodology & Engine Specs",
        "doc_wacc": "#### ⚙️ 1. Cost of Capital (WACC & CAPM)",
        "doc_wacc_desc": "The platform calculates the Cost of Equity using the Capital Asset Pricing Model (CAPM). For Moroccan targets, the Risk-Free Rate is typically benchmarked against the 10-Year Moroccan Treasury Bond. The resulting WACC is used as the standard discount rate.",
        "doc_dcf": "#### 📊 2. Discounted Cash Flow (DCF)",
        "doc_dcf_desc": "The DCF engine uses a 5-year explicit Free Cash Flow forecast. The Terminal Value is derived via the Gordon Growth Model, assuming a perpetual growth rate aligned with long-term inflation.",
        "doc_lbo": "#### 💰 3. Leveraged Buyout (LBO)",
        "doc_lbo_desc": "The LBO quick-modeler assumes a 5-year holding horizon. Entry and Exit Enterprise Values are driven by EBITDA multiples. Return metrics (IRR & MoIC) evaluate the equity value creation post-debt paydown."
    },
    "Français": {
        "login_title": "ACCÈS SYSTÈME", "email": "Email Professionnel", "pass": "Mot de passe", "auth": "S'authentifier", "sys": "**Système**",
        "welcome": "👋 Bon retour,", "settings": "⚙️ Paramètres & Profil", "profile": "**Profil Utilisateur**", "pref": "**Préférences**",
        "curr_lbl": "Devise par défaut", "lang_lbl": "Langue de la plateforme", "docs": "📖 Documentation", "logout": "🚪 Déconnexion",
        "cse": "Bourse de Casablanca", "subtitle": "Plateforme d'Analyse Financière et Recherche BTP", "badge": "🇲🇦 Focus Marché Marocain",
        "tracked": "Entreprises Suivies", "avg_pe": "P/E Moyen", "top_stock": "Action la plus chère", "entities": "Entités",
        "nav": "🚀 Modules de Navigation Rapide",
        "ca_title": "📉 Analyse d'Entreprise", "ca_desc": "Importez des modèles Excel, analysez les écarts et générez des teasers.",
        "bb_title": "⚖️ Benchmark Sectoriel", "bb_desc": "Comparez les marges, la liquidité et le ROE avec les concurrents marocains.",
        "ma_title": "💼 Salle des Marchés M&A", "ma_desc": "Exécutez des modèles LBO, le MEDAF et des simulations Monte Carlo.",
        "lc_title": "💹 Graphiques en Direct", "lc_desc": "Suivez les tendances du marché, la volatilité et l'historique des prix.",
        "mh_title": "🗄️ Mon Historique", "mh_desc": "Accédez, gérez et téléchargez vos sessions d'analyse précédentes.",
        "ac_title": "👤 À propos du Créateur", "ac_desc": "Profil professionnel, parcours académique et liens de networking.",
        "launch": "Lancer le Module",
        # Docs Section
        "doc_head": "📖 Méthodologie Financière et Spécifications",
        "doc_wacc": "#### ⚙️ 1. Coût du Capital (CMPC & MEDAF)",
        "doc_wacc_desc": "La plateforme calcule le coût des capitaux propres via le MEDAF. Pour les cibles marocaines, le taux sans risque est basé sur les bons du Trésor marocain à 10 ans. Le CMPC obtenu sert de taux d'actualisation.",
        "doc_dcf": "#### 📊 2. Actualisation des Flux de Trésorerie (DCF)",
        "doc_dcf_desc": "Le modèle DCF utilise une prévision explicite des FCF sur 5 ans. La valeur terminale est calculée via le modèle de Gordon Shapiro, supposant un taux de croissance perpétuelle.",
        "doc_lbo": "#### 💰 3. LBO (Rachat par Effet de Levier)",
        "doc_lbo_desc": "Le modèle LBO suppose un horizon de détention de 5 ans. Les valeurs d'entreprise d'entrée et de sortie dépendent des multiples d'EBITDA. Les rendements (TRI & MoIC) évaluent la création de valeur."
    },
    "Español": {
        "login_title": "ACCESO AL SISTEMA", "email": "Correo Corporativo", "pass": "Contraseña", "auth": "Autenticar", "sys": "**Sistema**",
        "welcome": "👋 Bienvenido de nuevo,", "settings": "⚙️ Ajustes y Perfil", "profile": "**Perfil de Usuario**", "pref": "**Preferencias**",
        "curr_lbl": "Moneda predeterminada", "lang_lbl": "Idioma de la plataforma", "docs": "📖 Documentación", "logout": "🚪 Cerrar Sesión",
        "cse": "Bolsa de Casablanca", "subtitle": "Centro de Análisis Financiero de Renta Variable BTP", "badge": "🇲🇦 Enfoque Mercado Marroquí",
        "tracked": "Empresas Seguidas", "avg_pe": "P/E Promedio", "top_stock": "Acción Más Cara", "entities": "Entidades",
        "nav": "🚀 Módulos de Navegación Rápida",
        "ca_title": "📉 Análisis Corporativo", "ca_desc": "Sube modelos Excel, analiza variaciones y genera informes de inversión.",
        "bb_title": "⚖️ Benchmark Sectorial", "bb_desc": "Compara márgenes, liquidez y ROE contra competidores marroquíes.",
        "ma_title": "💼 Sala de Fusiones (M&A)", "ma_desc": "Ejecuta modelos LBO, CAPM y simulaciones Monte Carlo DCF.",
        "lc_title": "💹 Gráficos en Vivo", "lc_desc": "Rastrea tendencias del mercado en tiempo real y datos históricos.",
        "mh_title": "🗄️ Mi Historial", "mh_desc": "Accede, gestiona y descarga tus sesiones de análisis guardadas.",
        "ac_title": "👤 Sobre el Creador", "ac_desc": "Perfil profesional, formación académica y enlaces de networking.",
        "launch": "Iniciar Módulo",
        # Docs Section
        "doc_head": "📖 Metodología Financiera y Especificaciones",
        "doc_wacc": "#### ⚙️ 1. Costo de Capital (WACC y CAPM)",
        "doc_wacc_desc": "La plataforma calcula el Costo del Capital mediante el CAPM. Para objetivos marroquíes, la Tasa Libre de Riesgo se basa en los Bonos del Tesoro a 10 años. El WACC resultante se usa como tasa de descuento.",
        "doc_dcf": "#### 📊 2. Flujo de Caja Descontado (DCF)",
        "doc_dcf_desc": "El motor DCF proyecta flujos de caja libres a 5 años. El Valor Terminal se calcula con el Modelo de Crecimiento de Gordon, asumiendo una tasa de crecimiento perpetuo.",
        "doc_lbo": "#### 💰 3. Compra Apalancada (LBO)",
        "doc_lbo_desc": "El modelo LBO asume un horizonte de inversión de 5 años. Los Valores Empresariales de entrada y salida se basan en múltiplos de EBITDA."
    },
    "العربية": {
        "login_title": "تسجيل الدخول", "email": "البريد الإلكتروني للشركة", "pass": "كلمة المرور", "auth": "دخول", "sys": "**النظام**",
        "welcome": "👋 مرحباً بعودتك،", "settings": "⚙️ الإعدادات والملف الشخصي", "profile": "**الملف الشخصي**", "pref": "**التفضيلات**",
        "curr_lbl": "العملة الافتراضية", "lang_lbl": "لغة المنصة", "docs": "📖 وثائق المنصة", "logout": "🚪 تسجيل الخروج",
        "cse": "بورصة الدار البيضاء", "subtitle": "منصة التحليل المالي وأبحاث أسهم قطاع البناء والأشغال العمومية", "badge": "🇲🇦 تركيز على السوق المغربي",
        "tracked": "الشركات المتابعة", "avg_pe": "متوسط مكرر الربحية", "top_stock": "أغلى سهم", "entities": "شركات",
        "nav": "🚀 وحدات التنقل السريع",
        "ca_title": "📉 تحليل الشركات", "ca_desc": "رفع نماذج الإكسل، تحليل التغيرات، واستخراج تقارير الاستثمار.",
        "bb_title": "⚖️ مقارنة القطاع", "bb_desc": "مقارنة هوامش التشغيل والسيولة والعائد على حقوق المساهمين مع المنافسين.",
        "ma_title": "💼 غرفة صفقات الاندماج والاستحواذ", "ma_desc": "تنفيذ نماذج LBO السريعة، وCAPM المتقدمة، ومحاكاة مونت كارلو.",
        "lc_title": "💹 رسوم بيانية حية", "lc_desc": "تتبع اتجاهات السوق في الوقت الفعلي والبيانات التاريخية للأسعار.",
        "mh_title": "🗄️ السجل الخاص بي", "mh_desc": "الوصول وإدارة وتنزيل جلسات التحليل المحفوظة مسبقًا.",
        "ac_title": "👤 عن المطور", "ac_desc": "الملف المهني والخلفية الأكاديمية وروابط التواصل.",
        "launch": "تشغيل الوحدة",
        # Docs Section
        "doc_head": "📖 المنهجية المالية ومواصفات النظام",
        "doc_wacc": "#### ⚙️ 1. تكلفة رأس المال (WACC و CAPM)",
        "doc_wacc_desc": "تحسب المنصة تكلفة حقوق الملكية باستخدام نموذج (CAPM). بالنسبة للشركات المغربية، يُستند المعدل الخالي من المخاطر عادةً إلى سندات الخزينة المغربية لأجل 10 سنوات. يُستخدم WACC كنسبة خصم لتحديد القيمة الحالية.",
        "doc_dcf": "#### 📊 2. خصم التدفقات النقدية (DCF)",
        "doc_dcf_desc": "يستخدم محرك DCF توقعات التدفقات النقدية الحرة لمدة 5 سنوات. يتم حساب القيمة النهائية (Terminal Value) باستخدام نموذج جوردون للنمو، بافتراض معدل نمو دائم يتماشى مع التضخم طويل الأجل.",
        "doc_lbo": "#### 💰 3. الاستحواذ المدعوم بالقروض (LBO)",
        "doc_lbo_desc": "يفترض نموذج LBO فترة احتفاظ تبلغ 5 سنوات. يتم تحديد قيم الدخول والخروج للشركة بناءً على مضاعفات EBITDA. تقيس العوائد (IRR و MoIC) القيمة الناتجة بعد سداد الديون."
    }
}
lang = st.session_state.lang
txt = t[lang]

# ==========================================
# 2. SUPABASE SETUP
# ==========================================
try:
    supabase = create_client(
        supabase_url=st.secrets["SUPABASE_URL"],
        supabase_key=st.secrets["SUPABASE_KEY"],
        options=ClientOptions(postgrest_client_timeout=10)
    )
except Exception as e:
    st.error(f"Database Connection Error: {e}")
    st.stop()

if "user" not in st.session_state: st.session_state.user = None

# ==========================================
# 3. MODALS & UI COMPONENTS
# ==========================================

@st.dialog(txt["doc_head"], width="large")
def show_docs_modal():
    st.markdown(txt["doc_wacc"])
    st.write(txt["doc_wacc_desc"])
    st.latex(r"K_e = R_f + \beta \times (R_m - R_f)")
    
    st.markdown("---")
    st.markdown(txt["doc_dcf"])
    st.write(txt["doc_dcf_desc"])
    st.latex(r"TV = \frac{FCF_5 \times (1 + g)}{WACC - g}")
    
    st.markdown("---")
    st.markdown(txt["doc_lbo"])
    st.write(txt["doc_lbo_desc"])
    st.latex(r"MoIC = \frac{\text{Exit Equity}}{\text{Entry Equity}}")

# Explicitly protect the sidebar and header from RTL flipping
if lang == "العربية":
    rtl_css = """
    .block-container { direction: rtl; text-align: right; }
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"], [data-testid="stHeader"] { direction: ltr !important; text-align: left !important; }
    """
else:
    rtl_css = ""

st.markdown(f"""
<style>
    [data-testid="stSidebarNav"] li:first-child a span {{ display: none !important; }}
    [data-testid="stSidebarNav"] li:first-child a::after {{ content: "🏠 Home"; font-size: 15px; margin-left: 0px; }}
    
    .full-width-banner {{ position: relative; width: 100%; height: 250px; background-image: url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop'); background-size: cover; background-position: center; margin-bottom: 2rem; border-radius: 10px; border-left: 5px solid #c1272d; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
    .banner-overlay {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, rgba(14,17,23,1) 0%, rgba(14,17,23,0.8) 40%, rgba(193,39,45,0.2) 100%); }}
    .banner-content {{ position: absolute; top: 50%; left: 30px; transform: translateY(-50%); z-index: 2; }}
    .moroccan-badge {{ display: inline-block; background: rgba(193,39,45,0.2); border: 1px solid #c1272d; padding: 5px 15px; border-radius: 20px; color: white; font-size: 0.9rem; margin-top: 15px; font-weight: bold; }}
    
    .overview-container {{ display: flex; justify-content: space-around; background-color: #161a22; padding: 20px; border-radius: 8px; border-top: 3px solid #333; margin-bottom: 30px;}}
    .overview-item {{ text-align: center; }}
    .overview-label {{ margin: 0; color: #b3b3b3; font-size: 14px; margin-bottom: 5px; }}
    .overview-value {{ margin: 0; color: white; font-size: 24px; font-weight: bold; }}
    
    {rtl_css}
</style>
""", unsafe_allow_html=True)

if st.session_state.user is None:
    st.markdown("<style>[data-testid='stSidebar'] { display: none !important; } [data-testid='collapsedControl'] { display: none !important; }</style>", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_dashboard_data():
    try:
        df = pd.read_csv("btp_market_data.csv")
        df["PE_Ratio"] = pd.to_numeric(df["PE_Ratio"], errors='coerce')
        df["Price_MAD"] = pd.to_numeric(df["Price_MAD"], errors='coerce')
        return df
    except Exception: return None

# ==========================================
# 4. ROUTING & UI
# ==========================================
if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_info, col_auth = st.columns([1.5, 1], gap="large")
    
    with col_info:
        st.image("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?q=80&w=2070&auto=format&fit=crop", use_container_width=True)
        st.markdown(f"## 📊 {txt['cse']}")
        st.markdown(f"<p style='color: #b3b3b3; font-size: 1.1rem;'>{txt['subtitle']}</p>", unsafe_allow_html=True)
        
    with col_auth:
        with st.container(border=True):
            st.markdown(f"<h3 style='text-align: center; color: white; margin-top: 5px; margin-bottom: 0;'>{txt['login_title']}</h3>", unsafe_allow_html=True)
            st.markdown("<hr style='border: 1px solid #c1272d; margin-top: 10px; margin-bottom: 20px; width: 50%; margin-left: auto; margin-right: auto;'>", unsafe_allow_html=True)
            
            choice = st.radio("Action", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
            email = st.text_input(txt['email'], placeholder="email@domain.com")
            password = st.text_input(txt['pass'], type="password")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(txt['auth'], use_container_width=True, type="primary"):
                if choice == "Login":
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.user = res.user
                        st.rerun()
                    except Exception: st.error("Login Error: Invalid credentials or user not found.")
                else:
                    try:
                        supabase.auth.sign_up({"email": email, "password": password})
                        st.success("Account created successfully! Switch to Login.")
                    except Exception as e: st.error(f"Sign Up Error: {str(e)}")

else:
    # --- HEADER & SETTINGS ---
    top_col1, top_col2 = st.columns([4, 1])
    with top_col1:
        user_name = st.session_state.user.email.split('@')[0].capitalize()
        st.markdown(f"<h4 style='color: #e0e0e0; margin-top: 10px;'>{txt['welcome']} {user_name}</h4>", unsafe_allow_html=True)
    
    with top_col2:
        with st.popover(txt['settings'], use_container_width=True):
            st.markdown(txt['profile'])
            st.write(f"📧 {st.session_state.user.email}")
            st.divider()
            
            st.markdown(txt['pref'])
            langs = ["English", "Français", "Español", "العربية"]
            currs = ["MAD", "USD", "EUR"]
            
            new_lang = st.selectbox(txt['lang_lbl'], langs, index=langs.index(st.session_state.lang))
            new_curr = st.selectbox(txt['curr_lbl'], currs, index=currs.index(st.session_state.currency))
            
            if new_lang != st.session_state.lang or new_curr != st.session_state.currency:
                st.session_state.lang = new_lang
                st.session_state.currency = new_curr
                st.rerun()
                
            st.divider()
            st.markdown(txt['sys'])
            
            # TRIGGER MODAL INSTEAD OF COMING SOON
            if st.button(txt['docs'], use_container_width=True): 
                show_docs_modal()
                
            if st.button(txt['logout'], type="primary", use_container_width=True):
                supabase.auth.sign_out()
                st.session_state.user = None
                st.rerun()
                
    st.markdown("<br>", unsafe_allow_html=True)

    # --- BANNER ---
    st.markdown(f"""
    <div class="full-width-banner">
        <div class="banner-overlay"></div>
        <div class="banner-content" {'dir="rtl"' if lang=="العربية" else ''}>
            <h1 style="color: white; margin: 0; font-size: 2.8rem; letter-spacing: 1px;">{txt['cse']}</h1>
            <p style="color:#e0e0e0; font-size:1.3rem; margin: 5px 0 0 0;">{txt['subtitle']}</p>
            <div class="moroccan-badge">{txt['badge']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    df_dash = get_dashboard_data()
    if df_dash is not None:
        avg_pe = df_dash["PE_Ratio"].mean()
        tracked_count = len(df_dash)
        
        # APPLY CURRENCY CONVERSION TO HOME PAGE
        rate = st.session_state.rates[st.session_state.currency]
        symbol = st.session_state.sym[st.session_state.currency]
        
        top_stock_row = df_dash.loc[df_dash["Price_MAD"].idxmax()]
        top_stock_name = top_stock_row["Company"]
        top_stock_val = top_stock_row["Price_MAD"] * rate
        
        st.markdown(f"""
        <div class="overview-container" {'dir="rtl"' if lang=="العربية" else ''}>
            <div class="overview-item">
                <p class="overview-label">{txt['tracked']}</p>
                <p class="overview-value">{tracked_count} {txt['entities']}</p>
            </div>
            <div class="overview-item">
                <p class="overview-label">{txt['avg_pe']}</p>
                <p class="overview-value">{avg_pe:.1f}x</p>
            </div>
            <div class="overview-item">
                <p class="overview-label">{txt['top_stock']}</p>
                <p class="overview-value">{top_stock_name} <span style="font-size:16px; color:#2ca02c;">({top_stock_val:,.2f} {symbol})</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"### {txt['nav']}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ROW 1
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown(f"<h4 style='color:#1f77b4; margin-top:0;'>{txt['ca_title']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b3b3b3; font-size:0.85rem; height:45px;'>{txt['ca_desc']}</p>", unsafe_allow_html=True)
            if st.button(txt['launch'], key="b1", use_container_width=True): st.switch_page("pages/1_Corporate_Analysis.py")
    with c2:
        with st.container(border=True):
            st.markdown(f"<h4 style='color:#2ca02c; margin-top:0;'>{txt['bb_title']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b3b3b3; font-size:0.85rem; height:45px;'>{txt['bb_desc']}</p>", unsafe_allow_html=True)
            if st.button(txt['launch'], key="b2", use_container_width=True): st.switch_page("pages/2_BTP_Benchmark.py")
    with c3:
        with st.container(border=True):
            st.markdown(f"<h4 style='color:#9467bd; margin-top:0;'>{txt['ma_title']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b3b3b3; font-size:0.85rem; height:45px;'>{txt['ma_desc']}</p>", unsafe_allow_html=True)
            if st.button(txt['launch'], key="b3", use_container_width=True): st.switch_page("pages/3_MA_Valuation.py")
    
    # ROW 2
    c4, c5, c6 = st.columns(3)
    with c4:
        with st.container(border=True):
            st.markdown(f"<h4 style='color:#d62728; margin-top:0;'>{txt['lc_title']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b3b3b3; font-size:0.85rem; height:45px;'>{txt['lc_desc']}</p>", unsafe_allow_html=True)
            if st.button(txt['launch'], key="b4", use_container_width=True): st.switch_page("pages/4_Live_Charts.py")
    with c5:
        with st.container(border=True):
            st.markdown(f"<h4 style='color:#ff7f0e; margin-top:0;'>{txt['mh_title']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b3b3b3; font-size:0.85rem; height:45px;'>{txt['mh_desc']}</p>", unsafe_allow_html=True)
            if st.button(txt['launch'], key="b5", use_container_width=True): st.switch_page("pages/6_My_History.py")
    with c6:
        with st.container(border=True):
            st.markdown(f"<h4 style='color:#17becf; margin-top:0;'>{txt['ac_title']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b3b3b3; font-size:0.85rem; height:45px;'>{txt['ac_desc']}</p>", unsafe_allow_html=True)
            if st.button(txt['launch'], key="b6", use_container_width=True): st.switch_page("pages/5_About_Creator.py")
