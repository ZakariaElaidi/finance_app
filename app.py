import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime
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
        "dev_by": "👨‍💻 Engineered by",
        "tracked": "Tracked Companies", "avg_pe": "Sector Average P/E", "prem_stock": "Premium Stock", "value_stock": "Value Stock (Lowest P/E)", "entities": "Entities",
        
        # --- NEW PIPELINE TEXTS ---
        "nav": "🔄 The M&A Transaction Pipeline",
        "p1_title": "1️⃣ Deal Origination", "p1_desc": "Screen live market data to identify undervalued targets within the Moroccan sector.",
        "p2_title": "2️⃣ Valuation & Advisory", "p2_desc": "Analyze historical financials, run variance reports, and execute standard DCF valuations.",
        "p3_title": "3️⃣ Buyout Structuring", "p3_desc": "Structure LBO scenarios, assess debt capacity, and run Monte Carlo risk simulations.",
        "nav_tools": "🛠️ Additional Tools & Archive",
        
        "lc_title": "💹 Live Charts", "lc_desc": "Track real-time market trends, volatility, and historical pricing data.",
        "mh_title": "🗄️ My History", "mh_desc": "Access, manage, and download your previously saved analysis sessions.",
        "ac_title": "👤 About Creator", "ac_desc": "Professional profile, academic background, and networking links.",
        "launch": "Launch Module",
        "recent_act": "⏱️ Recent Sessions", "view_hist": "View Full History", "no_recent": "No recent sessions found.",
        "guest_btn": "🚀 Continue as Guest",
        "macro_title": "🌍 Global Macro Indicators", "masi": "MASI (Morocco)", "sp500": "S&P 500 (US)", "cac40": "CAC 40 (France)",
        "chart_title": "📊 Live Market Prices Overview", "quote_title": "💡 Daily Financial Insight",
        "cta_title": "Looking for a top-tier Financial Analyst?", "cta_desc": "Let's build the future of M&A and Private Equity together.", "cta_btn": "📩 Connect on LinkedIn",
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
        "dev_by": "👨‍💻 Conçu par",
        "tracked": "Entreprises Suivies", "avg_pe": "P/E Moyen", "prem_stock": "Action Premium", "value_stock": "Action de Valeur (P/E bas)", "entities": "Entités",
        
        # --- NEW PIPELINE TEXTS ---
        "nav": "🔄 Pipeline des Transactions M&A",
        "p1_title": "1️⃣ Origination de Deals", "p1_desc": "Analysez le marché en direct pour identifier des cibles sous-évaluées dans le secteur.",
        "p2_title": "2️⃣ Valorisation & Conseil", "p2_desc": "Analysez l'historique, les écarts financiers et exécutez des valorisations DCF.",
        "p3_title": "3️⃣ Structuration LBO", "p3_desc": "Structurez des scénarios LBO, évaluez la capacité d'endettement et lancez Monte Carlo.",
        "nav_tools": "🛠️ Outils Additionnels & Archives",
        
        "lc_title": "💹 Graphiques en Direct", "lc_desc": "Suivez les tendances du marché, la volatilité et l'historique des prix.",
        "mh_title": "🗄️ Mon Historique", "mh_desc": "Accédez, gérez et téléchargez vos sessions d'analyse précédentes.",
        "ac_title": "👤 À propos du Créateur", "ac_desc": "Profil professionnel, parcours académique et liens de networking.",
        "launch": "Lancer le Module",
        "recent_act": "⏱️ Sessions Récentes", "view_hist": "Voir l'historique complet", "no_recent": "Aucune session récente trouvée.",
        "guest_btn": "🚀 Continuer en tant qu'invité",
        "macro_title": "🌍 Indicateurs Macro Globaux", "masi": "MASI (Maroc)", "sp500": "S&P 500 (US)", "cac40": "CAC 40 (France)",
        "chart_title": "📊 Aperçu des Prix du Marché", "quote_title": "💡 Perspective Financière du Jour",
        "cta_title": "À la recherche d'un Analyste Financier de haut niveau ?", "cta_desc": "Construisons ensemble l'avenir du M&A et du Private Equity.", "cta_btn": "📩 Me contacter sur LinkedIn",
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
        "dev_by": "👨‍💻 Desarrollado por",
        "tracked": "Empresas Seguidas", "avg_pe": "P/E Promedio", "prem_stock": "Acción Premium", "value_stock": "Acción de Valor (P/E bajo)", "entities": "Entidades",
        
        # --- NEW PIPELINE TEXTS ---
        "nav": "🔄 Pipeline de Transacciones M&A",
        "p1_title": "1️⃣ Originación de Acuerdos", "p1_desc": "Filtra datos del mercado en vivo para identificar objetivos infravalorados en el sector.",
        "p2_title": "2️⃣ Valoración y Asesoría", "p2_desc": "Analiza finanzas históricas, ejecuta informes de variaciones y valoraciones DCF.",
        "p3_title": "3️⃣ Estructuración LBO", "p3_desc": "Estructura escenarios LBO, evalúa capacidad de deuda y simulaciones Monte Carlo.",
        "nav_tools": "🛠️ Herramientas Adicionales y Archivo",
        
        "lc_title": "💹 Gráficos en Vivo", "lc_desc": "Rastrea tendencias del mercado en tiempo real y datos históricos.",
        "mh_title": "🗄️ Mi Historial", "mh_desc": "Accede, gestiona y descarga tus sesiones de análisis guardadas.",
        "ac_title": "👤 Sobre el Creador", "ac_desc": "Perfil profesional, formación académica y enlaces de networking.",
        "launch": "Iniciar Módulo",
        "recent_act": "⏱️ Sesiones Recientes", "view_hist": "Ver historial completo", "no_recent": "No se encontraron sesiones recientes.",
        "guest_btn": "🚀 Continuar como Invitado",
        "macro_title": "🌍 Indicadores Macro Globales", "masi": "MASI (Marruecos)", "sp500": "S&P 500 (EE.UU.)", "cac40": "CAC 40 (Francia)",
        "chart_title": "📊 Resumen de Precios del Mercado", "quote_title": "💡 Perspectiva Financiera Diaria",
        "cta_title": "¿Buscas un Analista Financiero de primer nivel?", "cta_desc": "Construyamos juntos el futuro del M&A y Capital Privado.", "cta_btn": "📩 Conectar en LinkedIn",
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
        "dev_by": "👨‍💻 تم التطوير بواسطة",
        "tracked": "الشركات المتابعة", "avg_pe": "متوسط مكرر الربحية", "prem_stock": "السهم الأغلى", "value_stock": "أفضل قيمة (أقل P/E)", "entities": "شركات",
        
        # --- NEW PIPELINE TEXTS ---
        "nav": "🔄 مسار صفقات الاندماج والاستحواذ",
        "p1_title": "1️⃣ اكتشاف الصفقات", "p1_desc": "فرز بيانات السوق الحية لتحديد الشركات المقيمة بأقل من قيمتها الحقيقية.",
        "p2_title": "2️⃣ التقييم والاستشارات", "p2_desc": "تحليل البيانات المالية التاريخية، وتقييم التدفقات النقدية المخصومة (DCF).",
        "p3_title": "3️⃣ هيكلة الاستحواذ", "p3_desc": "هيكلة سيناريوهات LBO، تقييم قدرة الديون، ومحاكاة مخاطر مونت كارلو.",
        "nav_tools": "🛠️ أدوات إضافية وأرشيف",
        
        "lc_title": "💹 رسوم بيانية حية", "lc_desc": "تتبع اتجاهات السوق في الوقت الفعلي والبيانات التاريخية للأسعار.",
        "mh_title": "🗄️ السجل الخاص بي", "mh_desc": "الوصول وإدارة وتنزيل جلسات التحليل المالي المحفوظة مسبقًا.",
        "ac_title": "👤 عن المطور", "ac_desc": "الملف المهني والخلفية الأكاديمية وروابط التواصل.",
        "launch": "تشغيل الوحدة",
        "recent_act": "⏱️ الجلسات الأخيرة", "view_hist": "عرض السجل الكامل", "no_recent": "لم يتم العثور على جلسات أخيرة.",
        "guest_btn": "🚀 المتابعة كضيف",
        "macro_title": "🌍 المؤشرات الماكرو-اقتصادية الكبرى", "masi": "مازي (المغرب)", "sp500": "إس آند بي 500 (أمريكا)", "cac40": "كاك 40 (فرنسا)",
        "chart_title": "📊 نظرة عامة على أسعار السوق", "quote_title": "💡 حكمة مالية اليوم",
        "cta_title": "هل تبحث عن محلل مالي محترف لتعزيز فريقك؟", "cta_desc": "دعنا نبني مستقبل عمليات الاندماج والاستحواذ معاً.", "cta_btn": "📩 تواصل معي عبر لينكد إن",
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

# --- EXPANDED QUOTES LIST ---
quotes = [
    "“Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1.” – Warren Buffett",
    "“Price is what you pay. Value is what you get.” – Warren Buffett",
    "“The stock market is a device for transferring money from the impatient to the patient.” – Warren Buffett",
    "“In investing, what is comfortable is rarely profitable.” – Robert Arnott",
    "“The individual investor should act consistently as an investor and not as a speculator.” – Benjamin Graham",
    "“Know what you own, and know why you own it.” – Peter Lynch",
    "“Compound interest is the eighth wonder of the world. He who understands it, earns it.” – Albert Einstein",
    "“The four most dangerous words in investing are: 'this time it's different.'” – Sir John Templeton",
    "“Behind every stock is a company. Find out what it's doing.” – Peter Lynch",
    "“Courage taught me no matter how bad a crisis gets... any sound investment will eventually pay off.” – Carlos Slim"
]
todays_quote = quotes[datetime.today().day % len(quotes)]

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

def get_recent_history(user_id):
    try:
        res = supabase.table("users_history").select("id, created_at, work_data").eq("user_id", user_id).order("created_at", desc=True).limit(2).execute()
        return res.data
    except Exception: return []

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
    /* PREVENT HORIZONTAL SCROLL (TSWIPA FIX) */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        overflow-x: hidden !important;
    }}

    /* Global Fade-in Animation */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(15px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .block-container {{ animation: fadeIn 0.6s ease-out; overflow-x: hidden !important; }}

    [data-testid="stSidebarNav"] li:first-child a span {{ display: none !important; }}
    [data-testid="stSidebarNav"] li:first-child a::after {{ content: "🏠 Home"; font-size: 15px; margin-left: 0px; }}
    
    /* Elegant Banner */
    .full-width-banner {{ position: relative; width: 100%; height: 260px; background-image: url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop'); background-size: cover; background-position: center; margin-bottom: 1.5rem; border-radius: 12px; border-left: 6px solid #c1272d; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }}
    .banner-overlay {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, rgba(14,17,23,1) 0%, rgba(14,17,23,0.85) 40%, rgba(193,39,45,0.2) 100%); }}
    .banner-content {{ position: absolute; top: 50%; left: 40px; transform: translateY(-50%); z-index: 2; }}
    .moroccan-badge {{ display: inline-block; background: rgba(193,39,45,0.25); border: 1px solid #c1272d; padding: 6px 18px; border-radius: 25px; color: white; font-size: 0.9rem; margin-top: 15px; font-weight: bold; backdrop-filter: blur(4px); }}
    
    /* Macro Badges */
    .macro-card {{ background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 8px; padding: 12px 20px; border-left: 4px solid #1f77b4; box-shadow: 0 4px 10px rgba(0,0,0,0.2); transition: transform 0.3s ease, box-shadow 0.3s ease; display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }}
    .macro-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.4); border-left-color: #2ca02c; }}
    .macro-name {{ color: #a0aab5; font-size: 14px; margin: 0; font-weight: bold; text-transform: uppercase; }}
    .macro-val {{ color: white; font-size: 18px; margin: 0; font-weight: bold; }}
    .macro-pos {{ color: #2ca02c; font-size: 14px; font-weight: bold; }}
    .macro-neg {{ color: #d62728; font-size: 14px; font-weight: bold; }}
    
    /* Safe Ticker Tape CSS to prevent horizontal scroll */
    .ticker-wrap {{ width: 100%; overflow: hidden; background-color: #0e1117; white-space: nowrap; border-top: 1px solid rgba(255,255,255,0.1); border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 25px; box-sizing: border-box; }}
    .ticker {{ display: inline-block; animation: ticker 35s linear infinite; padding-left: 100%; }}
    @keyframes ticker {{ 0% {{ transform: translate3d(0, 0, 0); }} 100% {{ transform: translate3d(-100%, 0, 0); }} }}
    .ticker__item {{ display: inline-block; padding: 10px 2rem; font-size: 14px; color: #b3b3b3; font-weight: bold; }}
    .ticker__val {{ color: #2ca02c; margin-left: 5px; }}

    /* Glassmorphism Stats Container */
    .overview-container {{ display: flex; justify-content: space-around; background: rgba(22, 26, 34, 0.6); backdrop-filter: blur(10px); padding: 25px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); border-top: 3px solid #c1272d; margin-bottom: 25px; flex-wrap: wrap; gap: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }}
    .overview-item {{ text-align: center; flex: 1; min-width: 200px; transition: transform 0.3s ease; }}
    .overview-item:hover {{ transform: translateY(-3px); }}
    .overview-label {{ margin: 0; color: #a0aab5; font-size: 15px; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; }}
    .overview-value {{ margin: 0; color: white; font-size: 26px; font-weight: 800; text-shadow: 0 0 15px rgba(255,255,255,0.15); }}
    
    /* Quote Box */
    .quote-box {{ background: linear-gradient(145deg, rgba(22,26,34,0.6), rgba(30,34,43,0.8)); border-left: 4px solid #f5b041; border-radius: 8px; padding: 15px 20px; font-style: italic; color: #e0e0e0; margin-bottom: 25px; display: flex; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }}
    
    /* CTA Banner */
    .cta-banner {{ background: linear-gradient(135deg, #161a22, #1f2937); border-radius: 12px; padding: 30px; text-align: center; border: 1px solid #1f77b4; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-top: 35px; margin-bottom: 20px; }}
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(31, 119, 180, 0.7); }} 70% {{ box-shadow: 0 0 0 15px rgba(31, 119, 180, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(31, 119, 180, 0); }} }}
    .cta-btn {{ background-color: #1f77b4; color: white !important; font-weight: bold; padding: 12px 30px; border-radius: 30px; text-decoration: none; display: inline-block; margin-top: 15px; transition: all 0.3s ease; animation: pulse 2s infinite; }}
    .cta-btn:hover {{ background-color: #135d90; transform: scale(1.05); text-decoration: none; }}

    /* Interactive Navigation Cards */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(h4) {{
        transition: all 0.3s ease;
        background: linear-gradient(145deg, rgba(30,34,43,0.4), rgba(22,26,34,0.8));
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(h4):hover {{
        transform: translateY(-8px);
        box-shadow: 0 12px 25px rgba(0,0,0,0.5);
        border-color: rgba(255,255,255,0.2) !important;
    }}
    
    /* Recent Activity Card */
    .recent-card {{ background: rgba(255,255,255,0.03); border-left: 3px solid #ff7f0e; padding: 15px 20px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
    .recent-card h5 {{ margin: 0; color: #fff; font-size: 16px; }}
    .recent-card p {{ margin: 0; color: #b3b3b3; font-size: 13px; }}

    {rtl_css}
    
    /* MOBILE RESPONSIVENESS HACKS */
    @media (max-width: 768px) {{
        .block-container {{ padding-top: 2rem !important; padding-left: 0.8rem !important; padding-right: 0.8rem !important; }}
        .full-width-banner h1 {{ font-size: 1.8rem !important; }}
        .full-width-banner p {{ font-size: 1rem !important; }}
        .banner-content {{ left: 20px; }}
        .overview-container {{ flex-direction: column; align-items: center; padding: 15px; }}
        .overview-item {{ width: 100%; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 15px; }}
        .overview-item:last-child {{ border-bottom: none; padding-bottom: 0; margin-bottom: 0; }}
        [data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; margin-bottom: 15px !important; }}
        .macro-card {{ flex-direction: column; align-items: flex-start; gap: 5px; }}
    }}
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
        st.markdown(f"<p style='color: #b3b3b3; font-size: 1.1rem; margin-bottom: 5px;'>{txt['subtitle']}</p>", unsafe_allow_html=True)
        
        # --- Premium Developer Badge ---
        st.markdown(f"""
        <div style='display: inline-block; margin-top: 15px; margin-bottom: 20px; padding: 8px 18px; background: linear-gradient(90deg, rgba(22,26,34,0.8) 0%, rgba(245,176,65,0.15) 100%); border-left: 4px solid #f5b041; border-radius: 6px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);'>
            <span style='color: #a0aab5; font-size: 0.95rem; font-weight: 500; letter-spacing: 0.5px;'>{txt['dev_by']} </span>
            <span style='color: #f5b041; font-size: 1.05rem; font-weight: 900; letter-spacing: 1px;'>ZAKARIA ELAIDI</span>
        </div>
        """, unsafe_allow_html=True)
        
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
            
            # --- GUEST BUTTON ---
            st.markdown("<div style='text-align:center; color:#b3b3b3; margin: 15px 0;'>— OR —</div>", unsafe_allow_html=True)
            if st.button(txt['guest_btn'], use_container_width=True):
                st.session_state.user = type('Guest', (), {'email': 'guest@portfolio.com', 'id': 'guest_123'})()
                st.rerun()

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
            
            if st.button(txt['docs'], use_container_width=True): 
                show_docs_modal()
                
            if st.button(txt['logout'], type="primary", use_container_width=True):
                if st.session_state.user.email != 'guest@portfolio.com':
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
    
    # --- MACRO-ECONOMIC BADGES ---
    mac_col1, mac_col2, mac_col3 = st.columns(3)
    with mac_col1:
        st.markdown(f"""<div class="macro-card"><div><p class="macro-name">{txt['masi']}</p><p class="macro-val">13,245.80</p></div><div class="macro-pos">+0.42% ▲</div></div>""", unsafe_allow_html=True)
    with mac_col2:
        st.markdown(f"""<div class="macro-card"><div><p class="macro-name">{txt['sp500']}</p><p class="macro-val">5,431.60</p></div><div class="macro-pos">+1.12% ▲</div></div>""", unsafe_allow_html=True)
    with mac_col3:
        st.markdown(f"""<div class="macro-card" style="border-left-color: #d62728;"><div><p class="macro-name">{txt['cac40']}</p><p class="macro-val">7,932.10</p></div><div class="macro-neg">-0.24% ▼</div></div>""", unsafe_allow_html=True)

    df_dash = get_dashboard_data()
    if df_dash is not None:
        rate = st.session_state.rates[st.session_state.currency]
        symbol = st.session_state.sym[st.session_state.currency]
        
        # Build Live Ticker
        ticker_items = "".join([f"<div class='ticker__item'>{row['Company']}: <span class='ticker__val'>{row['Price_MAD'] * rate:,.2f} {symbol}</span></div>" for _, row in df_dash.iterrows()])
        st.markdown(f"<div class='ticker-wrap' {'dir=\"ltr\"'}><div class='ticker'>{ticker_items}</div></div>", unsafe_allow_html=True)
        
        # Calculate Smart Stats
        avg_pe = df_dash["PE_Ratio"].mean()
        prem_stock_row = df_dash.loc[df_dash["Price_MAD"].idxmax()]
        prem_stock_name = prem_stock_row["Company"]
        prem_stock_val = prem_stock_row["Price_MAD"] * rate
        value_stock_row = df_dash.loc[df_dash["PE_Ratio"].idxmin()]
        value_stock_name = value_stock_row["Company"]
        value_stock_pe = value_stock_row["PE_Ratio"]
        
        st.markdown(f"""
        <div class="overview-container" {'dir="rtl"' if lang=="العربية" else ''}>
            <div class="overview-item">
                <p class="overview-label">{txt['avg_pe']}</p>
                <p class="overview-value">{avg_pe:.1f}x</p>
            </div>
            <div class="overview-item">
                <p class="overview-label">{txt['prem_stock']}</p>
                <p class="overview-value">{prem_stock_name} <span style="font-size:16px; color:#2ca02c;">({prem_stock_val:,.2f} {symbol})</span></p>
            </div>
            <div class="overview-item">
                <p class="overview-label">{txt['value_stock']}</p>
                <p class="overview-value">{value_stock_name} <span style="font-size:16px; color:#1f77b4;">({value_stock_pe:.1f}x)</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- MINI MARKET CHART ---
        st.markdown(f"#### {txt['chart_title']}")
        df_dash['Converted_Price'] = df_dash['Price_MAD'] * rate
        fig_mini = px.bar(df_dash, x="Company", y="Converted_Price", color="Converted_Price", color_continuous_scale="Viridis")
        fig_mini.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False, xaxis_title="", yaxis_title=f"Price ({symbol})", xaxis_tickangle=-45)
        st.plotly_chart(fig_mini, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # --- RECENT ACTIVITY SECTION ---
    if st.session_state.user.email != 'guest@portfolio.com':
        recent_sessions = get_recent_history(st.session_state.user.id)
        if recent_sessions:
            st.markdown(f"### {txt['recent_act']}")
            c_hist1, c_hist2 = st.columns([3, 1])
            with c_hist1:
                for item in recent_sessions:
                    data = json.loads(item['work_data'])
                    s_name = data.get('Session_Name', f"Session: {item['created_at'][:10]}")
                    s_date = data.get('Date', item['created_at'][:10])
                    st.markdown(f"""
                    <div class="recent-card" {'dir="rtl"' if lang=="العربية" else ''}>
                        <div><h5>{s_name}</h5><p>{s_date}</p></div>
                        <div><span style="color:#2ca02c; font-weight:bold;">{data.get('Revenue', 0) * st.session_state.rates[st.session_state.currency]:,.0f} {st.session_state.sym[st.session_state.currency]}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
            with c_hist2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(txt['view_hist'], use_container_width=True): st.switch_page("pages/6_My_History.py")
            st.markdown("<br>", unsafe_allow_html=True)

    # --- DAILY QUOTE ---
    st.markdown(f"""
    <div class="quote-box" {'dir="rtl"' if lang=="العربية" else ''}>
        <div style="font-size: 24px; margin-right: 15px;">{txt['quote_title'].split()[0]}</div>
        <div>
            <span style="font-size: 1.1rem;">{todays_quote}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- NEW: THE PIPELINE NAVIGATION ---
    st.markdown(f"### {txt['nav']}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ROW 1 (The M&A Pipeline)
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown(f"<h4 style='color:#1f77b4; margin-top:0;'>{txt['p1_title']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b3b3b3; font-size:0.85rem; height:45px;'>{txt['p1_desc']}</p>", unsafe_allow_html=True)
            if st.button(txt['launch'], key="b1", use_container_width=True): st.switch_page("pages/2_BTP_Benchmark.py")
    with c2:
        with st.container(border=True):
            st.markdown(f"<h4 style='color:#2ca02c; margin-top:0;'>{txt['p2_title']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b3b3b3; font-size:0.85rem; height:45px;'>{txt['p2_desc']}</p>", unsafe_allow_html=True)
            if st.button(txt['launch'], key="b2", use_container_width=True): st.switch_page("pages/1_Corporate_Analysis.py")
    with c3:
        with st.container(border=True):
            st.markdown(f"<h4 style='color:#9467bd; margin-top:0;'>{txt['p3_title']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b3b3b3; font-size:0.85rem; height:45px;'>{txt['p3_desc']}</p>", unsafe_allow_html=True)
            if st.button(txt['launch'], key="b3", use_container_width=True): st.switch_page("pages/3_MA_Valuation.py")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### {txt['nav_tools']}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ROW 2 (Tools & Archive)
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

    # --- CTA BANNER FOR RECRUITERS ---
    st.markdown(f"""
    <div class="cta-banner" {'dir="rtl"' if lang=="العربية" else ''}>
        <h2 style="color: white; margin-bottom: 5px;">{txt['cta_title']}</h2>
        <p style="color: #a0aab5; font-size: 1.1rem; margin-bottom: 5px;">{txt['cta_desc']}</p>
        <a href="https://www.linkedin.com/in/zakaria-elaidi/" target="_blank" class="cta-btn">{txt['cta_btn']}</a>
    </div>
    """, unsafe_allow_html=True)
