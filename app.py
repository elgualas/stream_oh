import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from recurrencia import cargar_datos, filtrar_datos, process_group, display_recurrence_summary
from intensidad import create_summary, display_summary
from cumplimiento import cargar_datos_entregas, crear_resumen_entregas, display_cumplimiento_summary

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="oh!.ico",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# Cargar el archivo CSV
file_path = 'recurrencia.csv'  # Cambia esto por la ruta correcta de tu archivo
df = cargar_datos(file_path)

# Filtrar los datos por los valores de la columna 'estado'
sin_camp_df, camp_df, garantia_df = filtrar_datos(df)

# Crear resúmenes de intensidad
sin_camp_summary = create_summary(sin_camp_df)
camp_summary = create_summary(camp_df)
garantia_summary = create_summary(garantia_df)
total_df = pd.concat([sin_camp_df, camp_df, garantia_df])
total_summary = create_summary(total_df)

# Crear los resúmenes de recurrencia
sin_camp_recurrence = process_group(sin_camp_df)
camp_recurrence = process_group(camp_df)
garantia_recurrence = process_group(garantia_df)
total_recurrence = process_group(total_df)

st.sidebar.markdown(
    """
    <style>
    .sidebar-title {
        font-size: 40px;  /* Ajusta el tamaño de la fuente */
        text-align: center;  /* Centra el texto */
        font-weight: bold;  /* Hace el texto en negrita */
        color: white;
    }
    .menu-box {
        background-color: #f0f0f0;  /* Color de fondo del recuadro */
        padding: 10px;  /* Espaciado interno */
        border-radius: 10px;  /* Bordes redondeados */
        text-align: center;  /* Centra el contenido */
    }
    .menu-image {
        margin-bottom: 10px;  /* Espacio debajo de la imagen */
    }
    </style>
    """, 
    unsafe_allow_html=True
)

st.sidebar.markdown('<div class="sidebar-title">Proyecto</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="menu-box">', unsafe_allow_html=True)
st.sidebar.image("oh!.png", use_column_width=True)  # Añade tu imagen
option = st.sidebar.selectbox("Selecciona una opción:", ["Intensidad", "Recurrencia", "Cumplimiento", "Otros"])
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Mostrar contenido basado en la opción seleccionada
if option == "Intensidad":
    display_summary(st, go, sin_camp_summary, camp_summary, garantia_summary, total_summary)
elif option == "Recurrencia":
    display_recurrence_summary(st, go, sin_camp_recurrence, camp_recurrence, garantia_recurrence, total_recurrence)
elif option == "Cumplimiento":
    entrega_file_path = 'entrega_mayo.csv'  # Cambia esto por la ruta correcta de tu archivo
    tiendas_file_path = 'tiendas.csv'  # Cambia esto por la ruta correcta de tu archivo
    entrega_mayo, tiendas = cargar_datos_entregas(entrega_file_path, tiendas_file_path)
    cumplimiento_summary = crear_resumen_entregas(entrega_mayo, tiendas)
    display_cumplimiento_summary(st, cumplimiento_summary)
elif option == "Otros":
    st.write("Contenido para Opción 3")
