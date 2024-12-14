import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np

# Set page configuration
st.set_page_config(page_title="Financial Inclusion MX", page_icon="💸", layout="centered")

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'State-Level_Consolidated_Dataset.csv')
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    percentage_columns = [col for col in df.columns if col.startswith('%')]
    for col in percentage_columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '.').astype(float)
        else:
            df[col] = df[col].astype(float)
    df.set_index('Estado', inplace=True)
    return df

df = load_data()

st.title('Comprehensive Financial Inclusion Analysis in Mexico')

# 1. Population Demographics
st.header('1. Population Demographics')
df['Adult_Population_Percentage'] = df['Poblacion_adulta'] / df['Poblacion'] * 100
df['Superficie_km2'] = df['Superficie_km2'].fillna(df['Superficie_km2'].median())

fig = px.scatter(df, x='Poblacion', y='Adult_Population_Percentage', 
                 size='Superficie_km2', hover_name=df.index, 
                 labels={'Poblacion': 'Total Population', 
                         'Adult_Population_Percentage': 'Adult Population (%)', 
                         'Superficie_km2': 'Area (km²)'},
                 title='Population Demographics by State')
st.plotly_chart(fig)

# 2. Banking Infrastructure Availability
st.header('2. Banking Infrastructure Availability')
infrastructure_metrics = {
    'Sucursales_banca_comercial_10mil_adultos': '#1f77b4',
    'Cajeros_10mil_adultos': '#2ca02c',
    'Corresponsales_10mil_adultos': '#d62728'
}
selected_metric = st.selectbox('Select infrastructure metric', list(infrastructure_metrics.keys()), key='infrastructure')

fig = px.bar(df.sort_values(selected_metric, ascending=False), y=selected_metric, 
             title=f'{selected_metric} per 10,000 Adults',
             color_discrete_sequence=[infrastructure_metrics[selected_metric]])
fig.update_layout(xaxis_title='State', yaxis_title='Number per 10,000 Adults', height=600)
st.plotly_chart(fig)

# 3. Account Ownership by Type
st.header('3. Account Ownership by Type')
account_columns = [
    'Cuentas_Nivel1_10mil_adultos_Banca', 
    'Cuentas_Nivel2_10mil_adultos_Banca', 
    'Cuentas_Nivel3_10mil_adultos_Banca', 
    'Cuentas_cuentas_transaccionales_tradicionales_10mil_adultos_Banca'
]

account_labels = {
    'Cuentas_Nivel1_10mil_adultos_Banca': 'Cuentas Nivel 1',
    'Cuentas_Nivel2_10mil_adultos_Banca': 'Cuentas Nivel 2',
    'Cuentas_Nivel3_10mil_adultos_Banca': 'Cuentas Nivel 3',
    'Cuentas_cuentas_transaccionales_tradicionales_10mil_adultos_Banca': 'Transaccionales Tradicionales'
}

view_type = st.radio('Select view type', ['Absolute Numbers', 'Percentage'])

if view_type == 'Absolute Numbers':
    account_data_abs = df[account_columns]
    account_data_renamed = account_data_abs.rename(columns=account_labels)
    fig = px.bar(
        account_data_renamed.sort_values(list(account_labels.values())[0], ascending=False),
        y=list(account_labels.values()),
        title='Account Ownership by Type per 10,000 Adults'
    )
    fig.update_layout(
        xaxis_title='State', 
        yaxis_title='Accounts per 10,000 Adults', 
        barmode='stack', 
        height=700
    )
else:
    account_data_percentage = df[account_columns].div(df[account_columns].sum(axis=1), axis=0) * 100
    account_data_renamed = account_data_percentage.rename(columns=account_labels)
    fig = px.bar(
        account_data_renamed.sort_values(list(account_labels.values())[0], ascending=False),
        y=list(account_labels.values()),
        title='Account Ownership by Type (Percentage)'
    )
    fig.update_layout(
        xaxis_title='State', 
        yaxis_title='Percentage', 
        barmode='stack', 
        height=700
    )

fig.update_layout(
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
        font=dict(size=10)
    ),
    margin=dict(l=50, r=300, t=80, b=200),
    xaxis_tickangle=-45,
    height=700
)
st.plotly_chart(fig, use_container_width=True)

# 4. Credit Product Penetration
st.header('4. Credit Product Penetration')
credit_columns = [
    'Creditos_hipotecarios_10mil_adultos_Banca', 
    'Creditos_personales_10mil_adultos_Banca', 
    'Creditos_nomina_10mil_adultos_Banca', 
    'Creditos_automotrices_10mil_adultos_Banca', 
    'Creditos_ABCD_10mil_adultos_Banca'
]

credit_labels = {
    'Creditos_hipotecarios_10mil_adultos_Banca': 'Créditos Hipotecarios',
    'Creditos_personales_10mil_adultos_Banca': 'Créditos Personales',
    'Creditos_nomina_10mil_adultos_Banca': 'Créditos Nómina',
    'Creditos_automotrices_10mil_adultos_Banca': 'Créditos Automotrices',
    'Creditos_ABCD_10mil_adultos_Banca': 'Créditos ABCD'
}

credit_data_renamed = df[credit_columns].rename(columns=credit_labels)
fig = px.bar(
    credit_data_renamed.sort_values('Créditos Hipotecarios', ascending=False), 
    y=list(credit_labels.values()),
    title='Credit Product Penetration per 10,000 Adults'
)
fig.update_layout(
    xaxis_title='State', 
    yaxis_title='Credits per 10,000 Adults', 
    barmode='stack', 
    height=700,
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
        font=dict(size=10)
    ),
    margin=dict(l=50, r=300, t=80, b=200),
    xaxis_tickangle=-45
)
st.plotly_chart(fig, use_container_width=True)

# 5. Mobile Banking Adoption
st.header('5. Mobile Banking Adoption')
df['Mobile_Banking_Penetration'] = df['Contratos_celular_10mil_adultos'] / 10000

fig = px.bar(
    df.sort_values('Mobile_Banking_Penetration', ascending=False), 
    y='Mobile_Banking_Penetration', 
    title='Mobile Banking Adoption by State'
)
fig.update_layout(
    xaxis_title='State', 
    yaxis_title='Mobile Banking Contracts per Adult', 
    height=600
)
st.plotly_chart(fig)

# 6. Comparison of Different Financial Institutions (Previous good version)
st.header('6. Comparison of Different Financial Institutions')
institution_columns = ['Sucursales_banca_comercial_10mil_adultos', 
                       'Sucursales_banca_desarrollo_10mil_adultos', 
                       'Sucursales_cooperativas_10mil_adultos', 
                       'Sucursales_microfinancieras_10mil_adultos']
institution_data = df[institution_columns]

institution_colors = {
    'Sucursales_banca_comercial_10mil_adultos': '#1f77b4',
    'Sucursales_banca_desarrollo_10mil_adultos': '#ff7f0e',
    'Sucursales_cooperativas_10mil_adultos': '#2ca02c',
    'Sucursales_microfinancieras_10mil_adultos': '#d62728'
}

institution_view = st.radio('Select view', ['Individual Institutions', 'Total Branches'])

if institution_view == 'Individual Institutions':
    selected_institution = st.selectbox('Select institution type', institution_columns)
    fig = px.bar(df.sort_values(selected_institution, ascending=False), 
                 y=selected_institution,
                 title=f'{selected_institution} per 10,000 Adults',
                 color_discrete_sequence=[institution_colors[selected_institution]])
    fig.update_layout(
        xaxis_title='State', 
        yaxis_title='Branches per 10,000 Adults', 
        height=700,
        legend=dict(
            orientation="h",          
            yanchor="top",
            y=-0.25,                  
            xanchor="center",
            x=0.5,
            font=dict(size=10)        
        ),
        margin=dict(l=50, r=50, t=80, b=250),  
        xaxis_tickangle=-45                   
    )
else:
    df['Total_Branches'] = institution_data.sum(axis=1)
    fig = px.bar(df.sort_values('Total_Branches', ascending=False), 
                 y=institution_columns,
                 title='Total Financial Institution Branches per 10,000 Adults',
                 color_discrete_map=institution_colors)
    fig.update_layout(
        xaxis_title='State', 
        yaxis_title='Branches per 10,000 Adults', 
        barmode='stack', 
        height=700,
        legend=dict(
            orientation="h",          
            yanchor="top",
            y=-0.25,                  
            xanchor="center",
            x=0.5,
            font=dict(size=10)        
        ),
        margin=dict(l=50, r=50, t=80, b=250),  
        xaxis_tickangle=-45                   
    )

fig.update_layout(
    legend=dict(
        orientation="h",          
        yanchor="top",
        y=-0.25,                  
        xanchor="center",
        x=0.5,
        font=dict(size=10)        
    ),
    margin=dict(l=50, r=50, t=80, b=250),      
    xaxis_tickangle=-45,                       
    height=700                                 
)
st.plotly_chart(fig, use_container_width=True)

# 7. Relationships between Various Indicators and Financial Inclusion
st.header('7. Relationships between Various Indicators and Financial Inclusion')
df['FI_Index'] = (
    df['Sucursales_banca_comercial_10mil_adultos'] + 
    df['Cajeros_10mil_adultos'] + 
    df['Corresponsales_10mil_adultos'] +
    df[account_columns].sum(axis=1) / 1000 +
    df[credit_columns].sum(axis=1) / 1000
) / 5

df['Poblacion'] = df['Poblacion'].fillna(df['Poblacion'].median())

indicators = [
    'TPV_10mil_adultos', 
    'Sucursales_banca_comercial_10mil_adultos', 
    'Cajeros_10mil_adultos', 
    'Corresponsales_10mil_adultos', 
    'Contratos_celular_10mil_adultos'
]

for indicator in indicators:
    fig = px.scatter(
        df, 
        x=indicator, 
        y='FI_Index', 
        size='Poblacion', 
        hover_name=df.index, 
        labels={
            indicator: f'{indicator} per 10,000 Adults', 
            'FI_Index': 'Financial Inclusion Index',
            'Poblacion': 'Population'
        },
        title=f'Relationship between {indicator} and Financial Inclusion'
    )
    st.plotly_chart(fig)

    correlation = df[indicator].corr(df['FI_Index'])
    st.write(f"Correlation between {indicator} and Financial Inclusion Index: {correlation:.2f}")

# 8. Top and Bottom States in Financial Inclusion
st.header('8. Top and Bottom States in Financial Inclusion')
top_3_fi = df['FI_Index'].nlargest(3)
bottom_3_fi = df['FI_Index'].nsmallest(3)

st.write("Top 3 states with highest financial inclusion:")
st.write(top_3_fi)
st.write("Bottom 3 states with lowest financial inclusion:")
st.write(bottom_3_fi)

# Footer
st.markdown(
    'Made by [Valentin Mendez](https://www.linkedin.com/in/valentemendez/) using information from the [CNBV](https://datos.gob.mx/busca/organization/2a93da6c-8c17-4671-a334-984536ac9d61?tags=inclusion)'
)

# Hide the "Made with Streamlit" footer
hide_streamlit_style = """
<style>
footer {visibility: hidden;}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)