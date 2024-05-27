import pandas as pd
import streamlit as st

def cargar_datos():
    tiendas_path = 'tiendas.csv'  # Cambia esto por la ruta correcta de tu archivo
    entrega_mayo_path = 'entrega_mayo.csv'  # Cambia esto por la ruta correcta de tu archivo

    tiendas_df = pd.read_csv(tiendas_path)
    entrega_mayo_df = pd.read_csv(entrega_mayo_path)
    return tiendas_df, entrega_mayo_df

def procesar_datos(tiendas_df, entrega_mayo_df):
    # Unir los DataFrames por la columna 'id tienda'
    merged_df = pd.merge(entrega_mayo_df, tiendas_df, left_on='id tienda', right_on='id tienda')

    # Crear la columna 'nombre de la tienda' concatenando 'zona' y 'tienda'
    merged_df['nombre de la tienda'] = merged_df['zona'] + ' - ' + merged_df['tienda']

    # Agrupar por 'tipo de tienda' y 'nombre de la tienda' para contar las entregas
    resumen_df = merged_df.groupby(['tipo de tienda', 'nombre de la tienda']).size().reset_index(name='entregas')

    return resumen_df

def mostrar_resumen(resumen_df):
    st.title('Resumen de Cumplimiento de Entregas')
    st.dataframe(resumen_df)

def main():
    tiendas_df, entrega_mayo_df = cargar_datos()
    resumen_df = procesar_datos(tiendas_df, entrega_mayo_df)
    mostrar_resumen(resumen_df)

if __name__ == '__main__':
    main()
