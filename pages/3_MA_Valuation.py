import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import io

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
        "title": "💼 M&A & Private Equity Deal Room",
        "glos_title": "ℹ️ Glossary & Advanced Definitions",
        "glos_mc": "**Monte Carlo Simulation:** A computational algorithm that relies on repeated random sampling to understand the impact of risk and uncertainty in the valuation.",
        "glos_moic": "**MoIC (Multiple on Invested Capital):** Shows how much value an investment has generated (Exit Equity / Entry Equity).",
        "sb_title": "🏢 Target Base Financials", "sb_info": "Input the target company's base financials here (in MAD).",
        "b_rev": "Base Revenue (MAD)", "b_ebitda": "Base EBITDA (MAD)",
        "capm_title": "⚙️ Advanced WACC Calculator",
        "capm_def": "**Capital Asset Pricing Model (CAPM):** The CAPM is a financial model used to calculate the expected Return on Equity. It establishes a linear relationship between the required return of an investment and its systematic risk.",
        "rf": "Risk-Free Rate (%)", "rm": "Market Return (%)", "beta": "Beta (β)", "tax": "Tax Rate (%)",
        "kd": "Cost of Debt (%)", "w_debt": "Debt Weighting (%)",
        "ke_res": "Cost of Equity (Ke)", "kd_res": "Cost of Debt post-tax (Kd)", "wacc_res": "Implied WACC",
        "capm_toggle": "Enable CAPM Calculation Mode", "wacc_slider": "WACC %",
        "dcf_title": "📊 Standard DCF Engine",
        "tg": "Terminal Growth %", "pg": "Projected Growth %", "fcfm": "FCF Margin %",
        "ev": "Implied Enterprise Value (EV)",
        "mc_btn": "🎲 Run Monte Carlo Simulation (10k Iterations)", "mc_run": "Running 10,000 simulations...",
        "mc_chart": "Enterprise Value Probability Distribution", "freq": "Frequency", "ci": "75% Confidence Interval",
        "lbo_title": "💰 LBO Quick-Modeler",
        "entry_m": "Entry Multiple (x)", "exit_m": "Exit Multiple (x)", "debt_f": "Debt Funding %",
        "pe_metrics": "Private Equity Metrics (5-Year Horizon)", "irr": "IRR", "moic": "MoIC",
        "sens_hm": "📊 EV Sensitivity (WACC vs Terminal Growth)", "dl_val_xlsx": "📥 Export Valuation Model (Excel)"
    },
    "Français": {
        "title": "💼 Salle des Marchés M&A & Private Equity",
        "glos_title": "ℹ️ Glossaire et Définitions",
        "glos_mc": "**Simulation Monte Carlo :** Algorithme informatique basé sur un échantillonnage aléatoire répété pour évaluer l'impact du risque.",
        "glos_moic": "**MoIC (Multiple sur le Capital Investi) :** Indique la valeur générée par un investissement.",
        "sb_title": "🏢 Données Financières de Base", "sb_info": "Saisissez les données financières de base de la cible (en MAD).",
        "b_rev": "Revenus de Base (MAD)", "b_ebitda": "EBITDA de Base (MAD)",
        "capm_title": "⚙️ Calculateur WACC Avancé (MEDAF)",
        "capm_def": "**Modèle d'Évaluation des Actifs Financiers (MEDAF) :** Modèle financier utilisé pour calculer la rentabilité attendue des capitaux propres.",
        "rf": "Taux Sans Risque (%)", "rm": "Rendement du Marché (%)", "beta": "Bêta (β)", "tax": "Taux d'Imposition (%)",
        "kd": "Coût de la Dette (%)", "w_debt": "Pondération de la Dette (%)",
        "ke_res": "Coût des Capitaux Propres (Ke)", "kd_res": "Coût de la Dette après impôts (Kd)", "wacc_res": "CMPC Implicite (WACC)",
        "capm_toggle": "Activer le Mode de Calcul MEDAF", "wacc_slider": "CMPC (WACC) %",
        "dcf_title": "📊 Moteur DCF Standard",
        "tg": "Croissance Terminale %", "pg": "Croissance Projetée %", "fcfm": "Marge FCF %",
        "ev": "Valeur d'Entreprise Implicite (VE)",
        "mc_btn": "🎲 Lancer Simulation Monte Carlo (10k Itérations)", "mc_run": "Exécution de 10 000 simulations...",
        "mc_chart": "Distribution de Probabilité de la Valeur d'Entreprise", "freq": "Fréquence", "ci": "Intervalle de Confiance à 75 %",
        "lbo_title": "💰 Modélisateur LBO Rapide",
        "entry_m": "Multiple d'Entrée (x)", "exit_m": "Multiple de Sortie (x)", "debt_f": "Financement par Dette %",
        "pe_metrics": "Métriques Private Equity (Horizon 5 ans)", "irr": "TRI (IRR)", "moic": "Multiple (MoIC)",
        "sens_hm": "📊 Sensibilité de la VE (WACC vs Croissance)", "dl_val_xlsx": "📥 Exporter le Modèle de Valorisation (Excel)"
    },
    "Español": {
        "title": "💼 Sala de Fusiones y Capital Privado (M&A)",
        "glos_title": "ℹ️ Glosario y Definiciones Avanzadas",
        "glos_mc": "**Simulación Monte Carlo:** Algoritmo computacional basado en muestreo aleatorio para comprender el impacto del riesgo.",
        "glos_moic": "**MoIC (Múltiplo sobre Capital Invertido):** Muestra cuánto valor ha generado una inversión.",
        "sb_title": "🏢 Finanzas Base del Objetivo", "sb_info": "Ingrese las finanzas base de la empresa objetivo aquí (en MAD).",
        "b_rev": "Ingresos Base (MAD)", "b_ebitda": "EBITDA Base (MAD)",
        "capm_title": "⚙️ Calculadora WACC Avanzada",
        "capm_def": "**Modelo de Valoración de Activos de Capital (CAPM):** Utilizado para calcular la rentabilidad esperada del capital.",
        "rf": "Tasa Libre de Riesgo (%)", "rm": "Retorno del Mercado (%)", "beta": "Beta (β)", "tax": "Tasa Impositiva (%)",
        "kd": "Costo de la Deuda (%)", "w_debt": "Ponderación de Deuda (%)",
        "ke_res": "Costo del Capital (Ke)", "kd_res": "Costo de Deuda después de impuestos (Kd)", "wacc_res": "WACC Implícito",
        "capm_toggle": "Habilitar Modo de Cálculo CAPM", "wacc_slider": "WACC %",
        "dcf_title": "📊 Motor DCF Estándar",
        "tg": "Crecimiento Terminal %", "pg": "Crecimiento Proyectado %", "fcfm": "Margen FCF %",
        "ev": "Valor Empresarial Implícito (EV)",
        "mc_btn": "🎲 Ejecutar Simulación Monte Carlo", "mc_run": "Ejecutando 10,000 simulaciones...",
        "mc_chart": "Distribución de Probabilidad del Valor Empresarial", "freq": "Frecuencia", "ci": "Intervalo de Confianza del 75%",
        "lbo_title": "💰 Modelador LBO Rápido",
        "entry_m": "Múltiplo de Entrada (x)", "exit_m": "Múltiplo de Salida (x)", "debt_f": "Financiamiento de Deuda %",
        "pe_metrics": "Métricas de Capital Privado (Horizonte 5 años)", "irr": "TIR (IRR)", "moic": "Múltiplo (MoIC)",
        "sens_hm": "📊 Sensibilidad del EV (WACC vs Crecimiento)", "dl_val_xlsx": "📥 Exportar Modelo de Valoración (Excel)"
    },
    "العربية": {
        "title": "💼 غرفة صفقات الاندماج والاستحواذ (M&A)",
        "glos_title": "ℹ️ مسرد المصطلحات والتعاريف المتقدمة",
        "glos_mc": "**محاكاة مونت كارلو:** خوارزمية حسابية تعتمد على أخذ عينات عشوائية متكررة لفهم تأثير المخاطر وعدم اليقين في التقييم.",
        "glos_moic": "**مضاعف رأس المال المستثمر (MoIC):** يوضح مقدار القيمة التي حققها الاستثمار.",
        "sb_title": "🏢 البيانات المالية الأساسية للشركة", "sb_info": "أدخل البيانات المالية الأساسية للشركة المستهدفة هنا (بالدرهم المغربي).",
        "b_rev": "الإيرادات الأساسية (MAD)", "b_ebitda": "الأرباح التشغيلية EBITDA (MAD)",
        "capm_title": "⚙️ حاسبة WACC المتقدمة (CAPM)",
        "capm_def": "**نموذج تسعير الأصول الرأسمالية (CAPM):** هو نموذج مالي يُستخدم لحساب العائد المتوقع على حقوق الملكية.",
        "rf": "المعدل الخالي من المخاطر (%)", "rm": "عائد السوق (%)", "beta": "بيتا (β)", "tax": "نسبة الضريبة (%)",
        "kd": "تكلفة الدين (%)", "w_debt": "وزن الدين (%)",
        "ke_res": "تكلفة حقوق الملكية (Ke)", "kd_res": "تكلفة الدين بعد الضريبة (Kd)", "wacc_res": "المتوسط المرجح لتكلفة رأس المال (WACC)",
        "capm_toggle": "تمكين وضع حساب CAPM", "wacc_slider": "المتوسط المرجح لتكلفة رأس المال (WACC) %",
        "dcf_title": "📊 محرك خصم التدفقات النقدية (DCF)",
        "tg": "النمو النهائي (Terminal Growth) %", "pg": "النمو المتوقع %", "fcfm": "هامش التدفق النقدي الحر (FCF) %",
        "ev": "القيمة المؤسسية الضمنية (EV)",
        "mc_btn": "🎲 تشغيل محاكاة مونت كارلو", "mc_run": "يتم الآن تشغيل 10,000 محاكاة...",
        "mc_chart": "التوزيع الاحتمالي للقيمة المؤسسية", "freq": "التردد", "ci": "فترة ثقة 75%",
        "lbo_title": "💰 نموذج الاستحواذ المدعوم بالقروض (LBO)",
        "entry_m": "مضاعف الدخول (x)", "exit_m": "مضاعف التخارج (x)", "debt_f": "نسبة تمويل الديون %",
        "pe_metrics": "مقاييس الأسهم الخاصة (أفق 5 سنوات)", "irr": "معدل العائد الداخلي (IRR)", "moic": "مضاعف رأس المال (MoIC)",
        "sens_hm": "📊 تحليل الحساسية (WACC مقابل النمو)", "dl_val_xlsx": "📥 تصدير نموذج التقييم (Excel)"
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
    .ma-card {{ background-color: #161a22; border: 1px solid #333; padding: 15px; border-radius: 8px; margin-top: 15px; margin-bottom: 20px;}}
    .ma-card-title {{ color: #b3b3b3; font-size: 0.9rem; margin-bottom: 5px; }}
    .ma-card-value {{ color: white; font-size: 1.5rem; font-weight: bold; margin: 0; }}
    {rtl_css}
</style>
""", unsafe_allow_html=True)

st.title(txt["title"])

with st.expander(txt["glos_title"]):
    st.markdown(txt["glos_mc"])
    st.markdown(txt["glos_moic"])

# --- SIDEBAR INPUTS (NATIVE MAD) ---
st.sidebar.markdown(f"### {txt['sb_title']}")
st.sidebar.info(txt["sb_info"])
base_rev = st.sidebar.number_input(txt["b_rev"], value=5000000.0, step=100000.0)
base_ebitda = st.sidebar.number_input(txt["b_ebitda"], value=1200000.0, step=50000.0)

# --- ADVANCED WACC CALCULATOR (CAPM) ---
st.subheader(txt["capm_title"])
st.info(txt["capm_def"])
use_capm = st.toggle(txt["capm_toggle"])

if use_capm:
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        rf = c1.number_input(txt["rf"], value=4.0) / 100
        rm = c2.number_input(txt["rm"], value=10.0) / 100
        beta = c3.number_input(txt["beta"], value=1.2)
        tax = c4.number_input(txt["tax"], value=30.0) / 100
        
        st.markdown("---")
        
        c5, c6 = st.columns(2)
        kd_raw = c5.number_input(txt["kd"], value=6.0) / 100
        debt_weight = c6.slider(txt["w_debt"], 0.0, 100.0, 40.0) / 100
        equity_weight = 1 - debt_weight
        
        ke = rf + beta * (rm - rf)
        kd = kd_raw * (1 - tax)
        wacc = (ke * equity_weight) + (kd * debt_weight)
        
        st.success(f"**{txt['ke_res']}:** {ke*100:.2f}% &nbsp; | &nbsp; **{txt['kd_res']}:** {kd*100:.2f}%")
        st.markdown(f"<h3 style='text-align:center; color:#2ca02c;'>🎯 {txt['wacc_res']}: {wacc*100:.2f}%</h3>", unsafe_allow_html=True)
else:
    wacc = st.slider(txt["wacc_slider"], 5.0, 20.0, 10.0, 0.5) / 100

st.markdown("---")

# --- VALUATION ENGINES ---
col_dcf, col_lbo = st.columns(2, gap="large")

with col_dcf:
    st.subheader(txt["dcf_title"])
    tg = st.slider(txt["tg"], 0.0, 5.0, 2.0, 0.1) / 100
    proj_growth = st.slider(txt["pg"], -10.0, 30.0, 5.0, 1.0) / 100
    margin = st.slider(txt["fcfm"], 1.0, 30.0, 15.0, 1.0) / 100

    # DCF Math
    cfs = [base_rev * ((1 + proj_growth)**i) * margin for i in range(1, 6)]
    terminal_value = ((cfs[-1] * (1 + tg)) / (wacc - tg)) if wacc > tg else 0
    ev = sum([cf / ((1 + wacc)**(i+1)) for i, cf in enumerate(cfs)]) + (terminal_value / ((1 + wacc)**5))
    
    ev_converted = ev * rate
    
    st.markdown(f"""
    <div class="ma-card" style="border-left: 4px solid #1f77b4;">
        <div class="ma-card-title">{txt['ev']}</div>
        <div class="ma-card-value">{ev_converted:,.2f} {sym}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 🎲 MONTE CARLO SIMULATION
    if st.button(txt["mc_btn"], use_container_width=True, type="primary"):
        with st.spinner(txt["mc_run"]):
            np.random.seed(42)
            sim_growths = np.random.normal(proj_growth, 0.02, 10000) 
            sim_margins = np.random.normal(margin, 0.02, 10000) 
            
            sim_evs = []
            for g, m in zip(sim_growths, sim_margins):
                s_cfs = [base_rev * ((1 + g)**i) * m for i in range(1, 6)]
                s_tv = ((s_cfs[-1] * (1 + tg)) / (wacc - tg)) if wacc > tg else 0
                s_ev = sum([cf / ((1 + wacc)**(i+1)) for i, cf in enumerate(s_cfs)]) + (s_tv / ((1 + wacc)**5))
                sim_evs.append(s_ev * rate)
            
            fig_mc = go.Figure(data=[go.Histogram(x=sim_evs, nbinsx=50, marker_color='#c1272d')])
            fig_mc.update_layout(title=txt["mc_chart"], template="plotly_dark", xaxis_title=f"EV ({sym})", yaxis_title=txt["freq"], height=350)
            st.plotly_chart(fig_mc, use_container_width=True)
            
            perc_25, perc_75 = np.percentile(sim_evs, 25), np.percentile(sim_evs, 75)
            st.caption(f"**{txt['ci']}:** {perc_25:,.0f} {sym} - {perc_75:,.0f} {sym}")

with col_lbo:
    st.subheader(txt["lbo_title"])
    c_l1, c_l2 = st.columns(2)
    with c_l1: entry_mult = st.number_input(txt["entry_m"], 3.0, 15.0, 6.0, 0.5)
    with c_l2: exit_mult = st.number_input(txt["exit_m"], 3.0, 15.0, 6.0, 0.5)
    debt_pct = st.slider(txt["debt_f"], 0.0, 90.0, 60.0, 5.0) / 100

    # LBO Math
    entry_ev = base_ebitda * entry_mult
    debt = entry_ev * debt_pct
    equity = entry_ev - debt
    exit_ev = (base_ebitda * ((1 + proj_growth)**5)) * exit_mult
    exit_equity = exit_ev - max(0, debt - sum(cfs)*0.5)

    moic = exit_equity / equity if equity > 0 else 0
    irr = ((moic**(1/5) - 1) * 100) if moic > 0 else 0
    
    st.markdown(f"""
    <div class="ma-card" style="border-left: 4px solid #9467bd;">
        <div class="ma-card-title">{txt['pe_metrics']}</div>
        <div class="ma-card-value" style="font-size: 1.2rem;">{txt['irr']}: {irr:.2f}% &nbsp; | &nbsp; {txt['moic']}: {moic:.2f}x</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- DCF SENSITIVITY HEATMAP ---
st.subheader(txt["sens_hm"])

# Generate matrix (+/- 2% for WACC, +/- 1% for Terminal Growth)
wacc_range_dcf = np.linspace(max(0.01, wacc - 0.02), wacc + 0.02, 7)
tg_range_dcf = np.linspace(max(0.0, tg - 0.01), tg + 0.01, 7)

z_data_dcf = []
for w in wacc_range_dcf:
    row_ev = []
    for t_g in tg_range_dcf:
        if w > t_g:
            tv_matrix = ((cfs[-1] * (1 + t_g)) / (w - t_g))
            ev_matrix = sum([cf / ((1 + w)**(i+1)) for i, cf in enumerate(cfs)]) + (tv_matrix / ((1 + w)**5))
        else:
            ev_matrix = 0
        row_ev.append(ev_matrix * rate)
    z_data_dcf.append(row_ev)

custom_colors = [[0.0, 'red'], [0.5, 'orange'], [1.0, 'green']]
fig_heat_dcf = go.Figure(data=go.Heatmap(z=z_data_dcf, x=tg_range_dcf*100, y=wacc_range_dcf*100, colorscale=custom_colors, colorbar=dict(title=sym)))
fig_heat_dcf.update_layout(xaxis_title="Terminal Growth %", yaxis_title="WACC %", template="plotly_dark", height=400)
st.plotly_chart(fig_heat_dcf, use_container_width=True)

st.markdown("---")

# --- EXPORT TO EXCEL ---
output_val = io.BytesIO()
with pd.ExcelWriter(output_val, engine='xlsxwriter') as writer:
    workbook = writer.book
    worksheet = workbook.add_worksheet('Valuation_Summary')
    
    header_format = workbook.add_format({'bold': True, 'bg_color': '#1f77b4', 'font_color': 'white', 'border': 1})
    cell_format = workbook.add_format({'border': 1})
    
    # Write Headers
    worksheet.write('A1', 'Metric', header_format)
    worksheet.write('B1', 'Value', header_format)
    worksheet.set_column('A:B', 25)
    
    # Valuation Data
    data_val = [
        ("Base Revenue", f"{base_rev * rate:,.2f} {sym}"),
        ("Base EBITDA", f"{base_ebitda * rate:,.2f} {sym}"),
        ("Implied WACC", f"{wacc*100:.2f}%"),
        ("Terminal Growth", f"{tg*100:.2f}%"),
        ("Enterprise Value (DCF)", f"{ev_converted:,.2f} {sym}"),
        ("LBO Entry Multiple", f"{entry_mult:.1f}x"),
        ("LBO Exit Multiple", f"{exit_mult:.1f}x"),
        ("Debt Funding", f"{debt_pct*100:.1f}%"),
        ("Implied IRR", f"{irr:.2f}%"),
        ("Implied MoIC", f"{moic:.2f}x")
    ]
    
    for row_num, (metric, val) in enumerate(data_val, start=1):
        worksheet.write(row_num, 0, metric, cell_format)
        worksheet.write(row_num, 1, val, cell_format)

st.download_button(
    label=txt["dl_val_xlsx"],
    data=output_val.getvalue(),
    file_name="Valuation_Model.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    type="secondary"
)
