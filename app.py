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
    # Filter out "Sin identificar"
    df = df[df.index != 'Sin identificar']
    return df

df = load_data()

st.title('Financial Inclusion Analysis - Mexico, June 2024')

# 1. Population Demographics
st.header('1. Population demographics')
df['Adult_Population_Percentage'] = df['Poblacion_adulta'] / df['Poblacion'] * 100
df['Superficie_km2'] = df['Superficie_km2'].fillna(df['Superficie_km2'].median())

fig = px.scatter(df, x='Poblacion', y='Adult_Population_Percentage', 
                 size='Superficie_km2', hover_name=df.index, 
                 labels={'Poblacion': 'total population', 
                         'Adult_Population_Percentage': 'adult population as (%)', 
                         'Superficie_km2': 'Area (km²)'},
                 title='Population demographics by state; size represents area')
st.plotly_chart(fig)

# 2. Banking Infrastructure Availability
st.header('2. Banking infrastructure availability')

# Add a dictionary for friendly names
infrastructure_labels = {
    'Sucursales_banca_comercial_10mil_adultos': 'Commercial bank branches',
    'Cajeros_10mil_adultos': 'ATMs',
    'Corresponsales_10mil_adultos': 'Banking agents (corresponsales)'
}

infrastructure_metrics = {
    'Sucursales_banca_comercial_10mil_adultos': '#1f77b4',
    'Cajeros_10mil_adultos': '#2ca02c',
    'Corresponsales_10mil_adultos': '#d62728'
}

selected_metric = st.selectbox('Select infrastructure type:', 
                             list(infrastructure_metrics.keys()),
                             format_func=lambda x: infrastructure_labels[x],
                             key='infrastructure')

fig = px.bar(df.sort_values(selected_metric, ascending=False), 
             y=selected_metric, 
             title=f'{infrastructure_labels[selected_metric]} per 10,000 Adults',
             color_discrete_sequence=[infrastructure_metrics[selected_metric]])

fig.update_layout(
    xaxis_title='state', 
    yaxis_title='number per 10,000 adults', 
    height=600,
    xaxis_tickangle=-45
)
st.plotly_chart(fig)

# 3. Account Ownership by Type
st.header('3. Account ownership by type')
account_columns = [
    'Cuentas_Nivel1_10mil_adultos_Banca', 
    'Cuentas_Nivel2_10mil_adultos_Banca', 
    'Cuentas_Nivel3_10mil_adultos_Banca', 
    'Cuentas_cuentas_transaccionales_tradicionales_10mil_adultos_Banca'
]

account_labels = {
    'Cuentas_Nivel1_10mil_adultos_Banca': 'Cuentas nivel 1',
    'Cuentas_Nivel2_10mil_adultos_Banca': 'Cuentas nivel 2',
    'Cuentas_Nivel3_10mil_adultos_Banca': 'Cuentas nivel 3',
    'Cuentas_cuentas_transaccionales_tradicionales_10mil_adultos_Banca': 'Cuentas transaccionales tradicionales'
}

view_type = st.radio('Select view type', ['Absolute numbers', 'Percentage'])

if view_type == 'Absolute numbers':
    account_data_abs = df[account_columns]
    account_data_renamed = account_data_abs.rename(columns=account_labels)
    fig = px.bar(
        account_data_renamed.sort_values(list(account_labels.values())[0], ascending=False),
        y=list(account_labels.values()),
        title='Account ownership by type per 10,000 adults'
    )
    fig.update_layout(
        xaxis_title='state', 
        yaxis_title='accounts per 10,000 adults', 
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
st.header('4. Credit product penetration')
credit_columns = [
    'Creditos_hipotecarios_10mil_adultos_Banca', 
    'Creditos_personales_10mil_adultos_Banca', 
    'Creditos_nomina_10mil_adultos_Banca', 
    'Creditos_automotrices_10mil_adultos_Banca', 
    'Creditos_ABCD_10mil_adultos_Banca'
]

credit_labels = {
    'Creditos_hipotecarios_10mil_adultos_Banca': 'Mortgage (Hipotecarios)',
    'Creditos_personales_10mil_adultos_Banca': 'Personal (Personales)',
    'Creditos_nomina_10mil_adultos_Banca': 'Salary (Nómina)',
    'Creditos_automotrices_10mil_adultos_Banca': 'Automotive (Automotriz)',
    'Creditos_ABCD_10mil_adultos_Banca': 'ABCD'
}

credit_data_renamed = df[credit_columns].rename(columns=credit_labels)
fig = px.bar(
    credit_data_renamed.sort_values('Mortgage (Hipotecarios)', ascending=False), 
    y=list(credit_labels.values()),
    title='Credit product penetration per 10,000 adults'
)
fig.update_layout(
    xaxis_title='state', 
    yaxis_title='credits per 10,000 adults', 
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
st.header('5. Mobile banking adoption')
df['Mobile_Banking_Penetration'] = df['Contratos_celular_10mil_adultos'] / 10000

fig = px.bar(
    df.sort_values('Mobile_Banking_Penetration', ascending=False), 
    y='Mobile_Banking_Penetration', 
    title='Mobile banking adoption by state'
)
fig.update_layout(
    xaxis_title='state', 
    yaxis_title='mobile banking contracts per adult', 
    height=600,
    xaxis_tickangle=-45
)
st.plotly_chart(fig)

# 6. Comparison of different financial institutions
st.header('6. Comparison of different financial institutions')
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

institution_view = st.radio('Select view', ['Individual institutions', 'Total branches'])

institution_labels = {
    'Sucursales_banca_comercial_10mil_adultos': 'Commercial banks',
    'Sucursales_banca_desarrollo_10mil_adultos': 'Development banks',
    'Sucursales_cooperativas_10mil_adultos': 'Cooperatives',
    'Sucursales_microfinancieras_10mil_adultos': 'Microfinance institutions',
    'variable': 'Institution type'
}

if institution_view == 'Individual institutions':
    selected_institution = st.selectbox('Select institution type', 
                                      institution_columns,
                                      format_func=lambda x: institution_labels[x])
    fig = px.bar(df.sort_values(selected_institution, ascending=False), 
                 y=selected_institution,
                 title=f'{institution_labels[selected_institution]} per 10,000 adults',
                 color_discrete_sequence=[institution_colors[selected_institution]],
                 labels={
                     selected_institution: institution_labels[selected_institution],
                     "variable": ""  # This removes the "Institution type" label
                 })
    fig.update_layout(
        xaxis_title='state', 
        yaxis_title='branches per 10,000 adults', 
        height=700,
        width=1200,
        showlegend=False,  # This hides the legend for individual view
        margin=dict(l=50, r=300, t=80, b=200),
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig)
else:
    df['Total_Branches'] = institution_data.sum(axis=1)
    
    # Create a new DataFrame with renamed columns for plotting
    plot_data = df[institution_columns].copy()
    plot_data.columns = [institution_labels[col] for col in institution_columns]
    
    fig = px.bar(plot_data.sort_values('Commercial banks', ascending=False), 
                 y=list(institution_labels.values())[:4],  # Only take the first 4 values (excluding 'variable')
                 title='Total financial institution branches per 10,000 adults',
                 color_discrete_map={
                     'Commercial banks': '#1f77b4',
                     'Development banks': '#ff7f0e',
                     'Cooperatives': '#2ca02c',
                     'Microfinance institutions': '#d62728'
                 })
    fig.update_layout(
        xaxis_title='state', 
        yaxis_title='branches per 10,000 adults', 
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

# 7. Relationships between Various Indicators and Financial Inclusion
st.header('7. Relationships between various indicators and financial inclusion index')
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

indicator_labels = {
    'TPV_10mil_adultos': 'POS',
    'Sucursales_banca_comercial_10mil_adultos': 'Commercial bank branches', 
    'Cajeros_10mil_adultos': 'ATMs',
    'Corresponsales_10mil_adultos': 'Banking agents',
    'Contratos_celular_10mil_adultos': 'Mobile banking contracts'
}

for indicator in indicators:
    fig = px.scatter(
        df, 
        x=indicator, 
        y='FI_Index', 
        size='Poblacion', 
        hover_name=df.index, 
        labels={
            indicator: f'{indicator_labels[indicator]} per 10,000 adults', 
            'FI_Index': 'Financial Inclusion Index',
            'Poblacion': 'Population'
        },
        title=f'Relationship between {indicator_labels[indicator]} and Financial Inclusion Index; size = population'
    )
    st.plotly_chart(fig)

    correlation = df[indicator].corr(df['FI_Index'])
    st.write(f"*Correlation between {indicator_labels[indicator]} and Financial Inclusion Index: {correlation:.2f}*")

# 8. Top and Bottom States in Financial Inclusion
st.header('8. Financial Inclusion Index by state')

# Filter out "Sin identificar"
df_filtered = df[df.index != 'Sin identificar']

top_3_fi = df_filtered['FI_Index'].nlargest(3)
bottom_3_fi = df_filtered['FI_Index'].nsmallest(3)

st.write("Top 3 states with highest financial inclusion:")
st.write(top_3_fi)
st.write("Bottom 3 states with lowest financial inclusion:")
st.write(bottom_3_fi)

# Add bar chart for all states (excluding "Sin identificar")
fig = px.bar(df_filtered.sort_values('FI_Index', ascending=False), 
             y='FI_Index',
             title='Financial Inclusion Index by state',
             color_discrete_sequence=['#90EE90'])  # Light green color

fig.update_layout(
    xaxis_title='State',
    yaxis_title='Financial Inclusion Index',
    height=600,
    xaxis_tickangle=-45,
    showlegend=False
)

st.plotly_chart(fig)

import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv("Base_de_Datos_de_Inclusion_Financiera_202406 - Hoja 1.csv")
    return df

df = load_data()

year_col = "Periodo_Año"
quarter_col = "Periodo_Trimestre"

# Filter data according to rules:
df_filtered = pd.DataFrame()
for year in df[year_col].unique():
    if year == 2024:
        df_year = df[(df[year_col] == year) & (df[quarter_col] == "2T")]
    else:
        df_year = df[(df[year_col] == year) & (df[quarter_col] == "4T")]
    df_filtered = pd.concat([df_filtered, df_year], ignore_index=True)

df_filtered = df_filtered.sort_values(by=year_col)

# Convert year to string for categorical x-axis in bar charts
df_filtered[year_col] = df_filtered[year_col].astype(str)

# Adjust column selections (modify indices as per your actual data structure)
infrastructure_cols = df_filtered.columns[3:11]
infra_map = {
    "Branches": infrastructure_cols[0],
    "ATMs": infrastructure_cols[1],
    "POS": infrastructure_cols[2],
    "Places with POS": infrastructure_cols[3],
    "Banking agents (corresponsales)": infrastructure_cols[4],
    "Mobile banking contracts": infrastructure_cols[5],
    "Transactions in ATMs": infrastructure_cols[6],
    "Transactions in POS": infrastructure_cols[7]
}

captacion_types = df_filtered.columns[11:18]
captacion_total = df_filtered.columns[18]
captacion_map = {
    "Ahorro": captacion_types[0],
    "Plazo": captacion_types[1],
    "N1": captacion_types[2],
    "N2": captacion_types[3],
    "N3": captacion_types[4],
    "Tradicionales": captacion_types[5],
    "Simplificadas": captacion_types[6],
    "Total": captacion_total
}

credit_start_col = "Crédito\nBanca_Tarjeta de crédito"
credit_end_col = "Crédito\nBanca_Total"
credit_cols = df_filtered.loc[:, credit_start_col:credit_end_col].columns[:-1]
credit_total_col = df_filtered.loc[:, credit_start_col:credit_end_col].columns[-1]

credit_map = {}
for c in credit_cols:
    short_label = c.replace("Crédito\nBanca_", "").strip()
    credit_map[short_label] = c
credit_map["Total"] = credit_total_col

# EACP Captación mapping
captacion_eacp_cols = df_filtered.columns[19:23]  # Columns T to W
captacion_eacp_map = {
    "Ahorro EACP": captacion_eacp_cols[0],
    "Plazo EACP": captacion_eacp_cols[1],
    "Otras EACP": captacion_eacp_cols[2],
    "Total EACP": captacion_eacp_cols[3]
}

# EACP Crédito mapping
credito_eacp_cols = df_filtered.columns[31:37]  # Columns AF to AK
credito_eacp_map = {}
for c in credito_eacp_cols[:-1]:  # Exclude the total
    short_label = c.replace("Crédito\nEACP_", "").strip()
    credito_eacp_map[short_label] = c
credito_eacp_map["Total"] = credito_eacp_cols[-1]  # Add total separately

st.title("Financial Inclusion Analysis - Mexico, historical data")

###################################
# Infrastructure (Single Dropdown)
###################################
st.header("Infrastructure trends")
infra_choice = st.selectbox("Select type of infrastructure:", list(infra_map.keys()), index=0)

infra_col = infra_map[infra_choice]
infra_df = df_filtered[[year_col, infra_col]].copy()
# Single type: just show a bar chart with year on x and the value on y
fig_infra = px.bar(infra_df, x=year_col, y=infra_col, 
                   title=f"Infrastructure: {infra_choice}", 
                   color_discrete_sequence=["#CCCCCC"])  # Changed to light grey
fig_infra.update_layout(
    barmode='group',
    xaxis_title='year',
    yaxis_title='number of units'
)
st.plotly_chart(fig_infra, use_container_width=True)

###################################
# Captación (Single Dropdown)
###################################
st.header("Trends for 'Captación' - Banca")
capt_choice = st.selectbox("Select a type of 'Captación' (or total):", list(captacion_map.keys()), index=0)

if capt_choice == "Total":
    # Use total column directly (column S)
    capt_total_df = df_filtered[[year_col, captacion_total]].copy()
    fig_capt = px.bar(capt_total_df, x=year_col, y=captacion_total, 
                      title="Total Captación Banca",
                      color_discrete_sequence=["#1f77b4"])
    fig_capt.update_layout(
        xaxis_title='year',
        yaxis_title='number of accounts'
    )
    st.plotly_chart(fig_capt, use_container_width=True)
    st.markdown("""
        **Note:** The total is composed of:
        - Ahorro (Savings)
        - Plazo (Term deposits)
        - Tradicionales (Traditional)
        - Simplificadas (Simplified)
        
        Where N1, N2, and N3 accounts make up the Simplified accounts category.
    """)
else:
    # Single type chart remains the same
    capt_col = captacion_map[capt_choice]
    capt_df = df_filtered[[year_col, capt_col]].copy()
    fig_capt = px.bar(capt_df, x=year_col, y=capt_col, 
                      title=f"Captación: {capt_choice}",
                      color_discrete_sequence=["#1f77b4"])
    fig_capt.update_layout(
        xaxis_title='year',
        yaxis_title='number of accounts'
    )
    st.plotly_chart(fig_capt, use_container_width=True)

###################################
# Captación EACP (Single Dropdown)
###################################
st.header("Trends for 'Captación' - Entidades de Ahorro y Crédito Popular")
capt_eacp_choice = st.selectbox("Select a type of 'Captación' (or total):", list(captacion_eacp_map.keys()), index=0)

if capt_eacp_choice == "Total EACP":
    # Use column W directly
    capt_eacp_total_df = df_filtered[[year_col, captacion_eacp_map["Total EACP"]]].copy()
    fig_capt_eacp = px.bar(capt_eacp_total_df, x=year_col, y=captacion_eacp_map["Total EACP"],
                          title="Total Captación EACP",
                          color_discrete_sequence=['#2ca02c'])
    fig_capt_eacp.update_layout(
        xaxis_title='year',
        yaxis_title='number of accounts'
    )
    st.plotly_chart(fig_capt_eacp, use_container_width=True)
else:
    # Single type remains the same
    capt_eacp_col = captacion_eacp_map[capt_eacp_choice]
    capt_eacp_df = df_filtered[[year_col, capt_eacp_col]].copy()
    fig_capt_eacp = px.bar(capt_eacp_df, x=year_col, y=capt_eacp_col,
                          title=f"Captación EACP: {capt_eacp_choice}",
                          color_discrete_sequence=['#2ca02c'])
    fig_capt_eacp.update_layout(
        xaxis_title='year',
        yaxis_title='number of accounts'
    )
    st.plotly_chart(fig_capt_eacp, use_container_width=True)

###################################
# Crédito (Single Dropdown)
###################################
st.header("Trends for 'Crédito' - Banca")
credit_choice = st.selectbox("Select a type of 'Crédito' (or total):", list(credit_map.keys()), index=0)

if credit_choice == "Total":
    # Use column AE directly
    credit_total_df = df_filtered[[year_col, credit_total_col]].copy()
    fig_credit = px.bar(credit_total_df, x=year_col, y=credit_total_col,
                       title="Total Crédito Banca",
                       color_discrete_sequence=["#1f77b4"])
    fig_credit.update_layout(
        xaxis_title='year',
        yaxis_title='number of credits'
    )
    st.plotly_chart(fig_credit, use_container_width=True)
else:
    # Single type remains the same
    credit_col = credit_map[credit_choice]
    credit_df = df_filtered[[year_col, credit_col]].copy()
    fig_credit = px.bar(credit_df, x=year_col, y=credit_col,
                       title=f"Crédito: {credit_choice}",
                       color_discrete_sequence=["#1f77b4"])
    fig_credit.update_layout(
        xaxis_title='year',
        yaxis_title='number of credits'
    )
    st.plotly_chart(fig_credit, use_container_width=True)

###################################
# Crédito EACP (Single Dropdown)
###################################
st.header("Trends for 'Crédito' - Entidades de Ahorro y Crédito Popular")
# Modify the map to only include AF to AI and total AJ
credito_eacp_map = {}
for c in credito_eacp_cols[0:4]:  # Only take AF to AI
    short_label = c.replace("Crédito\nEACP_", "").strip() + " EACP"
    credito_eacp_map[short_label] = c
credito_eacp_map["Total EACP"] = credito_eacp_cols[-2]  # Add AJ as total

credit_eacp_choice = st.selectbox("Select a type of 'Crédito' (or total):", list(credito_eacp_map.keys()), index=0)

if credit_eacp_choice == "Total EACP":
    # Use column AJ directly
    credit_eacp_total_col = credito_eacp_cols[-2]  # This is column AJ
    credit_eacp_total_df = df_filtered[[year_col, credit_eacp_total_col]].copy()
    fig_credit_eacp = px.bar(credit_eacp_total_df, x=year_col, y=credit_eacp_total_col,
                            title="Total Crédito EACP",
                            color_discrete_sequence=['#2ca02c'])
    fig_credit_eacp.update_layout(
        xaxis_title='year',
        yaxis_title='number of credits'
    )
    st.plotly_chart(fig_credit_eacp, use_container_width=True)
else:
    # Single type remains the same
    credit_eacp_col = credito_eacp_map[credit_eacp_choice]
    credit_eacp_df = df_filtered[[year_col, credit_eacp_col]].copy()
    fig_credit_eacp = px.bar(credit_eacp_df, x=year_col, y=credit_eacp_col,
                            title=f"Crédito: {credit_eacp_choice}",
                            color_discrete_sequence=['#2ca02c'])
    fig_credit_eacp.update_layout(
        xaxis_title='year',
        yaxis_title='number of credits'
    )
    st.plotly_chart(fig_credit_eacp, use_container_width=True)

###################################
# Gender Analysis - Cards
###################################
st.header("Gender Analysis - Debit and Credit Cards")

# Filter data according to rules (4T except 2024 which is 2T)
df_gender = pd.DataFrame()
for year in df[year_col].unique():
    if year == 2024:
        df_year = df[(df[year_col] == year) & (df[quarter_col] == "2T")]
    else:
        df_year = df[(df[year_col] == year) & (df[quarter_col] == "4T")]
    df_gender = pd.concat([df_gender, df_year], ignore_index=True)

# Create DataFrames for debit and credit cards
debit_data = pd.DataFrame({
    'Year': df_gender[year_col],
    'Women': df_gender.iloc[:, 46].str.replace(',', '').astype(float),
    'Men': df_gender.iloc[:, 47].str.replace(',', '').astype(float)
})

credit_data = pd.DataFrame({
    'Year': df_gender[year_col],
    'Women': df_gender.iloc[:, 49].str.replace(',', '').astype(float),
    'Men': df_gender.iloc[:, 50].str.replace(',', '').astype(float)
})

# Filter from 2018 onwards and sort
debit_data = debit_data[debit_data['Year'] >= 2018].sort_values('Year')
credit_data = credit_data[credit_data['Year'] >= 2018].sort_values('Year')

# Calculate percentages for debit cards
debit_data['Total'] = debit_data['Men'] + debit_data['Women']
debit_data['Men %'] = (debit_data['Men'] / debit_data['Total'] * 100).round(1)
debit_data['Women %'] = (debit_data['Women'] / debit_data['Total'] * 100).round(1)

# Calculate percentages for credit cards
credit_data['Total'] = credit_data['Men'] + credit_data['Women']
credit_data['Men %'] = (credit_data['Men'] / credit_data['Total'] * 100).round(1)
credit_data['Women %'] = (credit_data['Women'] / credit_data['Total'] * 100).round(1)

# Debit Cards Analysis
st.subheader("Debit cards by gender")

# Line chart for debit cards (separate lines for men and women)
fig_debit_line = px.line(debit_data, x='Year', y=['Women', 'Men'],
                    title='Debit cards by gender over time',
                    color_discrete_map={'Women': '#ff7f0e', 'Men': '#1f77b4'})
fig_debit_line.update_layout(
    xaxis_title='year',
    yaxis_title='number of cards',
    legend_title='gender'
)
st.plotly_chart(fig_debit_line, use_container_width=True)

# Stacked bar chart for debit cards (percentages)
fig_debit_bar = px.bar(debit_data, x='Year', y=['Women %', 'Men %'],
                       title='Debit cards by gender over time (% distribution)',
                       color_discrete_map={'Women %': '#ff7f0e', 'Men %': '#1f77b4'})
fig_debit_bar.update_layout(
    xaxis_title='year',
    yaxis_title='percentage',
    barmode='stack',
    legend_title='gender',
    yaxis_range=[0, 100]  # Force y-axis to be 0-100%
)
st.plotly_chart(fig_debit_bar, use_container_width=True)

# Credit Cards Analysis
st.subheader("Credit cards by gender")

# Line chart for credit cards (separate lines for men and women)
fig_credit_line = px.line(credit_data, x='Year', y=['Women', 'Men'],
                     title='Credit cards by gender over time',
                     color_discrete_map={'Women': '#ff7f0e', 'Men': '#1f77b4'})
fig_credit_line.update_layout(
    xaxis_title='year',
    yaxis_title='number of cards',
    legend_title='gender'
)
st.plotly_chart(fig_credit_line, use_container_width=True)

# Stacked bar chart for credit cards (percentages)
fig_credit_bar = px.bar(credit_data, x='Year', y=['Women %', 'Men %'],
                        title='Credit cards by gender over time (% distribution)',
                        color_discrete_map={'Women %': '#ff7f0e', 'Men %': '#1f77b4'})
fig_credit_bar.update_layout(
    xaxis_title='year',
    yaxis_title='percentage',
    barmode='stack',
    legend_title='gender',
    yaxis_range=[0, 100]  # Force y-axis to be 0-100%
)
st.plotly_chart(fig_credit_bar, use_container_width=True)

# Cards analysis - brand distribution
st.header("Cards analysis - brand distribution")

# Load the analysis data
analysis_df = pd.read_csv('Consulta_20241224-151312014 - Analysis.csv')

# Credit Cards Total Trend

# Create DataFrame for credit total trend
credit_total_data = pd.DataFrame({
    'Year': analysis_df.columns[1:],  # Years from 2006 to 2024
    'Total Cards': analysis_df.iloc[0, 1:].values  # Total credit cards data
})

# Create line chart for credit total
fig_credit_total = px.line(
    credit_total_data,
    x='Year',
    y='Total Cards',
    title="Total credit cards",
)
fig_credit_total.update_layout(
    xaxis_title="year",
    yaxis_title="number of cards",
    showlegend=False,
    xaxis={'tickmode': 'linear', 'dtick': 1}  # Show all years
)
st.plotly_chart(fig_credit_total, use_container_width=True)

# Credit Cards Distribution
view_type_credit = st.radio("Select view type", ['Absolute numbers', 'Percentage'], key="credit_view")

# Prepare data for credit cards distribution
credit_brands_data = pd.DataFrame({
    'Year': analysis_df.columns[1:],
    'Mastercard': analysis_df.iloc[1, 1:].values,
    'Visa': analysis_df.iloc[2, 1:].values,
    'Other Brands': analysis_df.iloc[3, 1:].values
}).melt('Year', var_name='Brand', value_name='Cards')

if view_type_credit == 'Percentage':
    # Calculate percentages by year
    credit_brands_data['Cards'] = credit_brands_data['Cards'].astype(float)  # Convert to float first
    credit_brands_data['Cards'] = credit_brands_data.groupby('Year').apply(
        lambda x: (x['Cards'] / x['Cards'].sum() * 100).round(1)
    ).reset_index(level=0, drop=True)

# Create stacked bar chart for credit distribution
fig_credit_dist = px.bar(
    credit_brands_data,
    x='Year',
    y='Cards',
    color='Brand',
    title="Credit cards distribution by brand",
    labels={
        "Year": "year",
        "Cards": "percentage" if view_type_credit == 'Percentage' else "units"
    },
    barmode='stack',
    color_discrete_map={
        'Mastercard': '#FF0000',
        'Visa': '#0066CC',
        'Other Brands': '#808080'
    }
)
fig_credit_dist.update_layout(
    xaxis={'tickmode': 'linear', 'dtick': 1},  # Show all years
    yaxis_ticksuffix='%' if view_type_credit == 'Percentage' else ''
)
st.plotly_chart(fig_credit_dist, use_container_width=True)

# Debit Cards Total Trend

# Create DataFrame for debit total trend
debit_total_data = pd.DataFrame({
    'Year': analysis_df.columns[1:],  # Years from 2006 to 2024
    'Total Cards': analysis_df.iloc[4, 1:].values  # Total debit cards data
})

# Create line chart for debit total
fig_debit_total = px.line(
    debit_total_data,
    x='Year',
    y='Total Cards',
    title="Total debit cards",
)
fig_debit_total.update_layout(
    xaxis_title="year",
    yaxis_title="number of cards",
    showlegend=False,
    xaxis={'tickmode': 'linear', 'dtick': 1}  # Show all years
)
st.plotly_chart(fig_debit_total, use_container_width=True)

# Debit Cards Distribution
view_type_debit = st.radio("Select view type", ['Absolute numbers', 'Percentage'], key="debit_view")

# Prepare data for debit cards distribution
debit_brands_data = pd.DataFrame({
    'Year': analysis_df.columns[1:],
    'Mastercard': analysis_df.iloc[5, 1:].values,
    'Visa': analysis_df.iloc[6, 1:].values,
    'Other Brands': analysis_df.iloc[7, 1:].values
}).melt('Year', var_name='Brand', value_name='Cards')

if view_type_debit == 'Percentage':
    # Calculate percentages by year
    debit_brands_data['Cards'] = debit_brands_data['Cards'].astype(float)  # Convert to float first
    debit_brands_data['Cards'] = debit_brands_data.groupby('Year').apply(
        lambda x: (x['Cards'] / x['Cards'].sum() * 100).round(1)
    ).reset_index(level=0, drop=True)

# Create stacked bar chart for debit distribution
fig_debit_dist = px.bar(
    debit_brands_data,
    x='Year',
    y='Cards',
    color='Brand',
    title="Debit cards distribution by brand",
    labels={
        "Year": "year",
        "Cards": "percentage" if view_type_debit == 'Percentage' else "units"
    },
    barmode='stack',
    color_discrete_map={
        'Mastercard': '#FF0000',
        'Visa': '#0066CC',
        'Other Brands': '#808080'
    }
)
fig_debit_dist.update_layout(
    xaxis={'tickmode': 'linear', 'dtick': 1},  # Show all years
    yaxis_ticksuffix='%' if view_type_debit == 'Percentage' else ''
)
st.plotly_chart(fig_debit_dist, use_container_width=True)

# New section for yearly totals
st.header("Card transactional volume ($) by category")

# Read the yearly totals CSV
yearly_totals = pd.read_csv('Transacciones_totales.csv')

# Dictionary for label translations
base_translations = {
    'Agencias de Viajes': 'Travel Agencies',
    'Agregadores': 'Aggregators',
    'Aseguradoras': 'Insurance',
    'Beneficencia': 'Charity',
    'Colegios y Universidades': 'Universities',
    'Comida Rápida': 'Fast Food',
    'Educación Básica': 'Basic Education',
    'Entretenimiento': 'Entertainment',
    'Estacionamientos': 'Parking',
    'Farmacias': 'Pharmacies',
    'Gasolineras': 'Gas Stations',
    'Gobierno': 'Government',
    'Grandes superficies': 'Department Stores',
    'Guarderías': 'Daycare',
    'Hospitales': 'Hospitals',
    'Hoteles': 'Hotels',
    'Misceláneos': 'Miscellaneous',
    'Médicos y dentistas': 'Healthcare',
    'No definido': 'Undefined',
    'Otros': 'Others',
    'Peaje': 'Toll',
    'Refacciones y ferretería': 'Hardware Stores',
    'Renta de Autos': 'Car Rental',
    'Restaurantes': 'Restaurants',
    'Salones de belleza': 'Beauty Salons',
    'Supermercados': 'Supermarkets',
    'Telecomunicaciones': 'Telecommunications',
    'Transporte Aéreo': 'Air Transport',
    'Transporte Terrestre de Pasajeros': 'Ground Transport',
    'Ventas al detalle (Retail)': 'Retail'
}

# Create dictionaries for total, credit, and debit translations
label_translations = {
    f'Total de monto operado a través de tarjetas en {k}': v for k, v in base_translations.items()
}
credit_translations = {
    f'Monto operado a través de tarjetas de crédito en {k}': v for k, v in base_translations.items()
}
debit_translations = {
    f'Monto operado a través de tarjetas de débito en {k}': v for k, v in base_translations.items()
}

# Get total values (always from first row, columns 'Total 2023' and 'Total 2024 (eoy)')
total_2023 = float(yearly_totals.iloc[0]['Total 2023'].replace(',', ''))
total_2024 = float(yearly_totals.iloc[0]['Total 2024 (eoy)'].replace(',', ''))
delta_percentage = float(yearly_totals.iloc[0]['D% 2023 to 2024'].rstrip('%'))

# Display totals in trillions
st.write(f"2023 total: {total_2023/1e12:.2f} trillion MXN")
st.write(f"2024 total: {total_2024/1e12:.2f} trillion MXN")
st.write(f"Year-over-year growth: {delta_percentage:.1f}%")

# Create pie chart for 2024 categories
categories_2024 = yearly_totals.iloc[1:][['Título', 'Total 2024 (eoy)', '% 2024 (eoy)']]
categories_2024['Total 2024 (B)'] = categories_2024['Total 2024 (eoy)'].apply(lambda x: float(x.replace(',', ''))/1e9)
categories_2024['Percentage'] = categories_2024['% 2024 (eoy)'].apply(lambda x: float(x.rstrip('%')))
categories_2024['Clean Label'] = categories_2024['Título'].map(label_translations)

# Create custom hover text
categories_2024['hover_text'] = categories_2024.apply(
    lambda row: f"{row['Clean Label']}<br>{row['Total 2024 (B)']:.1f}B MXN<br>{row['Percentage']:.1f}%", 
    axis=1
)

fig_pie = px.pie(
    categories_2024,
    values='Total 2024 (B)',
    names='Clean Label',
    title="Transaction distribution by category in 2024",
    custom_data=['hover_text']
)

# Update hover template
fig_pie.update_traces(
    hovertemplate="%{customdata[0]}<extra></extra>",
    textinfo='percent+label'
)

st.plotly_chart(fig_pie, use_container_width=True)

# Create bar chart for year-over-year growth by category
growth_data = yearly_totals.iloc[1:][['Título', 'D% 2023 to 2024']]
growth_data['Growth'] = growth_data['D% 2023 to 2024'].apply(lambda x: float(x.rstrip('%')) if isinstance(x, str) else x)
growth_data['Clean Label'] = growth_data['Título'].map(label_translations)
growth_data = growth_data.dropna()  # Remove any NaN values
# Exclude "Undefined" category
growth_data = growth_data[growth_data['Clean Label'] != 'Undefined']
growth_data = growth_data.sort_values('Growth', ascending=True)

# Create bar chart with increased height
fig_growth = px.bar(
    growth_data,
    x='Growth',
    y='Clean Label',
    orientation='h',
    title="Year-over-year growth by category (2023 to 2024), excluding 'Undefined'",
    labels={"Growth": "growth (%)", "Clean Label": "category"}
)

fig_growth.update_traces(
    texttemplate='%{x:.1f}%',
    textposition='outside'
)

fig_growth.update_layout(
    xaxis_title="growth (%)",
    yaxis_title="",
    showlegend=False,
    height=800,  # Increased height to accommodate all categories
    margin=dict(l=50, r=50, t=50, b=50)
)

st.plotly_chart(fig_growth, use_container_width=True)

# Credit Cards Analysis
st.subheader("Credit card transactional volume ($)")

# Read credit transactions CSV
credit_totals = pd.read_csv('Transacciones_credito.csv')

# Get credit total values (using credit_translations)
credit_total_2023 = float(credit_totals.iloc[0]['Total 2023'].replace(',', ''))
credit_total_2024 = float(credit_totals.iloc[0]['Total 2024 (eoy)'].replace(',', ''))
credit_delta = float(credit_totals.iloc[0]['D% 2023 to 2024'].rstrip('%'))

# Display credit totals in trillions
st.write(f"2023 total: {credit_total_2023/1e12:.2f} trillion MXN")
st.write(f"2024 total: {credit_total_2024/1e12:.2f} trillion MXN")
st.write(f"Year-over-year growth: {credit_delta:.1f}%")

# Create pie chart for credit categories 2024
credit_categories = credit_totals.iloc[1:][['Título', 'Total 2024 (eoy)', '% 2024 (eoy)']]
credit_categories['Total 2024 (B)'] = credit_categories['Total 2024 (eoy)'].apply(lambda x: float(x.replace(',', ''))/1e9)
credit_categories['Percentage'] = credit_categories['% 2024 (eoy)'].apply(lambda x: float(x.rstrip('%')))
credit_categories['Clean Label'] = credit_categories['Título'].map(credit_translations)

credit_categories['hover_text'] = credit_categories.apply(
    lambda row: f"{row['Clean Label']}<br>{row['Total 2024 (B)']:.1f}B MXN<br>{row['Percentage']:.1f}%", 
    axis=1
)

fig_credit_pie = px.pie(
    credit_categories,
    values='Total 2024 (B)',
    names='Clean Label',
    title="Credit card transaction distribution by category in 2024",
    custom_data=['hover_text']
)

fig_credit_pie.update_traces(
    hovertemplate="%{customdata[0]}<extra></extra>",
    textinfo='percent+label'
)

st.plotly_chart(fig_credit_pie, use_container_width=True)

# Credit growth bar chart
credit_growth = credit_totals.iloc[1:][['Título', 'D% 2023 to 2024']]
credit_growth['Growth'] = credit_growth['D% 2023 to 2024'].apply(lambda x: float(x.rstrip('%')) if isinstance(x, str) else x)
credit_growth['Clean Label'] = credit_growth['Título'].map(credit_translations)
credit_growth = credit_growth.dropna()
# Exclude "Undefined" category
credit_growth = credit_growth[credit_growth['Clean Label'] != 'Undefined']
credit_growth = credit_growth.sort_values('Growth', ascending=True)

fig_credit_growth = px.bar(
    credit_growth,
    x='Growth',
    y='Clean Label',
    orientation='h',
    title="Credit card year-over-year growth by category (2023 to 2024), excluding 'Undefined'",
    labels={"Growth": "growth (%)", "Clean Label": "category"}
)

fig_credit_growth.update_traces(
    texttemplate='%{x:.1f}%',
    textposition='outside'
)

fig_credit_growth.update_layout(
    xaxis_title="growth (%)",
    yaxis_title="",
    showlegend=False,
    height=800,  # Increased height
    margin=dict(l=50, r=50, t=50, b=50)
)

st.plotly_chart(fig_credit_growth, use_container_width=True)

# Debit Cards Analysis
st.subheader("Debit card transactional volume ($)")

# Read debit transactions CSV
debit_totals = pd.read_csv('Transacciones_debito.csv')

# Get debit total values
debit_total_2023 = float(debit_totals.iloc[0]['Total 2023'].replace(',', ''))
debit_total_2024 = float(debit_totals.iloc[0]['Total 2024 (eoy)'].replace(',', ''))
debit_delta = float(debit_totals.iloc[0]['D% 2023 to 2024'].rstrip('%'))

# Display debit totals in trillions
st.write(f"2023 total: {debit_total_2023/1e12:.2f} trillion MXN")
st.write(f"2024 total: {debit_total_2024/1e12:.2f} trillion MXN")
st.write(f"Year-over-year growth: {debit_delta:.1f}%")

# Create pie chart for debit categories 2024
debit_categories = debit_totals.iloc[1:][['Título', 'Total 2024 (eoy)', '% 2024 (eoy)']]
debit_categories['Total 2024 (B)'] = debit_categories['Total 2024 (eoy)'].apply(lambda x: float(x.replace(',', ''))/1e9)
debit_categories['Percentage'] = debit_categories['% 2024 (eoy)'].apply(lambda x: float(x.rstrip('%')))
debit_categories['Clean Label'] = debit_categories['Título'].map(debit_translations)

debit_categories['hover_text'] = debit_categories.apply(
    lambda row: f"{row['Clean Label']}<br>{row['Total 2024 (B)']:.1f}B MXN<br>{row['Percentage']:.1f}%", 
    axis=1
)

fig_debit_pie = px.pie(
    debit_categories,
    values='Total 2024 (B)',
    names='Clean Label',
    title="Debit card transaction distribution by category in 2024",
    custom_data=['hover_text']
)

fig_debit_pie.update_traces(
    hovertemplate="%{customdata[0]}<extra></extra>",
    textinfo='percent+label'
)

st.plotly_chart(fig_debit_pie, use_container_width=True)

# Debit growth bar chart
debit_growth = debit_totals.iloc[1:][['Título', 'D% 2023 to 2024']]
debit_growth['Growth'] = debit_growth['D% 2023 to 2024'].apply(lambda x: float(x.rstrip('%')) if isinstance(x, str) else x)
debit_growth['Clean Label'] = debit_growth['Título'].map(debit_translations)
debit_growth = debit_growth.dropna()
# Exclude "Undefined" category
debit_growth = debit_growth[debit_growth['Clean Label'] != 'Undefined']
debit_growth = debit_growth.sort_values('Growth', ascending=True)

fig_debit_growth = px.bar(
    debit_growth,
    x='Growth',
    y='Clean Label',
    orientation='h',
    title="Debit card year-over-year growth by category (2023 to 2024), excluding 'Undefined'",
    labels={"Growth": "growth (%)", "Clean Label": "category"}
)

fig_debit_growth.update_traces(
    texttemplate='%{x:.1f}%',
    textposition='outside'
)

fig_debit_growth.update_layout(
    xaxis_title="growth (%)",
    yaxis_title="",
    showlegend=False,
    height=800,  # Increased height
    margin=dict(l=50, r=50, t=50, b=50)
)

st.plotly_chart(fig_debit_growth, use_container_width=True)

# Footer
st.markdown(
    'Made by [Valentin Mendez](https://www.linkedin.com/in/valentemendez/) using information from the [CNBV](https://datos.gob.mx/busca/organization/2a93da6c-8c17-4671-a334-984536ac9d61?tags=inclusion) and [Banxico](https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=21&accion=consultarDirectorioCuadros&locale=es)'
)

# Hide the "Made with Streamlit" footer
hide_streamlit_style = """
<style>
footer {visibility: hidden;}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)