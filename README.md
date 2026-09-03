# Demo LPS - Una Obra (V3)

Dashboard operacional de Last Planner System para una obra ficticia: Clínica de 3 pisos.

## Correcciones V3

- Plan de 6 semanas convertido en Lookahead visual S10–S15.
- Restricciones vinculadas exclusivamente a actividades presentes en el Lookahead.
- Tareas previas/habilitantes vinculadas mediante el mismo ID de actividad.
- Sin cambios funcionales en Resumen Ejecutivo, Plan Semanal, Arrastres/Reprogramación ni PPC/CNC.

## Ejecución local

```text
pip install -r requirements.txt
streamlit run app.py
```

Para actualizar la aplicación publicada, reemplazar `app.py`, `requirements.txt` y la carpeta `data` en el repositorio conectado a Streamlit.
