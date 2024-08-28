import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# Load the CSV file
df = pd.read_csv('CEDEARcsv.csv')

# Fetch the latest data for each ticker from Yahoo Finance
def fetch_latest_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    if hist.empty:
        return None, None
    latest_data = hist['Close'].iloc[-1]
    volume = hist['Volume'].iloc[-1]
    return latest_data, volume

# Initialize empty dictionaries to store prices and volumes
prices = {}
volumes = {}

# Fetch the latest price and volume data for all tickers, excluding those with no data
for column in ["CEDEAR-ARS", "CEDEARD", "Subyacente"]:
    unique_tickers = df[column].unique()
    for ticker in unique_tickers:
        latest_price, latest_volume = fetch_latest_data(ticker)
        if latest_price is not None and latest_volume is not None:
            prices[ticker] = latest_price
            volumes[ticker] = latest_volume

# Ensure the DataFrame only includes rows with valid price data and volume > 1 for all required tickers
df = df[df['CEDEAR-ARS'].isin(prices.keys()) & df['CEDEARD'].isin(prices.keys()) & df['Subyacente'].isin(prices.keys())]

# Calculate the X and Y values for the scatter plots
df['X_CCL'] = df.apply(lambda row: (prices[row['CEDEAR-ARS']] * row['Ratio']) / prices[row['Subyacente']], axis=1)
df['Y_CCL'] = df.apply(lambda row: prices[row['CEDEAR-ARS']] * volumes[row['CEDEAR-ARS']], axis=1)

df['X_MEP'] = df.apply(lambda row: (prices[row['CEDEAR-ARS']] * row['Ratio']) / prices[row['CEDEARD']], axis=1)
df['Y_MEP'] = df.apply(lambda row: prices[row['CEDEARD']] * volumes[row['CEDEARD']], axis=1)

df['X_Canje'] = df.apply(lambda row: (prices[row['CEDEARD']] * row['Ratio']) / prices[row['Subyacente']], axis=1)
df['Y_Canje'] = df.apply(lambda row: prices[row['CEDEARD']] * volumes[row['CEDEARD']], axis=1)

# Exclude rows where volume is less than 1
df = df[(df['Y_CCL'] > 1) & (df['Y_MEP'] > 1) & (df['Y_Canje'] > 1)]

# Function to remove outliers using IQR method
def remove_outliers(df, x_column, y_column):
    Q1_x = df[x_column].quantile(0.25)
    Q3_x = df[x_column].quantile(0.75)
    IQR_x = Q3_x - Q1_x
    
    Q1_y = df[y_column].quantile(0.25)
    Q3_y = df[y_column].quantile(0.75)
    IQR_y = Q3_y - Q1_y
    
    lower_bound_x = Q1_x - 1.5 * IQR_x
    upper_bound_x = Q3_x + 1.5 * IQR_x
    
    lower_bound_y = Q1_y - 1.5 * IQR_y
    upper_bound_y = Q3_y + 1.5 * IQR_y
    
    filtered_df = df[(df[x_column] >= lower_bound_x) & (df[x_column] <= upper_bound_x) & 
                     (df[y_column] >= lower_bound_y) & (df[y_column] <= upper_bound_y)]
    return filtered_df

# Remove outliers for each plot
df_ccl = remove_outliers(df, 'X_CCL', 'Y_CCL')
df_mep = remove_outliers(df, 'X_MEP', 'Y_MEP')
df_canje = remove_outliers(df, 'X_Canje', 'Y_Canje')

# Create interactive scatter plots
st.title('CEDEAR Analysis')

# Scatter plot 1: Dólar CCL de CEDEARs
st.subheader('Scatter Plot 1: Dólar CCL de CEDEARs')
x_range_ccl = st.slider('Filter X values (Dólar CCL)', min_value=float(df_ccl['X_CCL'].min()), max_value=float(df_ccl['X_CCL'].max()), value=(float(df_ccl['X_CCL'].min()), float(df_ccl['X_CCL'].max())))
y_range_ccl = st.slider('Filter Y values (Dólar CCL)', min_value=float(df_ccl['Y_CCL'].min()), max_value=float(df_ccl['Y_CCL'].max()), value=(float(df_ccl['Y_CCL'].min()), float(df_ccl['Y_CCL'].max())))
filtered_df_ccl = df_ccl[(df_ccl['X_CCL'] >= x_range_ccl[0]) & (df_ccl['X_CCL'] <= x_range_ccl[1]) & (df_ccl['Y_CCL'] >= y_range_ccl[0]) & (df_ccl['Y_CCL'] <= y_range_ccl[1])]
fig_ccl = px.scatter(filtered_df_ccl, x='X_CCL', y='Y_CCL', hover_name='CEDEAR-ARS', title='Dólar CCL de CEDEARs')
st.plotly_chart(fig_ccl)

# Scatter plot 2: Dólar MEP de CEDEARs
st.subheader('Scatter Plot 2: Dólar MEP de CEDEARs')
x_range_mep = st.slider('Filter X values (Dólar MEP)', min_value=float(df_mep['X_MEP'].min()), max_value=float(df_mep['X_MEP'].max()), value=(float(df_mep['X_MEP'].min()), float(df_mep['X_MEP'].max())))
y_range_mep = st.slider('Filter Y values (Dólar MEP)', min_value=float(df_mep['Y_MEP'].min()), max_value=float(df_mep['Y_MEP'].max()), value=(float(df_mep['Y_MEP'].min()), float(df_mep['Y_MEP'].max())))
filtered_df_mep = df_mep[(df_mep['X_MEP'] >= x_range_mep[0]) & (df_mep['X_MEP'] <= x_range_mep[1]) & (df_mep['Y_MEP'] >= y_range_mep[0]) & (df_mep['Y_MEP'] <= y_range_mep[1])]
fig_mep = px.scatter(filtered_df_mep, x='X_MEP', y='Y_MEP', hover_name='CEDEAR-ARS', title='Dólar MEP de CEDEARs')
st.plotly_chart(fig_mep)

# Scatter plot 3: CANJE CEDEARS
st.subheader('Scatter Plot 3: CANJE CEDEARS')
x_range_canje = st.slider('Filter X values (CANJE)', min_value=float(df_canje['X_Canje'].min()), max_value=float(df_canje['X_Canje'].max()), value=(float(df_canje['X_Canje'].min()), float(df_canje['X_Canje'].max())))
y_range_canje = st.slider('Filter Y values (CANJE)', min_value=float(df_canje['Y_Canje'].min()), max_value=float(df_canje['Y_Canje'].max()), value=(float(df_canje['Y_Canje'].min()), float(df_canje['Y_Canje'].max())))
filtered_df_canje = df_canje[(df_canje['X_Canje'] >= x_range_canje[0]) & (df_canje['X_Canje'] <= x_range_canje[1]) & (df_canje['Y_Canje'] >= y_range_canje[0]) & (df_canje['Y_Canje'] <= y_range_canje[1])]
fig_canje = px.scatter(filtered_df_canje, x='X_Canje', y='Y_Canje', hover_name='CEDEARD', title='CANJE CEDEARS')
st.plotly_chart(fig_canje)
