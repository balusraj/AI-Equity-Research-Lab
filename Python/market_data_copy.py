"""
Project 001
Market Data Downloader Copy

Author: Balasubrahmanyam Behara
Project: AI Equity Research Lab
"""
import yfinance as yf
import pandas as pd
import company_list as cl

""""
ticker = input("Enter NSE Symbol : ").upper()
"""
def format_market_cap(value):
    if value >= 1_00_00_00_00_000:      # 1 Lakh Crore
        return f"₹{value/1_00_00_00_00_000:.2f} Lakh Cr"
    elif value >= 1_00_00_000:
        return f"₹{value/1_00_00_000:.2f} Cr"
    else:
        return f"₹{value:,}"

companies = cl.get_company_list()

for index, row in companies.iterrows():
    ticker = row["Ticker"].strip()  # Remove any leading/trailing whitespace
    ticker += ".NS"
    print(f"{i}. {ticker}")

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or info.get("currentPrice")is None:
            print("X invalid ticker or data unavailable.")
        else:
            print("-" * 40)
            print("AI Equity Research Lab")
            print("-" * 40)
            print(f"Company      : {info.get('longName')}")
            print(f"Sector       : {info.get('sector')}")
            print(f"Industry     : {info.get('industry')}")
            print(f"Employees    : {info.get('fullTimeEmployees'):,}")
            print(f"Website      : {info.get('website')}")
            print(f"Current Price: ₹{info.get('currentPrice')}")
            print(f"Market Cap   : {format_market_cap(info.get('marketCap'))}")
            print(f"P/E Ratio    : {info.get('trailingPE'):.2f}")
            print(f"52W High     : ₹{info.get('fiftyTwoWeekHigh'):.2f}")
            print(f"52W Low      : ₹{info.get('fiftyTwoWeekLow'):.2f}")

    except Exception as e:
        print(f"Error fetching data: {e}")