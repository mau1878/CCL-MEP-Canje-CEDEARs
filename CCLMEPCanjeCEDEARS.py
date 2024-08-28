import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# Load the CSV file
df = pd.read_csv('CEDEARcsv.csv')

# Fetch the latest data for each ticker from Yahoo Finance
def fetch_latest_data(tickers):
    data = yf.download(tickers, period='1d', interval='1m')
    latest_data = data['Close'].iloc[-1]
    volumes = data['Volume'].iloc[-1]
    return latest_data, volumes

# Initialize empty dictionaries to store prices and volumes
prices = {}
volumes = {}

# Fetch the latest price and volume data for all tickers
for column in ["CEDEAR-ARS", "CEDEARD", "Subyacente"]:
    unique_tickers = df[column].unique()
    for ticker in unique_tickers:
        latest_price, latest_volume = fetch_latest_data(ticker)
        prices[ticker] = latest_price
        volumes[ticker] = latest_volume

# Calculate the X and Y values for the scatter plots
df['X_CCL'] = df.apply(lambda row: (prices[row['CEDEAR-ARS']] * row['Ratio']) / prices[row['Subyacente']], axis=1)
df['Y_CCL'] = df.apply(lambda row: prices[row['CEDEAR-ARS']] * volumes[row['CEDEAR-ARS']], axis=1)

df['X_MEP'] = df.apply(lambda row: (prices[row['CEDEAR-ARS']] * row['Ratio']) / prices[row['CEDEARD']], axis=1)
df['Y_MEP'] = df.apply(lambda row: prices[row['CEDEARD']] * volumes[row['CEDEARD']], axis=1)

df['X_Canje'] = df.apply(lambda row: (prices[row['CEDEARD']] * row['Ratio']) / prices[row['Subyacente']], axis=1)
df['Y_Canje'] = df.apply(lambda row: prices[row['CEDEARD']] * volumes[row['CEDEARD']], axis=1)

# Create interactive scatter plots
st.title('CEDEAR Analysis')

# Scatter plot 1: Dólar CCL de CEDEARs
st.subheader('Scatter Plot 1: Dólar CCL de CEDEARs')
x_range_ccl = st.slider('Filter X values (Dólar CCL)', min_value=float(df['X_CCL'].min()), max_value=float(df['X_CCL'].max()), value=(float(df['X_CCL'].min()), float(df['X_CCL'].max())))
y_range_ccl = st.slider('Filter Y values (Dólar CCL)', min_value=float(df['Y_CCL'].min()), max_value=float(df['Y_CCL'].max()), value=(float(df['Y_CCL'].min()), float(df['Y_CCL'].max())))
filtered_df_ccl = df[(df['X_CCL'] >= x_range_ccl[0]) & (df['X_CCL'] <= x_range_ccl[1]) & (df['Y_CCL'] >= y_range_ccl[0]) & (df['Y_CCL'] <= y_range_ccl[1])]
fig_ccl = px.scatter(filtered_df_ccl, x='X_CCL', y='Y_CCL', hover_name='CEDEAR-ARS', title='Dólar CCL de CEDEARs')
st.plotly_chart(fig_ccl)

# Scatter plot 2: Dólar MEP de CEDEARs
st.subheader('Scatter Plot 2: Dólar MEP de CEDEARs')
x_range_mep = st.slider('Filter X values (Dólar MEP)', min_value=float(df['X_MEP'].min()), max_value=float(df['X_MEP'].max()), value=(float(df['X_MEP'].min()), float(df['X_MEP'].max())))
y_range_mep = st.slider('Filter Y values (Dólar MEP)', min_value=float(df['Y_MEP'].min()), max_value=float(df['Y_MEP'].max()), value=(float(df['Y_MEP'].min()), float(df['Y_MEP'].max())))
filtered_df_mep = df[(df['X_MEP'] >= x_range_mep[0]) & (df['X_MEP'] <= x_range_mep[1]) & (df['Y_MEP'] >= y_range_mep[0]) & (df['Y_MEP'] <= y_range_mep[1])]
fig_mep = px.scatter(filtered_df_mep, x='X_MEP', y='Y_MEP', hover_name='CEDEAR-ARS', title='Dólar MEP de CEDEARs')
st.plotly_chart(fig_mep)

# Scatter plot 3: CANJE CEDEARS
st.subheader('Scatter Plot 3: CANJE CEDEARS')
x_range_canje = st.slider('Filter X values (CANJE)', min_value=float(df['X_Canje'].min()), max_value=float(df['X_Canje'].max()), value=(float(df['X_Canje'].min()), float(df['X_Canje'].max())))
y_range_canje = st.slider('Filter Y values (CANJE)', min_value=float(df['Y_Canje'].min()), max_value=float(df['Y_Canje'].max()), value=(float(df['Y_Canje'].min()), float(df['Y_Canje'].max())))
filtered_df_canje = df[(df['X_Canje'] >= x_range_canje[0]) & (df['X_Canje'] <= x_range_canje[1]) & (df['Y_Canje'] >= y_range_canje[0]) & (df['Y_Canje'] <= y_range_canje[1])]
fig_canje = px.scatter(filtered_df_canje, x='X_Canje', y='Y_Canje', hover_name='CEDEARD', title='CANJE CEDEARS')
st.plotly_chart(fig_canje)
