import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64

# Configuración de página
st.set_page_config(layout="wide", page_title="Dashboard CCII 2025", page_icon="📊")

# Función para calcular positividad (6+7)
def calc_pos(data):
    """Calcula el porcentaje de respuestas positivas (notas 6 y 7)"""
    data_clean = data.dropna()
    if len(data_clean) == 0:
        return 0.0
    positives = len(data_clean[data_clean.isin([6, 7])])
    return round((positives / len(data_clean)) * 100, 1)

# Cargar datos
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('Encuesta_CCII_2025.csv', sep=';', encoding='utf-8')
        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'Encuesta_CCII_2025.csv'")
        return None
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        return None

# Función para exportar HTML
def create_export_html(perc_gen, total_resp, cont_vals, can_vals, attr_vals):
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f9f9f9; }}
            h1 {{ color: #0066cc; text-align: center; }}
            h2 {{ color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 8px; }}
            .metric {{ background: white; padding: 20px; margin: 15px 0; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }}
            .metric-value {{ font-size: 36px; font-weight: bold; color: #0066cc; }}
            table {{ width: 100%; border-collapse: collapse; margin: 25px 0; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #0066cc; color: white; }}
            tr:hover {{ background-color: #f5f5f5; }}
        </style>
    </head>
    <body>
        <h1>📊 Reporte de Comunicación Interna 2025</h1>
        <div style="display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;">
            <div class="metric">
                <strong>Satisfacción General</strong><br>
                <div class="metric-value">{perc_gen:.1f}%</div>
            </div>
            <div class="metric">
                <strong>Total Respuestas</strong><br>
                <div class="metric-value">{total_resp:,}</div>
            </div>
        </div>

        <h2>Relevancia de Contenidos (% Notas 6-7)</h2>
        <table>
            <tr><th>Contenido</th><th>% Positividad</th></tr>
            <tr><td>Obj. Estratégicos</td><td>{cont_vals[0]:.1f}%</td></tr>
            <tr><td>Clientes</td><td>{cont_vals[1]:.1f}%</td></tr>
            <tr><td>Des. Prof.</td><td>{cont_vals[2]:.1f}%</td></tr>
            <tr><td>Bienestar</td><td>{cont_vals[3]:.1f}%</td></tr>
            <tr><td>Compromiso</td><td>{cont_vals[4]:.1f}%</td></tr>
            <tr><td>Colaboración</td><td>{cont_vals[5]:.1f}%</td></tr>
            <tr><td>Comportamiento</td><td>{cont_vals[6]:.1f}%</td></tr>
            <tr><td>Orgullo</td><td>{cont_vals[7]:.1f}%</td></tr>
        </table>

        <h2>Valoración de Canales (% Notas 6-7)</h2>
        <table>
            <tr><th>Canal</th><th>% Positividad</th></tr>
            <tr><td>Intranet</td><td>{can_vals[0]:.1f}%</td></tr>
            <tr><td>Correos</td><td>{can_vals[1]:.1f}%</td></tr>
            <tr><td>Streaming</td><td>{can_vals[2]:.1f}%</td></tr>
            <tr><td>Teams</td><td>{can_vals[3]:.1f}%</td></tr>
            <tr><td>Pantallas</td><td>{can_vals[4]:.1f}%</td></tr>
        </table>

        <h2>Atributos de Comunicación (% Notas 6-7)</h2>
        <table>
            <tr><th>Atributo</th><th>% Positividad</th></tr>
            <tr><td>Oportunidad</td><td>{attr_vals[0]:.1f}%</td></tr>
            <tr><td>Utilidad</td><td>{attr_vals[1]:.1f}%</td></tr>
            <tr><td>Claridad</td><td>{attr_vals[2]:.1f}%</td></tr>
            <tr><td>Creatividad</td><td>{attr_vals[3]:.1f}%</td></tr>
            <tr><td>Frecuencia</td><td>{attr_vals[4]:.1f}%</td></tr>
        </table>

        <p style="text-align:center; color:#666; margin-top:50px;">
            Reporte generado automáticamente — Dashboard CCII 2025
        </p>
    </body>
    </html>
    """
    return html_content

df = load_data()

if df is None:
    st.stop()

# Identificar columnas demográficas (más seguro)
total_cols = df.shape[1]
col_edad = df.columns[34] if total_cols > 34 else None
col_region = df.columns[35] if total_cols > 35 else None
col_division = df.columns[36] if total_cols > 36 else None

# Sidebar - Filtros
st.sidebar.title("🔍 Filtros")
edad_seleccionada = region_seleccionada = division_seleccionada = None

if col_edad:
    edades = sorted(df[col_edad].dropna().unique())
    edad_seleccionada = st.sidebar.multiselect("👤 Edad", edades, default=edades)

if col_region:
    regiones = sorted(df[col_region].dropna().unique())
    region_seleccionada = st.sidebar.multiselect("📍 Región", regiones, default=regiones)

if col_division:
    divisiones = sorted(df[col_division].dropna().unique())
    division_seleccionada = st.sidebar.multiselect("🏢 División", divisiones, default=divisiones)

modo_comparativo = st.sidebar.checkbox("📊 Activar comparación por edades", value=False)

# Aplicar filtros
df_filtered = df.copy()
if edad_seleccionada and col_edad:
    df_filtered = df_filtered[df_filtered[col_edad].isin(edad_seleccionada)]
if region_seleccionada and col_region:
    df_filtered = df_filtered[df_filtered[col_region].isin(region_seleccionada)]
if division_seleccionada and col_division:
    df_filtered = df_filtered[df_filtered[col_division].isin(division_seleccionada)]

# Header
st.title("📊 Dashboard de Comunicación Interna 2025")

if len(df_filtered) == 0:
    st.warning("⚠️ No hay datos con los filtros seleccionados.")
    st.stop()

# Métricas generales
perc_gen = calc_pos(df_filtered.iloc[:, 33]) if total_cols > 33 else 0
promedio = df_filtered.iloc[:, 33].mean() if total_cols > 33 else 0

col1, col2, col3 = st.columns(3)
col1.metric("SATISFACCIÓN GENERAL", f"{perc_gen:.1f}%")
col2.metric("TOTAL RESPUESTAS", f"{len(df_filtered):,}")
col3.metric("PROMEDIO GENERAL", f"{promedio:.2f}")

st.markdown("---")

# Perfil demográfico
st.subheader("👥 Perfil Demográfico")
c1, c2, c3 = st.columns(3)
if col_edad:
    with c1:
        fig_edad = px.pie(df_filtered, names=col_edad, title="Por Edad", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_edad.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_edad, use_container_width=True)
if col_region:
    with c2:
        fig_reg = px.pie(df_filtered, names=col_region, title="Por Región", hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
        fig_reg.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_reg, use_container_width=True)
if col_division:
    with c3:
        fig_div = px.pie(df_filtered, names=col_division, title="Por División", hole=0.4, color_discrete_sequence=px.colors.sequential.Oranges_r)
        fig_div.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_div, use_container_width=True)

st.markdown("---")

# Contenidos y Canales
st.subheader("📢 Evaluación de Contenidos y Canales")
cont_labels = ["Obj. Estratégicos", "Clientes", "Des. Prof.", "Bienestar", "Compromiso", "Colaboración", "Comportamiento", "Orgullo"]
can_labels = ["Intranet", "Correos", "Streaming", "Teams", "Pantallas"]

cont_vals = [calc_pos(df_filtered.iloc[:, i]) for i in range(8)] if total_cols > 12 else [0]*8
can_vals = [calc_pos(df_filtered.iloc[:, i]) for i in range(8,13)] if total_cols > 12 else [0]*5

c_cont, c_can = st.columns(2)
with c_cont:
    fig_cont = px.bar(x=cont_labels, y=cont_vals, title="Relevancia de Contenidos", color=cont_vals, color_continuous_scale='Blues')
    fig_cont.add_hline(y=perc_gen, line_dash="dash", line_color="red", annotation_text="Satisfacción General")
    st.plotly_chart(fig_cont, use_container_width=True)

with c_can:
    fig_can = px.bar(x=can_labels, y=can_vals, title="Valoración de Canales", color=can_vals, color_continuous_scale='Oranges')
    fig_can.add_hline(y=perc_gen, line_dash="dash", line_color="red", annotation_text="Satisfacción General")
    st.plotly_chart(fig_can, use_container_width=True)

st.markdown("---")

# Atributos
st.subheader("✨ Atributos de la Comunicación")
attr_labels = ["Oportunidad", "Utilidad", "Claridad", "Creatividad", "Frecuencia"]
attr_vals = [calc_pos(df_filtered.iloc[:, i]) for i in range(28,33)] if total_cols > 32 else [0]*5

c_rad, c_bar = st.columns(2)
with c_rad:
    fig_radar = go.Figure(go.Scatterpolar(r=attr_vals, theta=attr_labels, fill='toself', line_color='#0066cc'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(range=[0,100])), title="Radar de Atributos")
    st.plotly_chart(fig_radar, use_container_width=True)

with c_bar:
    fig_bar = px.bar(x=attr_labels, y=attr_vals, title="Atributos (Barras)", color=attr_vals, color_continuous_scale='Viridis')
    st.plotly_chart(fig_bar, use_container_width=True)

# Exportar
st.markdown("---")
st.subheader("📄 Exportar")
e1, e2 = st.columns(2)
with e1:
    if st.button("📥 Descargar Reporte HTML"):
        html = create_export_html(perc_gen, len(df_filtered), cont_vals, can_vals, attr_vals)
        b64 = base64.b64encode(html.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="reporte_ccii_2025.html">Descargar HTML</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("✅ Listo para descargar")

with e2:
    csv = df_filtered.to_csv(index=False, sep=';').encode('utf-8')
    st.download_button("📥 Descargar Datos (CSV)", csv, "datos_filtrados_2025.csv", "text/csv")

st.caption("Dashboard Comunicación Interna 2025")
