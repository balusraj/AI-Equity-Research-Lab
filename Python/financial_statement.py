"""
Project 002
Financial Statement Downloader

Author: Balasubrahmanyam Behara
Project: AI Equity Research Lab
"""

import os
from pathlib import Path
import pandas as pd
import yfinance as yf


def get_nse_ticker(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol.endswith(".NS"):
        symbol += ".NS"
    return symbol


def save_dataframe(df: pd.DataFrame, path: Path) -> bool:
    if df is None or df.empty:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        try:
            df.to_excel(writer, sheet_name="data")
        except Exception:
            pd.DataFrame(df).to_excel(writer, sheet_name="data")
    return True


def download_financial_statements(symbol: str, output_dir: Path) -> None:
    ticker_symbol = get_nse_ticker(symbol)
    stock = yf.Ticker(ticker_symbol)
    # get company full name for folder naming
    try:
        info = stock.info or {}
    except Exception:
        info = {}

    company_full = info.get("longName") or ticker_symbol.replace('.NS', '')
    # sanitize folder name
    safe_company = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in company_full).strip()
    safe_company = safe_company.replace(' ', '_')

    base_dir = output_dir / safe_company
    annual_dir = base_dir / "Annual Reports"
    quarterly_dir = base_dir / "Quarterly Reports"

    statements_annual = {
        "Income Statement": stock.financials,
        "Balance Sheet": stock.balance_sheet,
        "Cash Flow Statement": stock.cashflow,
    }

    statements_quarterly = {
        "Quarterly Income Statement": stock.quarterly_financials,
        "Quarterly Balance Sheet": stock.quarterly_balance_sheet,
        "Quarterly Cash Flow Statement": stock.quarterly_cashflow,
    }

    print(f"Downloading financial statements for {ticker_symbol} -> {company_full}")
    saved_any = False

    for pretty_name, df in statements_annual.items():
        filename = f"{ticker_symbol.replace('.NS','')}_{pretty_name.replace(' ', '_')}.xlsx"
        path = annual_dir / filename
        if save_dataframe(df, path):
            print(f"Saved {pretty_name} to {path}")
            saved_any = True
        else:
            print(f"No data available for {pretty_name}")

    for pretty_name, df in statements_quarterly.items():
        filename = f"{ticker_symbol.replace('.NS','')}_{pretty_name.replace(' ', '_')}.xlsx"
        path = quarterly_dir / filename
        if save_dataframe(df, path):
            print(f"Saved {pretty_name} to {path}")
            saved_any = True
        else:
            print(f"No data available for {pretty_name}")

    if not saved_any:
        print("No financial statement data could be downloaded.")


def main() -> None:
    symbol = input("Enter NSE symbol (e.g. INFY): ").strip()
    if not symbol:
        print("Ticker symbol cannot be empty.")
        return

    output_dir = Path("financial_statements")
    download_financial_statements(symbol, output_dir)


if __name__ == "__main__":
    main()
