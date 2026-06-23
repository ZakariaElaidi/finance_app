import streamlit as st
import json
import pandas as pd
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
        "banner_h": "🗄️ Database & Archive", "banner_desc": "Review, manage, and export your previously saved financial analysis sessions.",
        "no_rec": "No records found in database. Save an analysis from the Corporate Analysis tab first.",
        "date": "Date Recorded:", "rev": "Revenue:", "nm": "Net Margin:", "roe": "ROE:", "cr": "Current Ratio:",
        "ren_lbl": "Rename Session", "ren_btn": "✏️ Update Name", "del_btn": "🗑️ Delete",
        "ren_succ": "Renamed successfully!", "del_succ": "Deleted!",
        "stats_ttl": "Total Sessions", "stats_rev": "Total Analyzed Revenue",
        "export_btn": "📥 Export All to CSV", "clear_btn": "🚨 Clear All History",
        "clear_warn": "Are you sure you want to delete all your history? This cannot be undone.",
        "clear_succ": "All history cleared."
    },
    "Français": {
        "banner_h": "🗄️ Base de données & Archives", "banner_desc": "Consultez, gérez et exportez vos sessions d'analyse financière précédemment sauvegardées.",
        "no_rec": "Aucun enregistrement trouvé. Sauvegardez d'abord une analyse depuis l'onglet Analyse d'Entreprise.",
        "date": "Date d'enregistrement :", "rev": "Revenus :", "nm": "Marge Nette :", "roe": "ROE :", "cr": "Ratio de Liquidité :",
        "ren_lbl": "Renommer la session", "ren_btn": "✏️ Mettre à jour", "del_btn": "🗑️ Supprimer",
        "ren_succ": "Renommé avec succès !", "del_succ": "Supprimé !",
        "stats_ttl": "Total des Sessions", "stats_rev": "Revenus Totaux Analysés",
        "export_btn": "📥 Tout exporter en CSV", "clear_btn": "🚨 Effacer tout l'historique",
        "clear_warn": "Êtes-vous sûr de vouloir supprimer tout votre historique ? Cette action est irréversible.",
        "clear_succ": "Historique effacé."
    },
    "Español": {
        "banner_h": "🗄️ Base de Datos y Archivo", "banner_desc": "Revisa, gestiona y exporta tus sesiones de análisis financiero guardadas previamente.",
        "no_rec": "No se encontraron registros. Guarda un análisis desde la pestaña de Análisis Corporativo primero.",
        "date": "Fecha de registro:", "rev": "Ingresos:", "nm": "Margen Neto:", "roe": "ROE:", "cr": "Ratio de Liquidez:",
        "ren_lbl": "Renombrar sesión", "ren_btn": "✏️ Actualizar nombre", "del_btn": "🗑️ Eliminar",
        "ren_succ": "¡Renombrado exitosamente!", "del_succ": "¡Eliminado!",
        "stats_ttl": "Sesiones Totales", "stats_rev": "Ingresos Totales Analizados",
        "export_btn": "📥 Exportar todo a CSV", "clear_btn": "🚨 Borrar todo el historial",
        "clear_warn": "¿Estás seguro de que deseas eliminar todo tu historial? Esto no se puede deshacer.",
        "clear_succ": "Historial borrado."
    },
    "العربية": {
        "banner_h": "🗄️ قاعدة البيانات والأرشيف", "banner_desc": "مراجعة وإدارة وتصدير جلسات التحليل المالي المحفوظة مسبقًا.",
        "no_rec": "لم يتم العثور على سجلات. احفظ تحليلاً من علامة تبويب تحليل الشركات أولاً.",
        "date": "تاريخ التسجيل:", "rev": "الإيرادات:", "nm": "هامش الربح الصافي:", "roe": "العائد على حقوق المساهمين:", "cr": "نسبة التداول:",
        "ren_lbl": "إعادة تسمية الجلسة", "ren_btn": "✏️ تحديث الاسم", "del_btn": "🗑️ حذف",
        "ren_succ": "تمت إعادة التسمية بنجاح!", "del_succ": "تم الحذف!",
        "stats_ttl": "إجمالي الجلسات", "stats_rev": "إجمالي الإيرادات المحللة",
        "export_btn": "📥 تصدير الكل إلى CSV", "clear_btn": "🚨 مسح كل السجل",
        "clear_warn": "هل أنت متأكد أنك تريد حذف كل السجل الخاص بك؟ لا يمكن التراجع عن هذا الإجراء.",
        "clear_succ": "تم مسح السجل."
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
    
    /* Archive Banner Styling */
    .full-width-banner {{ position: relative; width: 100%; height: 220px; background-image: url('https://images.unsplash.com/photo-1556761175-5973dc0f32d7?q=80&w=2070&auto=format&fit=crop'); background-size: cover; background-position: center; margin-bottom: 25px; border-radius: 10px; border-left: 5px solid #8B4513; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
    .banner-overlay {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, rgba(14,17,23,0.95) 0%, rgba(14,17,23,0.8) 50%, rgba(139,69,19,0.4) 100%); }}
    .banner-content {{ position: absolute; top: 50%; left: 30px; transform: translateY(-50%); z-index: 2; }}
    
    /* Stats Box Styling */
    .stat-box {{ background-color: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px; border-top: 3px solid #8B4513; text-align: center; }}
    
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

# --- BANNER ---
st.markdown(f"""
<div class="full-width-banner">
    <div class="banner-overlay"></div>
    <div class="banner-content" {'dir="rtl"' if lang=="العربية" else ''}>
        <h1 style="color: white; margin: 0; font-size: 2.2rem; letter-spacing: 1px;">{txt['banner_h']}</h1>
        <p style="color:#e0e0e0; font-size:1.1rem; margin-top: 8px;">{txt['banner_desc']}</p>
    </div>
</div>
""", unsafe_allow_html=True)

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

def clear_all_history(user_id):
    try:
        supabase.table("users_history").delete().eq("user_id", user_id).execute()
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
    # Calculate Stats
    total_sessions = len(hist)
    total_rev_mad = 0
    export_data = []
    
    for item in hist:
        data = json.loads(item['work_data'])
        total_rev_mad += data.get('Revenue', 0)
        
        # Prepare data for export
        flat_data = {
            "Session ID": item['id'],
            "Created At": item['created_at'][:10],
            "Session Name": data.get('Session_Name', f"Session: {item['created_at'][:10]}")
        }
        flat_data.update(data)
        export_data.append(flat_data)
        
    converted_total_rev = total_rev_mad * rate

    # Display Stats
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.markdown(f"<div class='stat-box'><h4>{txt['stats_ttl']}</h4><h2>{total_sessions}</h2></div>", unsafe_allow_html=True)
    with col_stat2:
        st.markdown(f"<div class='stat-box'><h4>{txt['stats_rev']}</h4><h2>{converted_total_rev:,.0f} {sym}</h2></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Action Buttons (Export & Clear All)
    col_exp, col_clr = st.columns(2)
    with col_exp:
        df_export = pd.DataFrame(export_data)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=txt["export_btn"],
            data=csv,
            file_name="financial_history_export.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_clr:
        if st.button(txt["clear_btn"], type="primary", use_container_width=True):
            st.session_state.show_clear_confirm = True

    if st.session_state.get("show_clear_confirm", False):
        st.warning(txt["clear_warn"])
        col_yes, col_no = st.columns(2)
        if col_yes.button("Yes, Clear All", type="primary"):
            if clear_all_history(st.session_state.user.id):
                st.success(txt["clear_succ"])
                st.session_state.show_clear_confirm = False
                st.rerun()
        if col_no.button("Cancel"):
            st.session_state.show_clear_confirm = False
            st.rerun()
            
    st.markdown("---")

    # Display History Items
    for item in hist:
        session_id = item['id']
        date_str = item['created_at'][:10]
        data = json.loads(item['work_data'])
        session_name = data.get('Session_Name', f"Session: {date_str}")
        
        saved_rev_mad = data.get('Revenue', 0)
        converted_rev = saved_rev_mad * rate
        
        with st.expander(f"📊 {session_name}"):
            st.write(f"**{txt['date']}** {data.get('Date', 'N/A')}")
            st.write(f"**{txt['rev']}** {converted_rev:,.2f} {sym}")
            st.write(f"**{txt['nm']}** {data.get('Net Margin', 0)}%")
            st.write(f"**{txt['roe']}** {data.get('ROE', 0)}%")
            
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
