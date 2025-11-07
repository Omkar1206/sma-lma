#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# -------------------------------
# MOVING AVERAGE CROSSOVER APP
# -------------------------------
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stock Crossover App", layout="wide")

st.title("📈 Moving Average Crossover Strategy")

# ---- Sidebar Inputs ----
st.sidebar.header("Configure Parameters")

stock_name = st.sidebar.text_input("Enter Stock Symbol", "LT.NS")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-10-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2025-10-01"))

short_window = st.sidebar.number_input("Short Moving Average (SMA)", min_value=3, max_value=50, value=5)
long_window = st.sidebar.number_input("Long Moving Average (LMA)", min_value=10, max_value=100, value=35)

# ---- Fetch Data ----
@st.cache_data
def load_data(stock, start, end):
    df = yf.download(stock, start=start, end=end)
    return df

df = load_data(stock_name, start_date, end_date)

if df.empty:
    st.warning("No data found. Please check the stock symbol or date range.")
    st.stop()

# ---- Calculate SMA and Signals ----
df[f"SMA_{short_window}"] = df["Close"].rolling(window=short_window).mean()
df[f"LMA_{long_window}"] = df["Close"].rolling(window=long_window).mean()

df["Signal"] = 0
df.loc[df.index[max(short_window, long_window)-1]:, "Signal"] = np.where(
    df[f"SMA_{short_window}"][max(short_window, long_window)-1:] > 
    df[f"LMA_{long_window}"][max(short_window, long_window)-1:], 1, 0
)
df["Position"] = df["Signal"].diff()

# ---- Plot ----
fig, ax = plt.subplots(figsize=(14,6))
ax.plot(df["Close"], label="Close Price", alpha=0.8)
ax.plot(df[f"SMA_{short_window}"], label=f"SMA {short_window}", linewidth=1.5)
ax.plot(df[f"LMA_{long_window}"], label=f"LMA {long_window}", linewidth=1.5)
ax.plot(df[df["Position"] == 1].index, df[f"SMA_{short_window}"][df["Position"] == 1], 
        '^', markersize=12, color='g', label='BUY Signal')
ax.plot(df[df["Position"] == -1].index, df[f"SMA_{short_window}"][df["Position"] == -1], 
        'v', markersize=12, color='r', label='SELL Signal')
ax.set_title(f"Moving Average Crossover for {stock_name}")
ax.legend()
ax.grid()

st.pyplot(fig)

# ---- Display Data ----
st.subheader("Stock Data with Signals")
st.dataframe(df.tail(20))

# ---- Optional Download ----
csv = df.to_csv().encode("utf-8")
st.download_button("Download Data as CSV", csv, f"{stock_name}_signals.csv", "text/csv")

