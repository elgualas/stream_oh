import pandas as pd
import streamlit as st
import plotly.graph_objects as go

@st.cache_data
def cargar_datos(file_path):
    return pd.read_csv(file_path)

@st.cache_data
def filtrar_datos(df):
    sin_camp_df = df[df['estado'] == 'sin camp.']
    camp_df = df[df['estado'] == 'camp.']
    garantia_df = df[df['estado'] == 'garantia']
    return sin_camp_df, camp_df, garantia_df

@st.cache_data
def create_summary(df):
    # Verificar la existencia de la columna 'Rango de Repeticiones'
    if 'Rango de Repeticiones' not in df.columns:
        raise KeyError("La columna 'Rango de Repeticiones' no existe en el DataFrame")

    # Obtener todas las columnas de mes dinámicamente
    month_columns = [col for col in df.columns if col.startswith(('Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'))]
    summary = df.groupby('Rango de Repeticiones')[month_columns + ['Total Registros']].sum().reset_index()

    month_columns_renamed = {col: col.split(' ')[0] for col in month_columns}
    summary.rename(columns=month_columns_renamed, inplace=True)
    summary.rename(columns={'Total Registros': 'CANTIDAD'}, inplace=True)
    
    rango_order = ['1', '2 a 4', '5 a 9', '10 a 14', '15 o mas']
    summary['Rango de Repeticiones'] = pd.Categorical(summary['Rango de Repeticiones'], categories=rango_order, ordered=True)
    summary = summary.sort_values('Rango de Repeticiones').reset_index(drop=True)
    
    totals = summary.drop(columns='Rango de Repeticiones').sum()
    totals['Rango de Repeticiones'] = 'Total general'
    
    summary = pd.concat([summary, pd.DataFrame(totals).transpose()], ignore_index=True)

    summary.iloc[:, 1:] = summary.iloc[:, 1:].applymap(lambda x: f"{int(x):,}" if isinstance(x, (int, float)) else x)
    
    return summary

def display_summary(st, go):
    st.header("Resumen de Intensidad")
    file_path = 'recurrencia.csv'  # Cambia esto por la ruta correcta de tu archivo
    df = cargar_datos(file_path)
    sin_camp_df, camp_df, garantia_df = filtrar_datos(df)
    sin_camp_summary = create_summary(sin_camp_df)
    camp_summary = create_summary(camp_df)
    garantia_summary = create_summary(garantia_df)
    total_df = pd.concat([sin_camp_df, camp_df, garantia_df])
    total_summary = create_summary(total_df)

    col1, col2 = st.columns([1, 2])
    with col1:
        selection = st.radio(
            "Selecciona una opción:",
            ["Sin Campaña", "Campaña", "Garantía", "Total"]
        )
        value_type = st.radio(
            "Selecciona el tipo de valor:",
            ["Absoluto", "Porcentaje"]
        )
    with col2:
        if selection == "Sin Campaña":
            selected_summary = sin_camp_summary
        elif selection == "Campaña":
            selected_summary = camp_summary
        elif selection == "Garantía":
            selected_summary = garantia_summary
        elif selection == "Total":
            selected_summary = total_summary
            
        months = [col for col in selected_summary.columns if col not in ['Rango de Repeticiones', 'CANTIDAD']]
        selected_months = st.multiselect("Selecciona los meses:", months, default=months)

        # Ordenar los meses seleccionados
        selected_months.sort(key=lambda month: months.index(month))

        selected_columns = ['Rango de Repeticiones'] + selected_months
        filtered_summary = selected_summary[selected_columns]

        filtered_summary['CANTIDAD'] = filtered_summary[selected_months].applymap(lambda x: int(x.replace(',', '')) if isinstance(x, str) else x).sum(axis=1)

        if value_type == "Porcentaje":
            if selection == "Total":
                total_general_values = filtered_summary.loc[filtered_summary['Rango de Repeticiones'] == 'Total general', selected_months].applymap(lambda x: float(x.replace(',', ''))).values[0]
            else:
                total_general_values = filtered_summary.loc[filtered_summary['Rango de Repeticiones'] == 'Total general', selected_months].applymap(lambda x: float(x.replace(',', ''))).values[0]
            
            filtered_summary[selected_months] = filtered_summary[selected_months].applymap(lambda x: float(x.replace(',', ''))).div(total_general_values, axis=1).multiply(100)
            filtered_summary.drop(columns=['CANTIDAD'], inplace=True)
            filtered_summary[selected_months] = filtered_summary[selected_months].applymap(lambda x: f"{x:.2f}%")
        else:
            filtered_summary[selected_months] = filtered_summary[selected_months].applymap(lambda x: f"{int(x):,}" if isinstance(x, (int, float)) else x)
            filtered_summary['CANTIDAD'] = filtered_summary['CANTIDAD'].apply(lambda x: f"{int(x):,}")

        st.table(filtered_summary)

        fig = go.Figure()

        for rango in filtered_summary['Rango de Repeticiones'].unique():
            if rango != 'Total general':
                if value_type == "Porcentaje":
                    y_values = filtered_summary[filtered_summary['Rango de Repeticiones'] == rango].iloc[0, 1:].apply(lambda x: float(x.replace('%', '')))
                else:
                    y_values = filtered_summary[filtered_summary['Rango de Repeticiones'] == rango].iloc[0, 1:].apply(lambda x: int(x.replace(',', '')))
                fig.add_trace(go.Bar(
                    x=selected_months,
                    y=y_values,
                    name=rango
                ))

        fig.update_layout(
            title="Gráfico de Intensidad de Clientes",
            xaxis_title="Meses",
            yaxis_title="Cantidad" if value_type == "Absoluto" else "Porcentaje",
            barmode='group'
        )

        st.plotly_chart(fig)
