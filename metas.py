import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime

# Define los pesos
peso_dia_semana = 0.9
peso_fin_de_semana = 1.5

# Define los días festivos
feriados = ['2024-06-14', '2024-06-27']

# Diccionario para los días de la semana
dias_semana = {0: 'lun', 1: 'mar', 2: 'mié', 3: 'jue', 4: 'vie', 5: 'sáb', 6: 'dom'}

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

def display_metas_summary():
    st.title("Resumen de Metas")
    
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
    
    st.subheader("Metas OH")
    st.table(df_OH)
    
    st.subheader("Metas OTO")
    st.table(df_OTO)

# Llama a la función display_metas_summary en tu aplicación principal
