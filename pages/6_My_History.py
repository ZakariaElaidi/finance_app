import streamlit as st
import json
from supabase import create_client, ClientOptions

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
        "title": "🗄️ Database Records & History", "no_rec": "No records found in database. Save an analysis from the Corporate Analysis tab first.",
        "date": "Date Recorded:", "rev": "Revenue:", "nm": "Net Margin:", "roe": "ROE:", "cr": "Current Ratio:",
        "ren_lbl": "Rename Session", "ren_btn": "✏️ Update Name", "del_btn": "🗑️ Delete",
        "ren_succ": "Renamed successfully!", "del_succ": "Deleted!"
    },
    "Français": {
        "title": "🗄️ Enregistrements & Historique", "no_rec": "Aucun enregistrement trouvé. Sauvegardez d'abord une analyse depuis l'onglet Analyse d'Entreprise.",
        "date": "Date d'enregistrement :", "rev": "Revenus :", "nm": "Marge Nette :", "roe": "ROE :", "cr": "Ratio de Liquidité :",
        "ren_lbl": "Renommer la session", "ren_btn": "✏️ Mettre à jour", "del_btn": "🗑️ Supprimer",
        "ren_succ": "Renommé avec succès !", "del_succ": "Supprimé !"
    },
    "Español": {
        "title": "🗄️ Registros e Historial", "no_rec": "No se encontraron registros. Guarda un análisis desde la pestaña de Análisis Corporativo primero.",
        "date": "Fecha de registro:", "rev": "Ingresos:", "nm": "Margen Neto:", "roe": "ROE:", "cr": "Ratio de Liquidez:",
        "ren_lbl": "Renombrar sesión", "ren_btn": "✏️ Actualizar nombre", "del_btn": "🗑️ Eliminar",
        "ren_succ": "¡Renombrado exitosamente!", "del_succ": "¡Eliminado!"
    },
    "العربية": {
        "title": "🗄️ السجلات والتاريخ", "no_rec": "لم يتم العثور على سجلات. احفظ تحليلاً من علامة تبويب تحليل الشركات أولاً.",
        "date": "تاريخ التسجيل:", "rev": "الإيرادات:", "nm": "هامش الربح الصافي:", "roe": "العائد على حقوق المساهمين:", "cr": "نسبة التداول:",
        "ren_lbl": "إعادة تسمية الجلسة", "ren_btn": "✏️ تحديث الاسم", "del_btn": "🗑️ حذف",
        "ren_succ": "تمت إعادة التسمية بنجاح!", "del_succ": "تم الحذف!"
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
    {rtl_css}
</style>
""", unsafe_allow_html=True)

st.title(txt["title"])

# --- SUPABASE INIT & FUNCTIONS ---
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"], options=ClientOptions(postgrest_client_timeout=10))
except Exception:
    st.error("Database connection failed.")
    st.stop()

def get_history(user_id):
    try:
        res = supabase.table("users_history").select("id, created_at, work_data").eq("user_id", user_id).order("created_at", desc=True).execute()
        return res.data
    except Exception: return []

def delete_session(session_id):
    try:
        supabase.table("users_history").delete().eq("id", session_id).execute()
        return True
    except Exception: return False

def update_session_name(session_id, current_data, new_name):
    try:
        current_data["Session_Name"] = new_name
        supabase.table("users_history").update({"work_data": json.dumps(current_data)}).eq("id", session_id).execute()
        return True
    except Exception: return False

hist = get_history(st.session_state.user.id)

# --- UI LOGIC ---
if len(hist) == 0:
    st.info(txt["no_rec"])
else:
    for item in hist:
        session_id = item['id']
        date_str = item['created_at'][:10]
        data = json.loads(item['work_data'])
        session_name = data.get('Session_Name', f"Session: {date_str}")
        
        # Apply currency conversion to saved revenue (which is stored in MAD)
        saved_rev_mad = data.get('Revenue', 0)
        converted_rev = saved_rev_mad * rate
        
        with st.expander(f"📊 {session_name}"):
            st.write(f"**{txt['date']}** {data.get('Date', 'N/A')}")
            st.write(f"**{txt['rev']}** {converted_rev:,.2f} {sym}")
            st.write(f"**{txt['nm']}** {data.get('Net Margin', 0)}%")
            st.write(f"**{txt['roe']}** {data.get('ROE', 0)}%")
            
            # Display Current Ratio if it exists in older saves
            if 'Current Ratio' in data:
                st.write(f"**{txt['cr']}** {data.get('Current Ratio', 0)}x")
            
            st.markdown("---")
            col_ren, col_del = st.columns([3, 1])
            
            with col_ren:
                new_name = st.text_input(txt["ren_lbl"], value=session_name, key=f"ren_input_{session_id}", label_visibility="collapsed")
                if st.button(txt["ren_btn"], key=f"btn_ren_{session_id}"):
                    if update_session_name(session_id, data, new_name):
                        st.success(txt["ren_succ"])
                        st.rerun()
                        
            with col_del:
                if st.button(txt["del_btn"], key=f"btn_del_{session_id}", type="primary", use_container_width=True):
                    if delete_session(session_id):
                        st.success(txt["del_succ"])
                        st.rerun()
