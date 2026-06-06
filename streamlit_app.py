"""
Dashboard de Incidencia Delictiva en México
=============================================
Aplicación Streamlit que integra dos bases del SESNSP:
  1. Fuero común (incidencia municipal)   — IDM_NM_dic25.csv
  2. Fuero federal (2012-2026)            — Fuero_federal_2012-2026_abr2026.csv

Despliegue gratuito en Streamlit Community Cloud (share.streamlit.io).
Embebible en cualquier sitio con:  <iframe src="https://TU-APP.streamlit.app/?embed=true" ...>
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
st.set_page_config(
    page_title="Dashboard de Incidencia Delictiva · México",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta institucional
C = {
    "blue": "#185FA5", "blue_l": "#378ADD", "purple": "#534AB7",
    "red": "#C0392B", "pink": "#993556", "pink_l": "#D4537E",
    "amber": "#BA7517", "green": "#3B6D11", "green_l": "#639922",
    "teal": "#0F6E56", "gray": "#5F5E5A", "navy": "#1B3A5B",
}
SECUENCIA = [C["blue"], C["purple"], C["red"], C["pink_l"], C["amber"],
             C["green_l"], C["teal"], C["gray"], C["blue_l"], C["pink"]]

MESES_COMUN = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio',
               'Agosto','Septiembre','Octubre','Noviembre','Diciembre']
MESES_FED = ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO',
             'AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']

# Estilo CSS ligero
st.markdown("""
<style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    h1 { color: #1B3A5B; }
    h2, h3 { color: #185FA5; }
    [data-testid="stMetricValue"] { font-size: 1.6rem; }
    .fuente { font-size: 0.78rem; color: #5F5E5A; font-style: italic; margin-top: -0.5rem; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# CARGA DE DATOS (con caché para velocidad)
# ============================================================
@st.cache_data
def cargar_comun():
    # El archivo se distribuye comprimido (.csv.gz) para respetar el límite de GitHub.
    # pandas lo descomprime automáticamente. Si usas el CSV sin comprimir, cambia el nombre.
    df = pd.read_csv("IDM_NM_dic25.csv.gz", encoding="latin1", compression="gzip")
    df["Total"] = df[MESES_COMUN].sum(axis=1)
    return df

@st.cache_data
def cargar_federal():
    df = pd.read_csv("Fuero_federal_2012-2026_abr2026.csv", encoding="latin1")
    df["Total"] = df[MESES_FED].sum(axis=1)
    return df

def cap(s):
    """Capitaliza nombres de entidades en MAYÚSCULAS y corrige acentos."""
    s = str(s).title()
    for a, b in [('Mexico','México'),('Leon','León'),('Potosi','Potosí'),
                 ('Michoacan','Michoacán'),('Queretaro','Querétaro'),('Yucatan','Yucatán')]:
        s = s.replace(a, b)
    return s

def fuente(texto):
    st.markdown(f'<p class="fuente">Fuente: {texto}</p>', unsafe_allow_html=True)

def fmt(n):
    return f"{int(n):,}".replace(",", " ")

LAYOUT = dict(
    margin=dict(l=10, r=10, t=50, b=10),
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Arial", size=13, color="#2C2C2A"),
    title_font=dict(size=16, color="#1B3A5B"),
    xaxis=dict(gridcolor="#E2E0D8"), yaxis=dict(gridcolor="#E2E0D8"),
)


# ============================================================
# SIDEBAR — SELECCIÓN DE BASE
# ============================================================
st.sidebar.title("📊 Panel de control")
base = st.sidebar.radio(
    "Selecciona la base de datos:",
    ["Fuero común (municipal)", "Fuero federal (2012–2026)"],
)
st.sidebar.markdown("---")


# ============================================================
# VISTA 1 — FUERO COMÚN
# ============================================================
def vista_comun():
    df = cargar_comun()
    SRC = "SESNSP — Incidencia Delictiva del Fuero Común a nivel municipal (IDM_NM_dic25.csv)."

    st.title("Incidencia Delictiva del Fuero Común")
    st.caption("Análisis estadístico descriptivo para política de seguridad · 2015–2019")

    # --- Filtros ---
    anios = sorted(df["Año"].unique())
    c1, c2 = st.sidebar.columns(2)
    a_min = c1.selectbox("Año inicial", anios, index=0)
    a_max = c2.selectbox("Año final", anios, index=len(anios)-1)
    if a_min > a_max:
        a_min, a_max = a_max, a_min

    entidades = ["Todas"] + sorted(df["Entidad"].unique())
    ent_sel = st.sidebar.selectbox("Entidad", entidades)

    dff = df[(df["Año"] >= a_min) & (df["Año"] <= a_max)]
    if ent_sel != "Todas":
        dff = dff[dff["Entidad"] == ent_sel]

    titulo_filtro = f"{a_min}–{a_max}" + ("" if ent_sel == "Todas" else f" · {ent_sel}")

    # --- KPIs ---
    total = int(dff["Total"].sum())
    n_anios = a_max - a_min + 1
    top_tipo = dff.groupby("Tipo de delito")["Total"].sum().idxmax()
    top_ent = dff.groupby("Entidad")["Total"].sum().idxmax()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de delitos", fmt(total))
    k2.metric("Promedio anual", fmt(total / n_anios))
    k3.metric("Delito principal", top_tipo)
    k4.metric("Entidad más afectada", top_ent if ent_sel == "Todas" else ent_sel)
    fuente(f"{SRC} Periodo seleccionado: {titulo_filtro}.")
    st.markdown("---")

    # --- Gráfica 1: tendencia anual ---
    st.subheader("Tendencia anual de delitos")
    st.markdown("Evolución del total de delitos en el periodo seleccionado.")
    serie = dff.groupby("Año")["Total"].sum().reset_index()
    fig = px.bar(serie, x="Año", y="Total", color_discrete_sequence=[C["blue"]])
    fig.update_layout(**LAYOUT, showlegend=False, height=350)
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, use_container_width=True)
    fuente(f"Suma del total anual (doce meses) por la variable Año. {SRC}")

    col1, col2 = st.columns(2)

    # --- Gráfica 2: top tipos ---
    with col1:
        st.subheader("Top 10 tipos de delito")
        st.markdown("Delitos de mayor volumen en el periodo.")
        top = dff.groupby("Tipo de delito")["Total"].sum().sort_values(ascending=False).head(10).reset_index()
        fig.update_layout(**LAYOUT, showlegend=False, height=400)
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig, use_container_width=True)
        fuente(f"Agregación por Tipo de delito. {SRC}")

    # --- Gráfica 3: bien jurídico ---
    with col2:
        st.subheader("Distribución por bien jurídico")
        st.markdown("Composición según el derecho vulnerado.")
        bj = dff.groupby("Bien jurídico afectado")["Total"].sum().sort_values(ascending=False).reset_index()
        fig = px.pie(bj, values="Total", names="Bien jurídico afectado", hole=0.45,
                     color_discrete_sequence=SECUENCIA)
        fig.update_layout(**LAYOUT, height=400,
                          legend=dict(orientation="h", yanchor="bottom", y=-0.45))
        fig.update_traces(textposition="inside", textinfo="percent")
        st.plotly_chart(fig, use_container_width=True)
        fuente(f"Agregación por Bien jurídico afectado. {SRC}")

    col3, col4 = st.columns(2)

    # --- Gráfica 4: top estados ---
    with col3:
        st.subheader("Top 10 entidades")
        st.markdown("Entidades con mayor incidencia en el periodo.")
        te = dff.groupby("Entidad")["Total"].sum().sort_values(ascending=False).head(10).reset_index()
        fig.update_layout(**LAYOUT, showlegend=False, height=400)
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig, use_container_width=True)
        fuente(f"Agregación por Entidad. {SRC}")

    # --- Gráfica 5: estacionalidad mensual ---
    with col4:
        st.subheader("Estacionalidad mensual")
        st.markdown("Distribución de delitos por mes (agregado del periodo).")
        mens = pd.DataFrame({"Mes": MESES_COMUN, "Total": [int(dff[m].sum()) for m in MESES_COMUN]})
        fig = px.bar(mens, x="Mes", y="Total", color_discrete_sequence=[C["teal"]])
        fig.update_layout(**LAYOUT, showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        fuente(f"Suma de cada columna mensual en el periodo. {SRC}")

    # --- Gráfica 6: homicidio doloso por estado ---
    st.subheader("Homicidio doloso por entidad")
    st.markdown("Distribución de la violencia letal en el periodo seleccionado.")
    hom = dff[dff["Subtipo de delito"] == "Homicidio doloso"]
    if len(hom):
        he = hom.groupby("Entidad")["Total"].sum().sort_values(ascending=False).head(15).reset_index()
        fig = px.bar(he, x="Entidad", y="Total", color_discrete_sequence=[C["red"]])
        fig.update_layout(**LAYOUT, showlegend=False, height=380)
        st.plotly_chart(fig, use_container_width=True)
        fuente(f"Filtro Subtipo de delito = 'Homicidio doloso', agregado por Entidad. {SRC}")
    else:
        st.info("No hay registros de homicidio doloso para el filtro seleccionado.")

    # --- Tabla de datos ---
    with st.expander("Ver tabla de datos agregada"):
        tabla = dff.groupby(["Año", "Tipo de delito"])["Total"].sum().reset_index()
        st.dataframe(tabla, use_container_width=True, hide_index=True)
        st.download_button("Descargar CSV", tabla.to_csv(index=False).encode("utf-8"),
                           "fuero_comun_filtrado.csv", "text/csv")


# ============================================================
# VISTA 2 — FUERO FEDERAL
# ============================================================
def vista_federal():
    df = cargar_federal()
    SRC = "SESNSP — Incidencia Delictiva del Fuero Federal (Fuero_federal_2012-2026_abr2026.csv)."

    st.title("Incidencia Delictiva del Fuero Federal")
    st.caption("Análisis para política de seguridad · 2012–2026")

    st.sidebar.info("Nota: 2026 es un año parcial (enero–abril). Se excluye de las series de tendencia.")

    # --- Filtros ---
    anios = sorted(df["AÑO"].unique())
    incluir_2026 = st.sidebar.checkbox("Incluir 2026 (parcial) en tendencias", value=False)
    anios_validos = anios if incluir_2026 else [a for a in anios if a <= 2025]

    c1, c2 = st.sidebar.columns(2)
    a_min = c1.selectbox("Año inicial", anios_validos, index=0)
    a_max = c2.selectbox("Año final", anios_validos, index=len(anios_validos)-1)
    if a_min > a_max:
        a_min, a_max = a_max, a_min

    entidades = ["Todas"] + [cap(e) for e in sorted(df["ENTIDAD"].unique())]
    ent_sel = st.sidebar.selectbox("Entidad", entidades)

    dff = df[(df["AÑO"] >= a_min) & (df["AÑO"] <= a_max)]
    if ent_sel != "Todas":
        # mapear el nombre capitalizado de vuelta al original
        orig = {cap(e): e for e in df["ENTIDAD"].unique()}
        dff = dff[dff["ENTIDAD"] == orig[ent_sel]]

    titulo_filtro = f"{a_min}–{a_max}" + ("" if ent_sel == "Todas" else f" · {ent_sel}")

    # --- KPIs ---
    total = int(dff["Total"].sum())
    n_anios = a_max - a_min + 1
    top_tipo = dff.groupby("TIPO")["Total"].sum().idxmax()
    top_concepto = dff.groupby("CONCEPTO")["Total"].sum().idxmax()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de delitos", fmt(total))
    k2.metric("Promedio anual", fmt(total / n_anios))
    k3.metric("Tipo principal", top_tipo[:24] + ("…" if len(top_tipo) > 24 else ""))
    k4.metric("Concepto principal", top_concepto[:24] + ("…" if len(top_concepto) > 24 else ""))
    fuente(f"{SRC} Periodo seleccionado: {titulo_filtro}.")
    st.markdown("---")

    # --- Gráfica 1: tendencia anual ---
    st.subheader("Tendencia anual del delito federal")
    st.markdown("Evolución del total de delitos federales en el periodo.")
    serie = dff.groupby("AÑO")["Total"].sum().reset_index()
    colores = [C["gray"] if a == 2026 else C["blue"] for a in serie["AÑO"]]
    fig = go.Figure(go.Bar(x=serie["AÑO"].astype(str), y=serie["Total"], marker_color=colores))
    fig.update_layout(**LAYOUT, showlegend=False, height=350, title="")
    st.plotly_chart(fig, use_container_width=True)
    fuente(f"Suma del total anual por la variable AÑO. {SRC}")

    col1, col2 = st.columns(2)

    # --- Gráfica 2: top tipos ---
    with col1:
        st.subheader("Top 12 tipos de delito")
        st.markdown("Delitos federales de mayor volumen.")
        top = dff.groupby("TIPO")["Total"].sum().sort_values(ascending=False).head(12).reset_index()
        top["TIPO_corto"] = top["TIPO"].str.slice(0, 38)
        fig.update_layout(**LAYOUT, showlegend=False, height=420)
        fig.update_yaxes(categoryorder="total ascending", title="")
        st.plotly_chart(fig, use_container_width=True)
        fuente(f"Agregación por TIPO. {SRC}")

    # --- Gráfica 3: por concepto ---
    with col2:
        st.subheader("Composición por concepto")
        st.markdown("Distribución según el concepto jurídico.")
        con = dff.groupby("CONCEPTO")["Total"].sum().sort_values(ascending=False).reset_index()
        fig = px.pie(con, values="Total", names="CONCEPTO", hole=0.45,
                     color_discrete_sequence=SECUENCIA)
        fig.update_layout(**LAYOUT, height=420,
                          legend=dict(orientation="h", yanchor="bottom", y=-0.55))
        fig.update_traces(textposition="inside", textinfo="percent")
        st.plotly_chart(fig, use_container_width=True)
        fuente(f"Agregación por CONCEPTO. {SRC}")

    col3, col4 = st.columns(2)

    # --- Gráfica 4: top estados ---
    with col3:
        st.subheader("Top 12 entidades")
        st.markdown("Entidades con mayor delito federal (excluye Extranjero).")
        te = dff[dff["ENTIDAD"] != "EXTRANJERO"].groupby("ENTIDAD")["Total"].sum().sort_values(ascending=False).head(12).reset_index()
        te["ENTIDAD"] = te["ENTIDAD"].apply(cap)
        fig.update_layout(**LAYOUT, showlegend=False, height=420)
        fig.update_yaxes(categoryorder="total ascending", title="")
        st.plotly_chart(fig, use_container_width=True)
        fuente(f"Agregación por ENTIDAD (excluye Extranjero). {SRC}")

    # --- Gráfica 5: contra la salud ---
    with col4:
        st.subheader("Delitos contra la salud por modalidad")
        st.markdown("Composición del narcotráfico federal.")
        cs = dff[dff["CONCEPTO"] == "CONTRA LA SALUD"]
        if len(cs):
            sub = cs.groupby("TIPO")["Total"].sum().sort_values(ascending=False).reset_index()
            fig = px.pie(sub, values="Total", names="TIPO", hole=0.45,
                         color_discrete_sequence=[C["red"], C["gray"], C["amber"],
                                                  C["purple"], C["blue_l"], C["green_l"], C["teal"]])
            fig.update_layout(**LAYOUT, height=420,
                              legend=dict(orientation="h", yanchor="bottom", y=-0.55))
            fig.update_traces(textposition="inside", textinfo="percent")
            st.plotly_chart(fig, use_container_width=True)
            fuente(f"Filtro CONCEPTO = 'Contra la salud', agregado por TIPO. {SRC}")
        else:
            st.info("Sin registros de 'Contra la salud' para el filtro.")

    # --- Gráfica 6: delito estratégico seleccionable ---
    st.subheader("Tendencia de delitos estratégicos")
    estrategicos = {
        "Armas de fuego y explosivos": "LEY FEDERAL DE ARMAS DE FUEGO Y EXPLOSIVOS (L.F.A.F.E.)",
        "Servidores públicos": "COMETIDOS POR SERVIDORES PUBLICOS",
        "Patrimoniales": "PATRIMONIALES",
        "Posesión (narcóticos)": "POSESION",
    }
    sel = st.selectbox("Selecciona el delito a graficar:", list(estrategicos.keys()))
    tipo_real = estrategicos[sel]
    serie_e = dff[dff["TIPO"] == tipo_real].groupby("AÑO")["Total"].sum().reset_index()
    fig = px.line(serie_e, x="AÑO", y="Total", markers=True,
                  color_discrete_sequence=[C["amber"]])
    fig.update_layout(**LAYOUT, showlegend=False, height=350)
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, use_container_width=True)
    fuente(f"Filtro TIPO = '{tipo_real}', agregado por AÑO. {SRC}")

    # --- Tabla ---
    with st.expander("Ver tabla de datos agregada"):
        tabla = dff.groupby(["AÑO", "CONCEPTO"])["Total"].sum().reset_index()
        st.dataframe(tabla, use_container_width=True, hide_index=True)
        st.download_button("Descargar CSV", tabla.to_csv(index=False).encode("utf-8"),
                           "fuero_federal_filtrado.csv", "text/csv")


# ============================================================
# ENRUTADOR PRINCIPAL
# ============================================================
if base.startswith("Fuero común"):
    vista_comun()
else:
    vista_federal()

# Pie de página
st.sidebar.markdown("---")
st.sidebar.caption(
    "Datos: Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP). "
    "Cifras de presuntos delitos registrados; no incluyen cifra negra ni están normalizadas por población."
)
