import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title='LPS Clínica 3 Pisos', page_icon='🏗️', layout='wide')
DATA = Path(__file__).parent / 'data'

@st.cache_data
def load(name):
    return pd.read_csv(DATA / name)

look = load('lookahead.csv')
rest = load('restricciones.csv')
plan = load('plan_semanal.csv')
hist = load('historico_ppc.csv')

st.title('Dashboard Digital Last Planner')
st.caption('Proyecto Demo · Clínica de 3 pisos · Estructura de hormigón armado')

page = st.sidebar.radio('Navegación', ['Resumen Ejecutivo','Lookahead 6 semanas','Restricciones','Plan Semanal','PPC / CNC'])
semana_actual = 'S06'
actual = plan[plan['Semana']==semana_actual]
cumplidas = int((actual['Cumplimiento']=='Sí').sum())
total = len(actual)
ppc = round(cumplidas/total*100) if total else 0
abiertas = int((rest['Estado']!='Liberada').sum())
vencidas = int((rest['Estado']=='Vencida').sum())

if page == 'Resumen Ejecutivo':
    c1,c2,c3,c4 = st.columns(4)
    c1.metric('PPC semana', f'{ppc}%')
    c2.metric('Compromisos', f'{cumplidas}/{total}')
    c3.metric('Restricciones abiertas', abiertas)
    c4.metric('Restricciones vencidas', vencidas)
    st.subheader('Evolución PPC')
    chart = alt.Chart(hist).mark_line(point=True).encode(x=alt.X('Semana:N', sort=None), y=alt.Y('PPC:Q', scale=alt.Scale(domain=[0,100])), tooltip=['Semana','PPC']).properties(height=280)
    st.altair_chart(chart, use_container_width=True)
    left,right=st.columns(2)
    with left:
        st.subheader('Causas de no cumplimiento')
        cnc = plan[plan['Cumplimiento']=='No']['CNC'].value_counts().reset_index(); cnc.columns=['CNC','Casos']
        st.altair_chart(alt.Chart(cnc).mark_bar().encode(x='Casos:Q',y=alt.Y('CNC:N',sort='-x'),tooltip=['CNC','Casos']).properties(height=250),use_container_width=True)
    with right:
        st.subheader('Restricciones por estado')
        rs=rest['Estado'].value_counts().reset_index(); rs.columns=['Estado','Cantidad']
        st.altair_chart(alt.Chart(rs).mark_bar().encode(x='Estado:N',y='Cantidad:Q',tooltip=['Estado','Cantidad']).properties(height=250),use_container_width=True)
    st.subheader('Alertas de la semana')
    st.dataframe(rest[rest['Estado'].isin(['Vencida','Pendiente'])][['Actividad','Restricción','Responsable','Fecha requerida','Estado']], use_container_width=True, hide_index=True)

elif page == 'Lookahead 6 semanas':
    st.subheader('Lookahead – próximas 6 semanas')
    piso=st.multiselect('Filtrar nivel', sorted(look['Nivel'].unique()), default=sorted(look['Nivel'].unique()))
    st.dataframe(look[look['Nivel'].isin(piso)], use_container_width=True, hide_index=True)

elif page == 'Restricciones':
    st.subheader('Matriz de restricciones')
    estados=st.multiselect('Estado', sorted(rest['Estado'].unique()), default=sorted(rest['Estado'].unique()))
    st.dataframe(rest[rest['Estado'].isin(estados)], use_container_width=True, hide_index=True)

elif page == 'Plan Semanal':
    st.subheader(f'Plan de Trabajo Semanal – {semana_actual}')
    st.dataframe(actual, use_container_width=True, hide_index=True)
    st.info('El demo es de consulta. En la implementación real, el Planner actualizaría los datos desde una fuente central.')

else:
    st.subheader('PPC histórico')
    st.altair_chart(alt.Chart(hist).mark_line(point=True).encode(x=alt.X('Semana:N',sort=None),y=alt.Y('PPC:Q',scale=alt.Scale(domain=[0,100])),tooltip=['Semana','PPC']).properties(height=300),use_container_width=True)
    st.subheader('Registro de incumplimientos')
    st.dataframe(plan[plan['Cumplimiento']=='No'][['Semana','Actividad','Nivel','Responsable','CNC','Observación']],use_container_width=True,hide_index=True)

st.divider()
st.caption('Demo conceptual LPS · Solo datos de planificación y control de compromisos. No reemplaza el programa maestro ni los sistemas contractuales/documentales del proyecto.')
