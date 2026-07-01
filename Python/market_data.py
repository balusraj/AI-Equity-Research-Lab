import yfinance as yf
import pandas as pd

ticker = "INFY.NS"

stock = yf.Ticker(ticker)

info = stock.info

print("-" * 40)
print("AI Equity Research Lab")
print("-" * 40)

print(f"Company      : {info.get('longName')}")
print(f"Current Price: ₹{info.get('currentPrice')}")
print(f"Market Cap   : {info.get('marketCap')}")
print(f"P/E Ratio    : {info.get('trailingPE')}")
print(f"52W High     : ₹{info.get('fiftyTwoWeekHigh')}")
print(f"52W Low      : ₹{info.get('fiftyTwoWeekLow')}")
