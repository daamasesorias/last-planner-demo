import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title="Dashboard Digital Last Planner", page_icon="📊", layout="wide")
BASE=Path(__file__).parent/"data"

@st.cache_data
def load():
    return (
        pd.read_csv(BASE/"plan_6_semanas.csv"),
        pd.read_csv(BASE/"restricciones.csv"),
        pd.read_csv(BASE/"tareas_previas.csv"),
        pd.read_csv(BASE/"plan_semanal.csv"),
        pd.read_csv(BASE/"arrastres.csv"),
        pd.read_csv(BASE/"historico_ppc.csv")
    )
plan6,rest,prev,semanal,arr,hist=load()
SEMANA="S10"

st.title("Dashboard Digital Last Planner")
st.caption("Proyecto Demo · Clínica de 3 pisos · Ejemplo de una obra")

pagina=st.sidebar.radio("Módulo",[
"Resumen Ejecutivo","Plan 6 Semanas","Restricciones Plan 6 Semanas",
"Tareas Previas / Habilitantes","Plan Semanal Actual",
"Arrastres y Reprogramación","PPC / CNC"])

if pagina=="Resumen Ejecutivo":
    total=len(semanal); cumplidas=(semanal["Cumplida"]=="Sí").sum()
    ppc=round(cumplidas/total*100) if total else 0
    abiertas=(rest["Estado"]!="Liberada").sum()
    vencidas=(rest["Estado"]=="Vencida").sum()
    activos=len(arr[arr["Estado_Reprogramacion"]!="Cerrada"])
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("PPC semana actual",f"{ppc}%")
    c2.metric("Compromisos",total)
    c3.metric("Restricciones abiertas",abiertas)
    c4.metric("Restricciones vencidas",vencidas)
    c5.metric("Arrastres activos",activos)
    st.subheader("Evolución PPC")
    ch=alt.Chart(hist).mark_line(point=True).encode(
        x=alt.X("Semana:N",sort=None),
        y=alt.Y("PPC:Q",scale=alt.Scale(domain=[0,100])),
        tooltip=["Semana","PPC","CNC_Principal"])
    st.altair_chart(ch,use_container_width=True)
    st.subheader("Alertas")
    st.dataframe(rest[rest["Estado"].isin(["Vencida","En riesgo","Pendiente"])],
                 use_container_width=True,hide_index=True)

elif pagina=="Plan 6 Semanas":
    st.subheader("Plan de 6 semanas")
    st.info("Cada actividad mantiene el mismo ID durante todo el ciclo Last Planner.")
    semanas=["S10","S11","S12","S13","S14","S15"]
    st.caption("● Semana prevista de ejecución · Una actividad puede abarcar más de una semana.")
    st.dataframe(
        plan6,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Actividad": st.column_config.TextColumn("Actividad", width="large"),
            "Responsable": st.column_config.TextColumn("Responsable", width="medium"),
            **{semana: st.column_config.TextColumn(semana, width="small") for semana in semanas},
        },
    )

elif pagina=="Restricciones Plan 6 Semanas":
    st.subheader("Restricciones asociadas a las actividades del Plan de 6 semanas")
    st.caption("Cada restricción conserva el ID de la actividad del Lookahead a la que amenaza o impide ejecutar.")
    st.dataframe(rest,use_container_width=True,hide_index=True)

elif pagina=="Tareas Previas / Habilitantes":
    st.subheader("Tareas previas / condiciones habilitantes")
    st.caption("Acciones que deben gestionarse anticipadamente para proteger la fecha de ejecución. Cada acción se vincula mediante el ID de su actividad del Lookahead.")
    st.dataframe(prev,use_container_width=True,hide_index=True)

elif pagina=="Plan Semanal Actual":
    st.subheader(f"Plan Semanal · {SEMANA}")
    st.dataframe(semanal,use_container_width=True,hide_index=True)
    ppc=round((semanal["Cumplida"]=="Sí").sum()/len(semanal)*100)
    st.metric("PPC calculado",f"{ppc}%")

elif pagina=="Arrastres y Reprogramación":
    st.subheader("Arrastres y Reprogramación")
    st.warning("Una actividad no cumplida no pasa automáticamente a la semana siguiente. Se registra su CNC, se revisan restricciones y se define una nueva semana.")
    st.dataframe(arr,use_container_width=True,hide_index=True)
    st.metric("Arrastres acumulados",int(arr["N_Arrastres"].sum()))

elif pagina=="PPC / CNC":
    st.subheader("PPC / CNC por semana")
    ch=alt.Chart(hist).mark_line(point=True).encode(
        x=alt.X("Semana:N",sort=None),
        y=alt.Y("PPC:Q",scale=alt.Scale(domain=[0,100])),
        tooltip=["Semana","PPC","CNC_Principal"])
    st.altair_chart(ch,use_container_width=True)
    cnc=semanal[(semanal["Cumplida"]=="No") & semanal["CNC"].notna() & (semanal["CNC"]!="")]
    if len(cnc):
        cc=cnc.groupby("CNC").size().reset_index(name="Cantidad")
        st.altair_chart(alt.Chart(cc).mark_bar().encode(
            x="Cantidad:Q",y=alt.Y("CNC:N",sort="-x"),tooltip=["CNC","Cantidad"]),
            use_container_width=True)
    st.dataframe(hist,use_container_width=True,hide_index=True)

st.divider()
st.caption("Demo conceptual DaAm Asesorías · Last Planner System. No reemplaza el programa maestro.")
