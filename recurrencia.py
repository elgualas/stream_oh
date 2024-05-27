import pandas as pd

def cargar_datos(file_path):
    df = pd.read_csv(file_path)
    return df

def filtrar_datos(df):
    sin_camp_df = df[df['estado'] == 'sin camp.']
    camp_df = df[df['estado'] == 'camp.']
    garantia_df = df[df['estado'] == 'garantia']
    return sin_camp_df, camp_df, garantia_df

def process_group(df):
    result = pd.DataFrame(columns=['Mes', 'Rec. Enero', 'Rec. Febrero', 'Rec. Marzo', 'Rec. Abril', 'Rec. Mayo'])

    suma_enero = df['Ene (Mes 0)'].sum()
    suma_febrero = df['Feb (Mes 1)'].sum()
    suma_marzo = df['Mar (Mes 2)'].sum()
    suma_abril = df['Abr (Mes 3)'].sum()
    suma_mayo = df['May (Mes 4)'].sum()

    dnis_enero = set(df[df['Ene (Mes 0)'] > 0]['DNI Cliente'])
    dnis_febrero = set(df[df['Feb (Mes 1)'] > 0]['DNI Cliente'])
    dnis_marzo = set(df[df['Mar (Mes 2)'] > 0]['DNI Cliente'])
    dnis_abril = set(df[df['Abr (Mes 3)'] > 0]['DNI Cliente'])
    dnis_mayo = set(df[df['May (Mes 4)'] > 0]['DNI Cliente'])

    suma_enero_febrero = len(dnis_enero & dnis_febrero)
    suma_febrero_nuevos = suma_febrero - suma_enero_febrero

    suma_enero_marzo = len(dnis_enero & dnis_marzo)
    suma_febrero_marzo = len(dnis_febrero & dnis_marzo)
    suma_marzo_nuevos = suma_marzo - (suma_enero_marzo + suma_febrero_marzo)

    suma_enero_abril = len(dnis_enero & dnis_abril)
    suma_febrero_abril = len(dnis_febrero & dnis_abril)
    suma_marzo_abril = len(dnis_marzo & dnis_abril)
    suma_abril_nuevos = suma_abril - (suma_enero_abril + suma_febrero_abril + suma_marzo_abril)

    suma_enero_mayo = len(dnis_enero & dnis_mayo)
    suma_febrero_mayo = len(dnis_febrero & dnis_mayo)
    suma_marzo_mayo = len(dnis_marzo & dnis_mayo)
    suma_abril_mayo = len(dnis_abril & dnis_mayo)
    suma_mayo_nuevos = suma_mayo - (suma_enero_mayo + suma_febrero_mayo + suma_marzo_mayo + suma_abril_mayo)

    result = pd.concat([result, pd.DataFrame([{
        'Mes': 'Enero',
        'Rec. Enero': suma_enero,
        'Rec. Febrero': 0,
        'Rec. Marzo': 0,
        'Rec. Abril': 0,
        'Rec. Mayo': 0
    }])], ignore_index=True)

    result = pd.concat([result, pd.DataFrame([{
        'Mes': 'Febrero',
        'Rec. Enero': suma_enero_febrero,
        'Rec. Febrero': suma_febrero_nuevos,
        'Rec. Marzo': 0,
        'Rec. Abril': 0,
        'Rec. Mayo': 0
    }])], ignore_index=True)

    result = pd.concat([result, pd.DataFrame([{
        'Mes': 'Marzo',
        'Rec. Enero': suma_enero_marzo,
        'Rec. Febrero': suma_febrero_marzo,
        'Rec. Marzo': suma_marzo_nuevos,
        'Rec. Abril': 0,
        'Rec. Mayo': 0
    }])], ignore_index=True)

    result = pd.concat([result, pd.DataFrame([{
        'Mes': 'Abril',
        'Rec. Enero': suma_enero_abril,
        'Rec. Febrero': suma_febrero_abril,
        'Rec. Marzo': suma_marzo_abril,
        'Rec. Abril': suma_abril_nuevos,
        'Rec. Mayo': 0
    }])], ignore_index=True)

    result = pd.concat([result, pd.DataFrame([{
        'Mes': 'Mayo',
        'Rec. Enero': suma_enero_mayo,
        'Rec. Febrero': suma_febrero_mayo,
        'Rec. Marzo': suma_marzo_mayo,
        'Rec. Abril': suma_abril_mayo,
        'Rec. Mayo': suma_mayo_nuevos
    }])], ignore_index=True)

    result['Total'] = result[['Rec. Enero', 'Rec. Febrero', 'Rec. Marzo', 'Rec. Abril', 'Rec. Mayo']].sum(axis=1)
    return result

def display_recurrence_summary(st, go, sin_camp_recurrence, camp_recurrence, garantia_recurrence, total_recurrence):
    st.header("Resumen de Recurrencia")
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
            
        months = ['Rec. Enero', 'Rec. Febrero', 'Rec. Marzo', 'Rec. Abril', 'Rec. Mayo']
        selected_months = st.multiselect("Selecciona los meses:", months, default=months)

        # Ordenar los meses seleccionados
        selected_months.sort(key=lambda month: months.index(month))

        selected_columns = ['Mes'] + selected_months
        filtered_summary = selected_summary[selected_columns]

        if value_type == "Porcentaje":
            filtered_summary[selected_months] = filtered_summary[selected_months].apply(lambda x: x / x.sum() * 100 if x.sum() != 0 else [0] * len(x), axis=1)
            filtered_summary[selected_months] = filtered_summary[selected_months].applymap(lambda x: f"{x:.2f}%")
        else:
            filtered_summary['Total'] = filtered_summary[selected_months].sum(axis=1)
            filtered_summary[selected_months] = filtered_summary[selected_months].applymap(lambda x: f"{int(x):,}")
            filtered_summary['Total'] = filtered_summary['Total'].apply(lambda x: f"{int(x):,}")

        if value_type == "Porcentaje":
            st.table(filtered_summary[selected_columns])
        else:
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
