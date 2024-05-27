import pandas as pd

def create_summary(df):
    summary = df.groupby('Rango de Repeticiones').agg({
        'Ene (Mes 0)': 'sum',
        'Feb (Mes 1)': 'sum',
        'Mar (Mes 2)': 'sum',
        'Abr (Mes 3)': 'sum',
        'May (Mes 4)': 'sum',
        'Total Registros': 'sum'
    }).reset_index()

    summary.columns = ['RANGO', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'CANTIDAD']
    
    rango_order = ['1', '2 a 4', '5 a 9', '10 a 14', '15 o mas']
    summary['RANGO'] = pd.Categorical(summary['RANGO'], categories=rango_order, ordered=True)
    summary = summary.sort_values('RANGO').reset_index(drop=True)
    
    totals = summary[['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'CANTIDAD']].sum()
    totals['RANGO'] = 'Total general'
    
    summary = pd.concat([summary, pd.DataFrame(totals).transpose()], ignore_index=True)

    summary.iloc[:, 1:] = summary.iloc[:, 1:].applymap(lambda x: f"{int(x):,}" if isinstance(x, (int, float)) else x)
    
    return summary

def display_summary(st, go, sin_camp_summary, camp_summary, garantia_summary, total_summary):
    st.header("Resumen de Intensidad")
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
            
        months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo']
        selected_months = st.multiselect("Selecciona los meses:", months, default=months)

        # Ordenar los meses seleccionados
        selected_months.sort(key=lambda month: months.index(month))

        selected_columns = ['RANGO'] + selected_months
        filtered_summary = selected_summary[selected_columns]

        filtered_summary['CANTIDAD'] = filtered_summary[selected_months].applymap(lambda x: int(x.replace(',', '')) if isinstance(x, str) else x).sum(axis=1)

        if value_type == "Porcentaje":
            if selection == "Total":
                total_general_values = filtered_summary.loc[filtered_summary['RANGO'] == 'Total general', selected_months].applymap(lambda x: float(x.replace(',', ''))).values[0]
            else:
                total_general_values = filtered_summary.loc[filtered_summary['RANGO'] == 'Total general', selected_months].applymap(lambda x: float(x.replace(',', ''))).values[0]
            
            filtered_summary[selected_months] = filtered_summary[selected_months].applymap(lambda x: float(x.replace(',', ''))).div(total_general_values, axis=1).multiply(100)
            filtered_summary.drop(columns=['CANTIDAD'], inplace=True)
            filtered_summary[selected_months] = filtered_summary[selected_months].applymap(lambda x: f"{x:.2f}%")
        else:
            filtered_summary[selected_months] = filtered_summary[selected_months].applymap(lambda x: f"{int(x):,}" if isinstance(x, (int, float)) else x)
            filtered_summary['CANTIDAD'] = filtered_summary['CANTIDAD'].apply(lambda x: f"{int(x):,}")

        st.table(filtered_summary)

        fig = go.Figure()

        for rango in filtered_summary['RANGO'].unique():
            if rango != 'Total general':
                if value_type == "Porcentaje":
                    y_values = filtered_summary[filtered_summary['RANGO'] == rango].iloc[0, 1:].apply(lambda x: float(x.replace('%', '')))
                else:
                    y_values = filtered_summary[filtered_summary['RANGO'] == rango].iloc[0, 1:].apply(lambda x: int(x.replace(',', '')))
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
