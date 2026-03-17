import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import date

st.set_page_config(page_title="📊 Stock Trend by Date", layout="wide")
st.title("📈 Stock Trend Checker by Date")

# --- User Inputs ---
stock = st.text_input("Enter NSE stock symbol (e.g., GRSE.NS):", value="GRSE.NS").upper()
period = st.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y"])
trend_type = st.radio("Select Trend Type", ["Daily", "Weekly", "Monthly"])
selected_date = st.date_input("Select Date", value=date.today())

# --- Download & Clean Data ---
df = yf.download(stock, period=period, interval="1d", auto_adjust=False)

if df.empty:
    st.error("❌ No data found for the selected stock.")
    st.stop()

# Flatten multi-index if needed
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df.columns = [str(col).strip().title() for col in df.columns]

df = df.dropna().reset_index()
df["Date"] = pd.to_datetime(df["Date"])
df["Day"] = df["Date"].dt.day_name()
df["Week"] = df["Date"].dt.strftime("W%U-%Y")
df["Month"] = df["Date"].dt.strftime("%Y-%m")
df["Daily_Trend"] = np.where(df["Close"] > df["Open"], "Bullish", "Bearish")

# RSI Calculation (optional)
if len(df) > 14:
    df["RSI"] = ta.momentum.RSIIndicator(close=df["Close"], window=14).rsi()
    df["Volume_Avg"] = df["Volume"].rolling(window=14).mean()

# --- Logic by Trend Type ---
if trend_type == "Daily":
    st.subheader("📅 Daily Trend")
    match = df[df["Date"].dt.date == selected_date]
    if not match.empty:
        st.write(match[["Date", "Open", "Close", "Daily_Trend", "Volume", "RSI"]])
    else:
        st.warning("No data found for selected date.")

elif trend_type == "Weekly":
    st.subheader("📈 Weekly Trend")
    df["Week_Start"] = df["Date"] - pd.to_timedelta(df["Date"].dt.weekday, unit='d')
    df["Week_Label"] = df["Week_Start"].dt.strftime("%Y-%m-%d")
    weekly = df.groupby("Week_Label").agg(Open=("Open", "first"), Close=("Close", "last"))
    weekly["Weekly_Trend"] = np.where(weekly["Close"] > weekly["Open"], "Bullish", "Bearish")
    selected_week = selected_date - pd.to_timedelta(selected_date.weekday(), unit='d')
    week_label = selected_week.strftime("%Y-%m-%d")
    if week_label in weekly.index:
        st.write(weekly.loc[[week_label]])
    else:
        st.warning("No data for selected week.")

elif trend_type == "Monthly":
    st.subheader("📆 Monthly Trend")
    monthly = df.groupby("Month").agg(Open=("Open", "first"), Close=("Close", "last"))
    monthly["Monthly_Trend"] = np.where(monthly["Close"] > monthly["Open"], "Bullish", "Bearish")
    month_label = selected_date.strftime("%Y-%m")
    if month_label in monthly.index:
        st.write(monthly.loc[[month_label]])
    else:
        st.warning("No data for selected month.")
