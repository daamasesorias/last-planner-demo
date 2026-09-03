
import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title="Dashboard Digital LPS", page_icon="📊", layout="wide")
BASE = Path(__file__).parent / "data"

@st.cache_data
def load():
    return (
        pd.read_csv(BASE/"plan_6_semanas.csv"),
        pd.read_csv(BASE/"restricciones.csv"),
        pd.read_csv(BASE/"tareas_previas.csv"),
        pd.read_csv(BASE/"plan_semanal.csv"),
        pd.read_csv(BASE/"arrastres.csv"),
        pd.read_csv(BASE/"historico_ppc.csv"),
    )

plan6, rest, prev, semanal, arr, hist = load()
SEMANA_ACTUAL = "S10"

st.title("Dashboard Digital Last Planner")
st.caption("Demo conceptual · 3 obras · Plan 6 semanas + preparación + compromisos + aprendizaje")

obra = st.sidebar.selectbox("Vista", ["Consolidado","Obra 1","Obra 2","Obra 3"])
pagina = st.sidebar.radio("Módulo", [
    "Resumen Ejecutivo","Plan 6 Semanas","Restricciones Plan 6 Semanas",
    "Tareas Previas / Habilitantes","Plan Semanal Actual",
    "Arrastres y Reprogramación","PPC / CNC"
])

def f(df):
    return df if obra=="Consolidado" else df[df["Obra"]==obra]

if pagina == "Resumen Ejecutivo":
    s, r, a = f(semanal), f(rest), f(arr)
    cumplidas = (s["Cumplida"]=="Sí").sum()
    total = len(s)
    ppc = round(cumplidas/total*100) if total else 0
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("PPC semana actual", f"{ppc}%")
    c2.metric("Compromisos", total)
    c3.metric("Restricciones abiertas", (~r["Estado"].isin(["Liberada"])).sum())
    c4.metric("Restricciones vencidas", (r["Estado"]=="Vencida").sum())
    c5.metric("Actividades arrastradas", len(a[a["Estado_Reprogramacion"]!="Cerrada"]))
    st.subheader("Evolución PPC")
    h=f(hist)
    chart=alt.Chart(h).mark_line(point=True).encode(
        x=alt.X("Semana:N", sort=None), y=alt.Y("PPC:Q", scale=alt.Scale(domain=[0,100])),
        color="Obra:N", tooltip=["Semana","Obra","PPC"])
    st.altair_chart(chart, use_container_width=True)
    st.subheader("Alertas de preparación")
    alert = f(rest)
    alert = alert[alert["Estado"].isin(["Vencida","En riesgo","Pendiente"])]
    st.dataframe(alert, use_container_width=True, hide_index=True)

elif pagina == "Plan 6 Semanas":
    st.subheader("Plan de 6 semanas")
    st.info("El ID de actividad se mantiene en restricciones, tareas previas, plan semanal y arrastres.")
    st.dataframe(f(plan6), use_container_width=True, hide_index=True)

elif pagina == "Restricciones Plan 6 Semanas":
    st.subheader("Restricciones asociadas al Plan de 6 semanas")
    d=f(rest)
    cat=st.multiselect("Categoría", sorted(d["Categoria"].unique()))
    if cat: d=d[d["Categoria"].isin(cat)]
    st.dataframe(d, use_container_width=True, hide_index=True)

elif pagina == "Tareas Previas / Habilitantes":
    st.subheader("Tareas previas para anticipar la ejecución")
    st.caption("Acciones que deben completarse antes de la actividad productiva: compras, ingeniería, suministros, coordinación, equipos, etc.")
    d=f(prev)
    estado=st.multiselect("Estado", sorted(d["Estado"].unique()))
    if estado: d=d[d["Estado"].isin(estado)]
    st.dataframe(d, use_container_width=True, hide_index=True)

elif pagina == "Plan Semanal Actual":
    st.subheader(f"Plan Semanal · {SEMANA_ACTUAL}")
    d=f(semanal)
    st.dataframe(d, use_container_width=True, hide_index=True)
    if len(d):
        ppc=round((d["Cumplida"]=="Sí").sum()/len(d)*100)
        st.metric("PPC calculado", f"{ppc}%")

elif pagina == "Arrastres y Reprogramación":
    st.subheader("Actividades no cumplidas y decisión de reprogramación")
    st.warning("Una actividad no cumplida NO pasa automáticamente a la semana siguiente: primero se registra la CNC y se reevalúan restricciones/habilitantes.")
    d=f(arr)
    st.dataframe(d, use_container_width=True, hide_index=True)
    if len(d):
        st.metric("Arrastres acumulados", int(d["N_Arrastres"].sum()))

elif pagina == "PPC / CNC":
    st.subheader("PPC y Causas de No Cumplimiento")
    h=f(hist)
    chart=alt.Chart(h).mark_line(point=True).encode(
        x=alt.X("Semana:N", sort=None), y=alt.Y("PPC:Q", scale=alt.Scale(domain=[0,100])),
        color="Obra:N", tooltip=["Semana","Obra","PPC","CNC_Principal"])
    st.altair_chart(chart, use_container_width=True)
    cnc=f(semanal)
    cnc=cnc[(cnc["Cumplida"]=="No") & cnc["CNC"].notna() & (cnc["CNC"]!="")]
    if len(cnc):
        counts=cnc.groupby("CNC").size().reset_index(name="Cantidad")
        st.altair_chart(alt.Chart(counts).mark_bar().encode(
            x="Cantidad:Q", y=alt.Y("CNC:N", sort="-x"), tooltip=["CNC","Cantidad"]
        ), use_container_width=True)
    st.dataframe(h, use_container_width=True, hide_index=True)

st.divider()
st.caption("Demo conceptual DaAm Asesorías · LPS: planificación de corto plazo, preparación del trabajo, compromisos y aprendizaje. No reemplaza el programa maestro ni los sistemas contractuales.")
