# cumplimiento.py
import pandas as pd

def cargar_datos_entregas(file_entregas, file_tiendas):
    entrega_mayo = pd.read_csv(file_entregas)
    tiendas = pd.read_csv(file_tiendas)
    return entrega_mayo, tiendas

def crear_resumen_entregas(entrega_mayo, tiendas):
    tiendas['Tienda'] = tiendas['zona'] + ' ' + tiendas['tienda']
    merged_df = entrega_mayo.merge(tiendas, left_on='tienda_id', right_on='IdTienda')
    delivery_summary_final = merged_df.groupby(['tipo', 'Tienda'])['IdEntrega'].count().reset_index()
    delivery_summary_final.columns = ['TipoTienda', 'Tienda', 'TotalEntregas']
    return delivery_summary_final

def display_cumplimiento_summary(st, summary_df):
    st.write("### Resumen de Entregas por Tienda")
    st.dataframe(summary_df)
