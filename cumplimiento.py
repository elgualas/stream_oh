# cumplimiento.py
import pandas as pd

def cargar_datos_entregas():
    entrega_mayo = pd.read_csv('entrega_mayo.csv')  # Cambia esto por la ruta correcta de tu archivo
    tiendas = pd.read_csv('tiendas.csv')  # Cambia esto por la ruta correcta de tu archivo
    return entrega_mayo, tiendas

def crear_resumen_entregas(entrega_mayo, tiendas, meta_dict):
    tiendas['Tienda'] = tiendas['zona'] + ' ' + tiendas['tienda']
    merged_df = entrega_mayo.merge(tiendas, left_on='tienda_id', right_on='IdTienda')
    delivery_summary_final = merged_df.groupby(['tipo', 'Tienda'])['IdEntrega'].count().reset_index()
    delivery_summary_final.columns = ['TipoTienda', 'Tienda', 'TotalEntregas']
    delivery_summary_final['Meta'] = delivery_summary_final['Tienda'].map(meta_dict)
    return delivery_summary_final

def display_cumplimiento_summary(st, meta_option):
    entrega_mayo, tiendas = cargar_datos_entregas()
    meta_dict = OH if meta_option == "OH" else OTO
    cumplimiento_summary = crear_resumen_entregas(entrega_mayo, tiendas, meta_dict)
    st.write("### Resumen de Entregas por Tienda")
    st.dataframe(cumplimiento_summary)

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
