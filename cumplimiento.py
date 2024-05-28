import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta

# Diccionarios basados en las imágenes proporcionadas
OH = {
    "vea caminos del inca": 140,
    "vea cortijo": 130,
    "vea dasso": 0,
    "vea la molina": 115,
    "vea miraflores": 190,
    "vea valle hermoso": 145,
    "oechsle primavera": 90,
    "oechsle san borja": 105,
    "vea higuereta": 155,
    "vea jockey": 105,
    "vea primavera": 50,
    "vea san borja": 175,
    "vea sucre": 105
}

OTO = {
    "vea caminos del inca": 200,
    "vea cortijo": 160,
    "vea dasso": 100,
    "vea la molina": 160,
    "vea miraflores": 250,
    "vea valle hermoso": 130,
    "oechsle primavera": 90,
    "oechsle san borja": 140,
    "vea higuereta": 170,
    "vea jockey": 130,
    "vea primavera": 50,
    "vea san borja": 165,
    "vea sucre": 115
}

# Feriados en el mes (ajustar manualmente si es necesario)
feriados = 0

def calcular_dias_del_mes():
    now = datetime.now()
    dia_actual = (now - timedelta(days=1)).day  # Restar un día para obtener el día anterior
    dias_del_mes = pd.Period(now.strftime('%Y-%m')).days_in_month
    dias_laborables = dias_del_mes - feriados
    return dia_actual, dias_laborables, dias_del_mes

def cargar_datos_entregas():
    entrega_mayo = pd.read_csv('entrega_mayo.csv')  # Cambia esto por la ruta correcta de tu archivo
    tiendas = pd.read_csv('tiendas.csv')  # Cambia esto por la ruta correcta de tu archivo
    return entrega_mayo, tiendas

def cargar_datos_estacionales():
    estacional_oh = pd.read_csv('estacional_oh.csv')  # Cambia esto por la ruta correcta de tu archivo
    estacional_oto = pd.read_csv('estacional_oto.csv')  # Cambia esto por la ruta correcta de tu archivo
    return estacional_oh, estacional_oto

def calcular_estacional(df, dia_actual):
    # Sumar las columnas hasta el día actual
    columnas = df.columns[1:dia_actual + 1]  # Excluir la columna 'tienda'
    df['Estacional'] = df[columnas].sum(axis=1)
    return df[['tienda', 'Estacional']]

def agregar_cumplimiento(df):
    dia_actual, dias_laborables, _ = calcular_dias_del_mes()
    porcentaje_esperado = (dia_actual / dias_laborables) * 100

    def calcular_cumplimiento(row):
        if row['Meta'] > 0:
            porcentaje = (row['TotalEntregas'] / row['Meta']) * 100
        else:
            porcentaje = 0
        if porcentaje >= porcentaje_esperado:
            color = "🟢"
        elif porcentaje_esperado * 0.9 <= porcentaje < porcentaje_esperado:
            color = "🟠"
        else:
            color = "🔴"
        return f'{porcentaje:.2f}% <span style="color: {color};">{color}</span>'

    df['Cumplimiento'] = df.apply(calcular_cumplimiento, axis=1)
    return df

def agregar_avance_estacional(df):
    def calcular_avance(row):
        if row['Estacional'] > 0:
            porcentaje = (row['TotalEntregas'] / row['Estacional']) * 100
        else:
            porcentaje = 0
        return f'{porcentaje:.2f}%'
    
    df['Avance Est.'] = df.apply(calcular_avance, axis=1)
    return df

def crear_resumen_entregas(entrega_mayo, tiendas, meta_dict, tipo_tienda, estacional, dia_actual):
    tiendas['Tienda'] = tiendas['zona'] + ' ' + tiendas['tienda']
    merged_df = entrega_mayo.merge(tiendas, left_on='tienda_id', right_on='IdTienda')
    if tipo_tienda != 'general':
        merged_df = merged_df[merged_df['tipo'] == tipo_tienda]
    delivery_summary_final = merged_df.groupby(['tipo', 'Tienda'])['IdEntrega'].count().reset_index()
    delivery_summary_final.columns = ['TipoTienda', 'Tienda', 'TotalEntregas']
    delivery_summary_final['Meta'] = delivery_summary_final['Tienda'].map(meta_dict)

    # Agregar columna Estacional
    estacional = calcular_estacional(estacional, dia_actual)
    delivery_summary_final = delivery_summary_final.merge(estacional, left_on='Tienda', right_on='tienda', how='left').drop('tienda', axis=1)

    delivery_summary_final = agregar_cumplimiento(delivery_summary_final)
    delivery_summary_final = agregar_avance_estacional(delivery_summary_final)

    # Reordenar columnas para que Estacional esté después de Cumplimiento
    cols = ['TipoTienda', 'Tienda', 'TotalEntregas', 'Meta', 'Cumplimiento', 'Estacional', 'Avance Est.']
    delivery_summary_final = delivery_summary_final[cols]

    # Agregar fila de total
    total_row = delivery_summary_final[['TotalEntregas', 'Meta', 'Estacional']].sum().to_frame().T
    total_row['TipoTienda'] = 'Total'
    total_row['Tienda'] = 'Total'
    total_row['Cumplimiento'] = agregar_cumplimiento(total_row).iloc[0]['Cumplimiento']
    total_row['Avance Est.'] = agregar_avance_estacional(total_row).iloc[0]['Avance Est.']
    delivery_summary_final = pd.concat([delivery_summary_final, total_row], ignore_index=True)

    return delivery_summary_final

def display_cumplimiento_summary(st):
    col1, col2 = st.columns([1, 3])

    with col1:
        meta_option = st.radio(
            "Selecciona la meta:",
            ["OH", "OTO"],
            key="meta_option_radio"
        )
        tipo_tienda = st.radio(
            "Selecciona el tipo de tienda:",
            ["general", "cluster_a", "tradicional"],
            key="tipo_tienda_radio"
        )
        # Añadir el recuadro con el resumen de días y porcentaje justo debajo de los filtros
        dia_actual, dias_laborables, dias_del_mes = calcular_dias_del_mes()
        dias_transcurridos = dia_actual  # Ya está ajustado para el día anterior
        porcentaje_transcurrido = (dias_transcurridos / dias_del_mes) * 100

        # Crear el recuadro compacto con HTML
        st.write(f"""
            <div style="border:1px solid #ddd; padding: 10px; display: inline-block;">
                <table>
                    <tr><th>Día</th><th>%</th></tr>
                    <tr><td>{dias_del_mes}</td><td>100%</td></tr>
                    <tr><td>{dias_transcurridos}</td><td>{porcentaje_transcurrido:.0f}%</td></tr>
                </table>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        entrega_mayo, tiendas = cargar_datos_entregas()
        estacional_oh, estacional_oto = cargar_datos_estacionales()
        estacional = estacional_oh if meta_option == "OH" else estacional_oto
        meta_dict = OH if meta_option == "OH" else OTO
        cumplimiento_summary = crear_resumen_entregas(entrega_mayo, tiendas, meta_dict, tipo_tienda, estacional, dia_actual)

        st.header("Resumen de Entregas por Tienda")
        
        # Convertir la columna Cumplimiento a HTML
        cumplimiento_summary['Cumplimiento'] = cumplimiento_summary['Cumplimiento'].apply(lambda x: f'<div style="text-align: right;">{x}</div>')
        
        # Mostrar la tabla
        st.write(
            cumplimiento_summary.to_html(escape=False, index=False),
            unsafe_allow_html=True
        )

    # Filtro para seleccionar una tienda específica o tipo de tienda
    st.header("Línea de Entregas")
    col3, col4 = st.columns([1, 3])
    with col3:
        tiendas['Tienda'] = tiendas['zona'] + ' ' + tiendas['tienda']  # Concatenar zona y tienda
        tipo_filtro = st.radio("Selecciona el tipo de filtro:", ["Tienda", "Tipo de Tienda"])
        if tipo_filtro == "Tienda":
            tienda_seleccionada = st.radio("Selecciona la tienda:", tiendas['Tienda'].unique())
            datos_filtrados = entrega_mayo[entrega_mayo['tienda_id'].isin(tiendas[tiendas['Tienda'] == tienda_seleccionada]['IdTienda'])]
        else:
            tipo_tienda_seleccionado = st.radio("Selecciona el tipo de tienda:", tiendas['tipo'].unique())
            datos_filtrados = entrega_mayo[entrega_mayo['tienda_id'].isin(tiendas[tiendas['tipo'] == tipo_tienda_seleccionado]['IdTienda'])]

    with col4:
        # Convertir la columna fecha_entrega a datetime
        datos_filtrados['fecha_entrega'] = pd.to_datetime(datos_filtrados['fecha_entrega'])
        
        # Crear una nueva columna para la fecha sin la hora
        datos_filtrados['fecha'] = datos_filtrados['fecha_entrega'].dt.date
        
        # Agrupar por fecha y contar las entregas
        entregas_por_dia = datos_filtrados.groupby('fecha').size().reset_index(name='entregas')
        
        # Crear la gráfica de línea de tiempo
        fig = px.line(entregas_por_dia, x='fecha', y='entregas', title='Entregas por Día')
        st.plotly_chart(fig)


