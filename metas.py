import streamlit as st
from datetime import date, timedelta, datetime

# Define los pesos
peso_dia_semana = 0.8
peso_fin_de_semana = 1.5

# Define los días festivos
feriados = ['2024-06-14', '2024-06-27']

def calcular_total_pesos(mes, año, feriados):
    total_pesos = 0
    dias_mes = [date(año, mes, dia) for dia in range(1, 32) if date(año, mes, dia).month == mes]
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
    dias_mes = [date(año, mes, dia) for dia in range(1, 32) if date(año, mes, dia).month == mes]
    
    for tienda, meta in metas.items():
        meta_diaria = {}
        for dia in dias_mes:
            if dia.strftime('%Y-%m-%d') in feriados:
                continue
            if dia.weekday() >= 5:
                meta_diaria[dia] = (meta / total_pesos) * peso_fin_de_semana
            else:
                meta_diaria[dia] = (meta / total_pesos) * peso_dia_semana
        metas_diarias[tienda] = meta_diaria
    
    return metas_diarias

def display_metas_summary():
    st.title("Resumen de Metas")
    
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
    
    metas_diarias_OH = distribuir_metas(OH, 6, 2024, feriados)
    metas_diarias_OTO = distribuir_metas(OTO, 6, 2024, feriados)
    
    st.subheader("Metas OH")
    for tienda, metas in metas_diarias_OH.items():
        st.markdown(f"### {tienda}")
        for dia, meta in metas.items():
            st.write(f"{dia}: {meta:.2f}")
    
    st.subheader("Metas OTO")
    for tienda, metas in metas_diarias_OTO.items():
        st.markdown(f"### {tienda}")
        for dia, meta in metas.items():
            st.write(f"{dia}: {meta:.2f}")

# Llama a la función display_metas_summary en tu aplicación principal
