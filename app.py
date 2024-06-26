import streamlit as st
import plotly.graph_objects as go
from recurrencia import display_recurrence_summary
from intensidad import display_summary
from cumplimiento import display_cumplimiento_summary
from metas import display_metas_summary

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="oh!.ico",
    layout="wide",
    initial_sidebar_state="expanded",
    
)

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
option = st.sidebar.selectbox("Selecciona una opción:", ["Cumplimiento", "Metas", "Intensidad", "Recurrencia",  "Otros"])
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Mostrar contenido basado en la opción seleccionada
if option == "Cumplimiento":
    display_cumplimiento_summary(st)
elif option == "Metas":
    display_metas_summary()  # Llama a la nueva función
elif option == "Intensidad":
    display_summary(st, go)
elif option == "Recurrencia":
    display_recurrence_summary(st, go)
elif option == "Otros":
    st.write("Contenido para Opción 3")
