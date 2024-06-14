import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import os

# Define los pesos
peso_dia_semana = 1.3
peso_fin_de_semana = 1.5

# Define los días festivos
feriados = []

# Diccionario para los días de la semana
dias_semana = {0: 'lun', 1: 'mar', 2: 'mié', 3: 'jue', 4: 'vie', 5: 'sáb', 6: 'dom'}

# Funciones auxiliares
def calcular_total_pesos(mes, año, feriados):
    total_pesos = 0
    dias_mes = []
    for dia in range(1, 32):
        try:
            current_date = date(año, mes, dia)
            if current_date.month == mes:
                dias_mes.append(current_date)
        except ValueError:
            break

    for dia in dias_mes:
        if dia.strftime('%Y-%m-%d') in feriados:
            continue
        if dia.weekday() >= 5:  # 5 y 6 son sábado y domingo
            total_pesos += peso_fin_de_semana
        else:
            total_pesos += peso_dia_semana
    return total_pesos

def distribuir_metas(metas, mes, año, feriados):
    total_pesos = calcular_total_pesos(mes, año, feriados)
    metas_diarias = {}
    dias_mes = []
    for dia in range(1, 32):
        try:
            current_date = date(año, mes, dia)
            if current_date.month == mes:
                dias_mes.append(current_date)
        except ValueError:
            break
    
    for tienda, meta in metas.items():
        meta_diaria = {}
        total_meta_diaria = 0
        
        # Calcula las metas diarias redondeadas hacia abajo
        for dia in dias_mes:
            if dia.strftime('%Y-%m-%d') in feriados:
                continue
            if dia.weekday() >= 5:
                meta_diaria[dia] = int((meta / total_pesos) * peso_fin_de_semana)
            else:
                meta_diaria[dia] = int((meta / total_pesos) * peso_dia_semana)
            total_meta_diaria += meta_diaria[dia]
        
        # Calcula el déficit
        deficit = meta - total_meta_diaria
        
        # Reparte el déficit entre viernes, sábados y domingos
        while deficit > 0:
            for dia in dias_mes:
                if deficit == 0:
                    break
                if dia.strftime('%Y-%m-%d') in feriados:
                    continue
                if dia.weekday() in [4, 5, 6]:  # 4 es viernes, 5 es sábado, 6 es domingo
                    meta_diaria[dia] += 1
                    deficit -= 1
                    if deficit == 0:
                        break
        
        metas_diarias[tienda] = meta_diaria
    
    return metas_diarias

def convertir_a_dataframe(metas_diarias):
    df = pd.DataFrame(metas_diarias).T
    df.columns = [f"{fecha.day}-{dias_semana[fecha.weekday()]}" for fecha in df.columns]
    df.index.name = 'Tienda'
    df['Total'] = df.sum(axis=1)
    return df

def ajustar_metas(df_metas, df_entregas, df_tiendas):
    hoy = datetime.now().date()
    hoy_str = hoy.strftime('%Y-%m-%d')
    
    # Aseguramos que la fecha de hoy esté en el formato esperado
    if hoy_str not in df_metas.columns:
        st.error(f"No hay datos de metas para la fecha de hoy: {hoy_str}")
        return df_metas
    
    # Ajustamos las metas para cada tienda en función de las entregas actuales
    for tienda in df_tiendas['Tienda']:
        if tienda in df_metas.index:
            entregas_tienda = df_entregas[df_entregas['Tienda'] == tienda]['Entregas'].sum()
            meta_total = df_metas.at[tienda, 'Total']
            entregas_acumuladas = df_entregas[df_entregas['Tienda'] == tienda].sum(axis=1).values[0]
            meta_hoy = (meta_total - entregas_acumuladas) / (30 - hoy.day + 1)
            df_metas.at[tienda, hoy_str] = max(0, int(meta_hoy))
    
    return df_metas

def display_metas_summary():
    st.title("Resumen de Metas")
    
    # Leer archivos CSV
    entregas_path = 'entrega_junio.csv'
    tiendas_path = 'tiendas.csv'
    
    if not os.path.exists(entregas_path) or not os.path.exists(tiendas_path):
        st.error("No se encontraron los archivos CSV requeridos.")
        return
    
    df_entregas = pd.read_csv(entregas_path)
    df_tiendas = pd.read_csv(tiendas_path)
    
    OH = {
        "vea caminos del inca": 150,
        "vea cortijo": 140,
        "vea la molina": 125,
        "vea miraflores": 200,
        "vea valle hermoso": 155,
        "oechsle primavera": 110,
        "oechsle san borja": 125,
        "vea higuereta": 175,
        "vea jockey": 125,
        "vea primavera": 70,
        "vea san borja": 195
    }

    OTO = {
        "vea caminos del inca": 194,
        "vea cortijo": 166,
        "vea la molina": 168,
        "vea miraflores": 230,
        "vea valle hermoso": 151,
        "oechsle primavera": 94,
        "oechsle san borja": 190,
        "vea higuereta": 180,
        "vea jockey": 165,
        "vea primavera": 85,
        "vea san borja": 160
    }
    
    metas_diarias_OH = distribuir_metas(OH, 6, 2024, feriados)
    metas_diarias_OTO = distribuir_metas(OTO, 6, 2024, feriados)
    
    df_OH = convertir_a_dataframe(metas_diarias_OH)
    df_OTO = convertir_a_dataframe(metas_diarias_OTO)
    
    # Ajustar las metas diarias en función de las entregas actuales
    df_OH_ajustado = ajustar_metas(df_OH, df_entregas, df_tiendas)
    df_OTO_ajustado = ajustar_metas(df_OTO, df_entregas, df_tiendas)
    
    st.subheader("Metas OH Ajustadas")
    st.table(df_OH_ajustado)
    
    st.subheader("Metas OTO Ajustadas")
    st.table(df_OTO_ajustado)

# Llama a la función display_metas_summary en tu aplicación principal
