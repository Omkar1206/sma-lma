# -------------------------------------------------------------
# MOVING AVERAGE CROSSOVER STREAMLIT APP (FINAL STABLE VERSION)
# -------------------------------------------------------------

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Streamlit page configuration
st.set_page_config(page_title="Stock Crossover App", layout="wide")

st.title("📈 Moving Average Crossover Strategy")
st.write("Analyze buy/sell crossover signals based on short and long moving averages using Yahoo Finance data.")

# ----------------------------
# Sidebar: User Inputs
# ----------------------------
st.sidebar.header("Configure Parameters")

stock_name = st.sidebar.text_input("Enter Stock Symbol (e.g., LT.NS, RELIANCE.NS, AAPL)", "LT.NS")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-10-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2025-10-01"))

short_window = st.sidebar.number_input("Short Moving Average (SMA)", min_value=3, max_value=50, value=5)
long_window = st.sidebar.number_input("Long Moving Average (LMA)", min_value=10, max_value=100, value=35)

# ----------------------------
# Data Loading with Error Handling
# ----------------------------
@st.cache_data
def load_data(stock, start, end):
    try:
        ticker = yf.Ticker(stock)
        df = ticker.history(start=start, end=end)
        if df.empty:
            st.warning("No data found. Please verify the stock symbol or date range.")
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

df = load_data(stock_name, start_date, end_date)

if df.empty:
    st.stop()

# ----------------------------
# Strategy Computation
# ----------------------------
df[f"SMA_{short_window}"] = df["Close"].rolling(window=short_window).mean()
df[f"LMA_{long_window}"] = df["Close"].rolling(window=long_window).mean()

df["Signal"] = 0
df.loc[df.index[max(short_window, long_window)-1]:, "Signal"] = np.where(
    df[f"SMA_{short_window}"][max(short_window, long_window)-1:] > 
    df[f"LMA_{long_window}"][max(short_window, long_window)-1:], 1, 0
)
df["Position"] = df["Signal"].diff()

# ----------------------------
# Plot Section
# ----------------------------
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df.index, df["Close"], label="Close Price", alpha=0.8)
ax.plot(df.index, df[f"SMA_{short_window}"], label=f"SMA {short_window}", linewidth=1.5)
ax.plot(df.index, df[f"LMA_{long_window}"], label=f"LMA {long_window}", linewidth=1.5)

# Plot buy/sell signals
ax.plot(df[df["Position"] == 1].index,
        df[f"SMA_{short_window}"][df["Position"] == 1],
        '^', markersize=12, color='g', label='BUY Signal')

ax.plot(df[df["Position"] == -1].index,
        df[f"SMA_{short_window}"][df["Position"] == -1],
        'v', markersize=12, color='r', label='SELL Signal')

ax.set_title(f"Moving Average Crossover Strategy for {stock_name}")
ax.set_xlabel("Date")
ax.set_ylabel("Price")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# ----------------------------
# Data Table & Download
# ----------------------------
st.subheader("Stock Data with SMA, LMA, and Signals")
st.dataframe(df.tail(20))

csv = df.to_csv().encode("utf-8")
st.download_button("📥 Download Data as CSV", csv, f"{stock_name}_signals.csv", "text/csv")

# ----------------------------
# Footer
# ----------------------------
st.caption("Data Source: Yahoo Finance | Built with Streamlit & yfinance")
