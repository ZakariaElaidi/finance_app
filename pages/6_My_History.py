import streamlit as st
import json
import pandas as pd
from supabase import create_client, ClientOptions

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
        "header_tag": "DATA ROOM & AUDIT TRAIL",
        "banner_h": "Deal Archive & History", "banner_desc": "Review, manage, and export your previously logged financial analysis and structuring sessions.",
        "no_rec": "No transaction records found. Log a session from the Valuation or Structuring modules.",
        "date": "Log Date", "rev": "Target Revenue", "nm": "EBITDA Margin", "roe": "Return on Equity", "cr": "Current Ratio",
        "ren_lbl": "Update Deal Name", "ren_btn": "✏️ Rename Log", "del_btn": "🗑️ Purge Record",
        "ren_succ": "Deal log renamed successfully.", "del_succ": "Record purged from database.",
        "stats_ttl": "Active Deal Logs", "stats_rev": "Cumulative Tracked Revenue",
        "export_btn": "📥 Export Audit Trail (CSV)", "clear_btn": "🚨 Purge Entire Data Room",
        "clear_warn": "CRITICAL: Are you sure you want to permanently delete all deal logs? This action cannot be reversed.",
        "clear_succ": "Data Room purged successfully.",
        "guest_lock": "🔒 Guest Mode Active: History tracking and Data Room functions are disabled. Please authenticate with a corporate account to utilize this module."
    },
    "Français": {
        "header_tag": "DATA ROOM & AUDIT",
        "banner_h": "Archive des Deals", "banner_desc": "Consultez, gérez et exportez vos sessions d'analyse et de structuration précédemment enregistrées.",
        "no_rec": "Aucun enregistrement trouvé. Sauvegardez une session depuis les modules de Valorisation.",
        "date": "Date d'enregistrement", "rev": "Revenus de la Cible", "nm": "Marge EBITDA", "roe": "Rentabilité des Capitaux", "cr": "Ratio de Liquidité",
        "ren_lbl": "Renommer le Deal", "ren_btn": "✏️ Mettre à jour", "del_btn": "🗑️ Purger",
        "ren_succ": "Deal renommé avec succès.", "del_succ": "Enregistrement supprimé de la base.",
        "stats_ttl": "Deals Actifs", "stats_rev": "Revenus Cumulés Suivis",
        "export_btn": "📥 Exporter l'Audit (CSV)", "clear_btn": "🚨 Purger la Data Room",
        "clear_warn": "CRITIQUE : Êtes-vous sûr de vouloir supprimer définitivement tout l'historique ? Irréversible.",
        "clear_succ": "Data Room purgée avec succès.",
        "guest_lock": "🔒 Mode Invité Actif : L'historique est désactivé. Authentifiez-vous pour utiliser ce module."
    },
    "Español": {
        "header_tag": "DATA ROOM Y AUDITORÍA",
        "banner_h": "Archivo de Acuerdos", "banner_desc": "Revise, gestione y exporte sus sesiones de análisis y estructuración.",
        "no_rec": "No se encontraron registros. Guarde una sesión desde los módulos de Valoración.",
        "date": "Fecha de Registro", "rev": "Ingresos del Objetivo", "nm": "Margen EBITDA", "roe": "ROE", "cr": "Ratio de Liquidez",
        "ren_lbl": "Renombrar Acuerdo", "ren_btn": "✏️ Actualizar", "del_btn": "🗑️ Purgar Registro",
        "ren_succ": "Registro renombrado exitosamente.", "del_succ": "Registro purgado de la base de datos.",
        "stats_ttl": "Registros Activos", "stats_rev": "Ingresos Acumulados",
        "export_btn": "📥 Exportar Auditoría (CSV)", "clear_btn": "🚨 Purgar Data Room Completo",
        "clear_warn": "CRÍTICO: ¿Está seguro de eliminar permanentemente todo su historial? Irreversible.",
        "clear_succ": "Data Room purgado exitosamente.",
        "guest_lock": "🔒 Modo Invitado: El historial está deshabilitado. Autentíquese para usar este módulo."
    },
    "العربية": {
        "header_tag": "غرفة البيانات وسجل التدقيق",
        "banner_h": "أرشيف الصفقات", "banner_desc": "مراجعة وإدارة وتصدير جلسات التحليل والهيكلة المالية المحفوظة مسبقًا.",
        "no_rec": "لم يتم العثور على سجلات صفقات. احفظ جلسة من وحدات التقييم أو الهيكلة.",
        "date": "تاريخ التسجيل", "rev": "إيرادات الهدف", "nm": "هامش الأرباح (EBITDA)", "roe": "العائد على حقوق المساهمين", "cr": "نسبة السيولة",
        "ren_lbl": "تحديث اسم الصفقة", "ren_btn": "✏️ إعادة تسمية", "del_btn": "🗑️ مسح السجل",
        "ren_succ": "تمت إعادة تسمية السجل بنجاح.", "del_succ": "تم مسح السجل من قاعدة البيانات.",
        "stats_ttl": "سجلات الصفقات النشطة", "stats_rev": "الإيرادات التراكمية المتتبعة",
        "export_btn": "📥 تصدير سجل التدقيق (CSV)", "clear_btn": "🚨 مسح غرفة البيانات بالكامل",
        "clear_warn": "حرج: هل أنت متأكد من الحذف النهائي لجميع السجلات؟ لا يمكن التراجع.",
        "clear_succ": "تم مسح غرفة البيانات بنجاح.",
        "guest_lock": "🔒 وضع الضيف نشط: السجل معطل. يرجى تسجيل الدخول بحساب معتمد لاستخدام هذه الوحدة."
    }
}
txt = t[lang]

# --- FULL WIDTH CSS INJECTION (Amber/Orange Theme) ---
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
    
    .inst-header {{ background: linear-gradient(145deg, #0e1117, #161b22); border-left: 4px solid #ff7f0e; padding: 30px 40px; border-radius: 8px; margin-bottom: 40px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
    .inst-phase {{ color: #ff7f0e; font-size: 0.9rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; display: block; }}
    .inst-title {{ color: #ffffff; font-size: 2.5rem; font-weight: 700; margin: 0; padding: 0; letter-spacing: -0.5px; }}
    .inst-desc {{ color: #8b949e; font-size: 1.1rem; margin-top: 10px; }}
    
    .kpi-container {{ display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }}
    .kpi-card {{ flex: 1; min-width: 200px; background: rgba(30, 34, 43, 0.5); border: 1px solid rgba(255,255,255,0.05); padding: 20px 25px; border-radius: 8px; border-top: 4px solid #ff7f0e; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}
    .kpi-val {{ font-size: 2.2rem; font-weight: 700; color: #ffffff; margin: 0; }}
    .kpi-lbl {{ font-size: 0.9rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin: 0; margin-top: 5px; }}
    
    .tear-sheet {{ background: rgba(0,0,0,0.2); border-radius: 6px; padding: 15px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.05); }}
    .ts-label {{ color: #8b949e; font-size: 0.85rem; text-transform: uppercase; margin: 0; }}
    .ts-val {{ color: #ffffff; font-size: 1.2rem; font-weight: 600; margin: 0 0 10px 0; }}
    
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

# --- GUEST MODE LOCK ---
if hasattr(st.session_state.user, 'email') and st.session_state.user.email == 'guest@portfolio.com':
    st.error(txt["guest_lock"])
    st.stop()

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
        
        flat_data = {
            "Session ID": item['id'],
            "Created At": item['created_at'][:10],
            "Session Name": data.get('Session_Name', f"Session: {item['created_at'][:10]}")
        }
        flat_data.update(data)
        export_data.append(flat_data)
        
    converted_total_rev = total_rev_mad * rate

    # Display KPI Stats
    st.markdown(f"""
    <div class="kpi-container" {'dir="rtl"' if lang=="العربية" else ''}>
        <div class="kpi-card"><p class="kpi-val">{total_sessions}</p><p class="kpi-lbl">{txt['stats_ttl']}</p></div>
        <div class="kpi-card" style="border-top-color: #1f77b4;"><p class="kpi-val">{converted_total_rev:,.0f} <span style="font-size: 1.2rem;">{sym}</span></p><p class="kpi-lbl">{txt['stats_rev']}</p></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action Buttons (Export & Clear All)
    col_exp, col_clr = st.columns(2)
    with col_exp:
        df_export = pd.DataFrame(export_data)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=txt["export_btn"],
            data=csv,
            file_name="Audit_Trail_Export.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_clr:
        if st.button(txt["clear_btn"], type="primary", use_container_width=True):
            st.session_state.show_clear_confirm = True

    if st.session_state.get("show_clear_confirm", False):
        st.warning(txt["clear_warn"])
        col_yes, col_no = st.columns(2)
        if col_yes.button("Yes, Purge Data Room", type="primary"):
            if clear_all_history(st.session_state.user.id):
                st.success(txt["clear_succ"])
                st.session_state.show_clear_confirm = False
                st.rerun()
        if col_no.button("Cancel"):
            st.session_state.show_clear_confirm = False
            st.rerun()
            
    st.markdown("---")

    # Display History Items (Tear-Sheet Format)
    for item in hist:
        session_id = item['id']
        date_str = item['created_at'][:10]
        data = json.loads(item['work_data'])
        session_name = data.get('Session_Name', f"Session: {date_str}")
        
        saved_rev_mad = data.get('Revenue', 0)
        converted_rev = saved_rev_mad * rate
        
        with st.expander(f"📁 {session_name}"):
            # Tear-Sheet HTML implementation
            st.markdown(f"""
            <div class="tear-sheet" {'dir="rtl"' if lang=="العربية" else ''}>
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 120px;">
                        <p class="ts-label">{txt['date']}</p>
                        <p class="ts-val" style="color: #8b949e;">{data.get('Date', 'N/A')}</p>
                    </div>
                    <div style="flex: 1; min-width: 120px;">
                        <p class="ts-label">{txt['rev']}</p>
                        <p class="ts-val" style="color: #ff7f0e;">{converted_rev:,.2f} {sym}</p>
                    </div>
                    <div style="flex: 1; min-width: 120px;">
                        <p class="ts-label">{txt['nm']}</p>
                        <p class="ts-val" style="color: #2ea043;">{data.get('Net Margin', 0)}%</p>
                    </div>
                    <div style="flex: 1; min-width: 120px;">
                        <p class="ts-label">{txt['roe']}</p>
                        <p class="ts-val" style="color: #1f77b4;">{data.get('ROE', 0)}%</p>
                    </div>
                    <div style="flex: 1; min-width: 120px;">
                        <p class="ts-label">{txt['cr']}</p>
                        <p class="ts-val">{data.get('Current Ratio', 'N/A')}{'x' if 'Current Ratio' in data else ''}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
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
