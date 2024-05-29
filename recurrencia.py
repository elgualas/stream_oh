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
def process_group(df):
    # Obtener las columnas de los meses dinámicamente
    month_columns = [col for col in df.columns if '(Mes ' in col]
    result = pd.DataFrame(columns=['Mes'] + [f'Rec. {col.split()[0]}' for col in month_columns])
    
    all_dnis = {col: set(df[df[col] > 0]['DNI Cliente']) for col in month_columns}
    total_sums = {col: df[col].sum() for col in month_columns}
    
    for i, month in enumerate(month_columns):
        row = {'Mes': month.split()[0]}
        current_dnis = all_dnis[month]
        
        for j in range(i):
            prev_month = month_columns[j]
            row[f'Rec. {prev_month.split()[0]}'] = len(current_dnis & all_dnis[prev_month])
        
        row[f'Rec. {month.split()[0]}'] = total_sums[month] - sum(row.get(f'Rec. {col.split()[0]}', 0) for col in month_columns[:i])
        
        for j in range(i + 1, len(month_columns)):
            row[f'Rec. {month_columns[j].split()[0]}'] = 0
        
        result = pd.concat([result, pd.DataFrame([row])], ignore_index=True)
    
    result['Total'] = result.iloc[:, 1:].sum(axis=1)
    return result

def display_recurrence_summary(st, go):
    st.header("Resumen de Recurrencia")
    file_path = 'recurrencia.csv'  # Cambia esto por la ruta correcta de tu archivo
    df = cargar_datos(file_path)
    sin_camp_df, camp_df, garantia_df = filtrar_datos(df)
    sin_camp_recurrence = process_group(sin_camp_df)
    camp_recurrence = process_group(camp_df)
    garantia_recurrence = process_group(garantia_df)
    total_df = pd.concat([sin_camp_df, camp_df, garantia_df])
    total_recurrence = process_group(total_df)

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
            selected_summary = sin_camp_recurrence
        elif selection == "Campaña":
            selected_summary = camp_recurrence
        elif selection == "Garantía":
            selected_summary = garantia_recurrence
        elif selection == "Total":
            selected_summary = total_recurrence
            
        months = [col for col in selected_summary.columns if col not in ['Mes', 'Total']]
        selected_months = st.multiselect("Selecciona los meses:", months, default=months)

        # Ordenar los meses seleccionados
        selected_months.sort(key=lambda month: months.index(month))

        selected_columns = ['Mes'] + selected_months
        filtered_summary = selected_summary[selected_columns]

        if value_type == "Porcentaje":
            filtered_summary[selected_months] = filtered_summary[selected_months].apply(lambda x: (x / x.sum() * 100) if x.sum() != 0 else x, axis=1)
            filtered_summary[selected_months] = filtered_summary[selected_months].applymap(lambda x: f"{x:.2f}%")
            st.table(filtered_summary[selected_columns])
        else:
            filtered_summary['Total'] = filtered_summary[selected_months].sum(axis=1)
            filtered_summary[selected_months] = filtered_summary[selected_months].applymap(lambda x: f"{int(x):,}")
            filtered_summary['Total'] = filtered_summary['Total'].apply(lambda x: f"{int(x):,}")
            st.table(filtered_summary)

        fig = go.Figure()

        for mes in selected_months:
            y_values = filtered_summary[mes].apply(lambda x: float(x.replace('%', '')) if '%' in x else x)
            fig.add_trace(go.Bar(
                x=filtered_summary['Mes'],
                y=y_values,
                name=mes
            ))

        fig.update_layout(
            title="Gráfico de Recurrencia de Clientes",
            xaxis_title="Meses",
            yaxis_title="Cantidad" if value_type == "Absoluto" else "Porcentaje",
            barmode='group'
        )

        st.plotly_chart(fig)
