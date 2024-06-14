import streamlit as st
import pandas as pd
from datetime import date, datetime

# Define los pesos
peso_dia_semana = 1.3
peso_fin_de_semana = 1.5

# Define los días festivos
feriados = []

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

def ajustar_metas_diarias(ventas_reales, metas_diarias, hoy):
    for tienda in metas_diarias:
        if tienda not in ventas_reales:
            continue
        
        ventas_acumuladas = sum(ventas_reales[tienda].get(dia, 0) for dia in metas_diarias[tienda] if dia < hoy)
        meta_restante = metas_diarias[tienda][hoy] + sum(metas_diarias[tienda][dia] for dia in metas_diarias[tienda] if dia > hoy)
        
        ajuste_necesario = metas_diarias[tienda][hoy] - ventas_acumuladas
        
        if ajuste_necesario > 0:
            for dia in sorted(metas_diarias[tienda]):
                if dia > hoy:
                    metas_diarias[tienda][dia] += ajuste_necesario // (len(metas_diarias[tienda]) - metas_diarias[tienda].keys().index(dia))
    
    return metas_diarias

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
    
    # Cargar archivos CSV
    entregas = pd.read_csv('/mnt/data/entrega_junio.csv')
    tiendas = pd.read_csv('/mnt/data/tiendas.csv')
    
    # Convertir entregas a diccionario
    entregas['fecha'] = pd.to_datetime(entregas['fecha'])
    ventas_reales = entregas.pivot_table(index='tienda', columns='fecha', values='entregas', aggfunc='sum').fillna(0).to_dict('index')
    
    # Obtener la fecha de hoy
    hoy = date.today()
    
    metas_diarias_OH = distribuir_metas(OH, 6, 2024, feriados)
    metas_diarias_OTO = distribuir_metas(OTO, 6, 2024, feriados)
    
    # Ajustar metas diarias
    metas_diarias_OH_ajustadas = ajustar_metas_diarias(ventas_reales, metas_diarias_OH, hoy)
    metas_diarias_OTO_ajustadas = ajustar_metas_diarias(ventas_reales, metas_diarias_OTO, hoy)
    
    df_OH = convertir_a_dataframe(metas_diarias_OH_ajustadas)
    df_OTO = convertir_a_dataframe(metas_diarias_OTO_ajustadas)
    
    st.subheader("Metas OH")
    st.table(df_OH)
    
    st.subheader("Metas OTO")
    st.table(df_OTO)

    st.subheader("Meta del Día de Hoy")
    meta_hoy = {tienda: metas_diarias_OH_ajustadas[tienda][hoy] + metas_diarias_OTO_ajustadas[tienda][hoy] for tienda in metas_diarias_OH_ajustadas}
    df_meta_hoy = pd.DataFrame.from_dict(meta_hoy, orient='index', columns=['Meta Hoy'])
    st.table(df_meta_hoy)

# Llama a la función display_metas_summary en tu aplicación principal