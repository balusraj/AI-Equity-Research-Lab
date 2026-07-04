"""
Project 002
Financial Statement Downloader (Normalized folders + merge duplicates)

Author: Balasubrahmanyam Behara
Project: AI Equity Research Lab
"""

import re
import shutil
from pathlib import Path
import pandas as pd
import yfinance as yf


def get_nse_ticker(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        symbol += ".NS"
    return symbol


def safe_fetch(getter, label: str):
    try:
        return getter()
    except Exception as e:
        print(f"  Warning: could not fetch {label} ({e})")
        return None


def normalize_company_name(name: str) -> str:
    if not name:
        return ""
    # normalize separators so suffix matching works (handle underscores/dashes)
    tmp = name.replace('_', ' ').replace('-', ' ')
    # remove common suffixes
    s = re.sub(r"\b(Pvt\.?\s*Ltd\.?|Private\s+Limited|Limited|Ltd\.?|Incorporated|Inc\.?|PLC|Corporation|Corp\.?|LLP)\b",
               "", tmp, flags=re.IGNORECASE)
    s = re.sub(r"[^A-Za-z0-9\s]", " ", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return s or name


def sanitize_folder_name(name: str, fallback: str) -> str:
    safe = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in name).strip()
    safe = safe.replace(" ", "_")
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe or fallback


def save_dataframe(df: pd.DataFrame, path: Path) -> bool:
    if df is None or df.empty:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="data")
        return True
    except Exception as e:
        print(f"  Error saving {path.name}: {e}")
        return False


def merge_existing_company_dirs(output_dir: Path, target_name: str) -> Path:
    """Find any existing directories under output_dir whose normalized name matches target_name.
    Move their contents into the normalized target directory and remove empty duplicates.
    Returns the path to the normalized target directory."""
    target_dir = output_dir / target_name
    if not output_dir.exists():
        return target_dir

    for child in list(output_dir.iterdir()):
        if not child.is_dir():
            continue
        child_norm = normalize_company_name(child.name)
        target_norm = normalize_company_name(target_name)
        if child_norm == target_norm and child.name != target_name:
            # ensure target exists
            target_dir.mkdir(parents=True, exist_ok=True)
            for item in child.iterdir():
                dest = target_dir / item.name
                # If both are directories (e.g. "Annual Reports"), merge their contents
                if item.is_dir() and dest.exists() and dest.is_dir():
                    for sub in item.iterdir():
                        sub_dest = dest / sub.name
                        if sub_dest.exists():
                            stem = sub_dest.stem
                            suffix = sub_dest.suffix
                            n = 1
                            while True:
                                new_name = f"{stem}_dup{n}{suffix}"
                                new_sub_dest = dest / new_name
                                if not new_sub_dest.exists():
                                    sub_dest = new_sub_dest
                                    break
                                n += 1
                        try:
                            shutil.move(str(sub), str(sub_dest))
                        except Exception:
                            if sub.is_dir():
                                shutil.copytree(str(sub), str(sub_dest))
                                shutil.rmtree(str(sub))
                            else:
                                shutil.copy2(str(sub), str(sub_dest))
                                sub.unlink()
                    # remove the now-empty subdirectory
                    try:
                        item.rmdir()
                    except Exception:
                        pass
                    continue

                if dest.exists():
                    # find a non-conflicting name by appending a counter
                    stem = dest.stem
                    suffix = dest.suffix
                    n = 1
                    while True:
                        new_name = f"{stem}_dup{n}{suffix}"
                        new_dest = target_dir / new_name
                        if not new_dest.exists():
                            dest = new_dest
                            break
                        n += 1
                try:
                    shutil.move(str(item), str(dest))
                except Exception:
                    # fallback: copy then remove
                    if item.is_dir():
                        shutil.copytree(str(item), str(dest))
                        shutil.rmtree(str(item))
                    else:
                        shutil.copy2(str(item), str(dest))
                        item.unlink()
            # try remove old directory
            try:
                child.rmdir()
            except Exception:
                pass
    return target_dir


def download_financial_statements(symbol: str, output_dir: Path) -> None:
    ticker_symbol = get_nse_ticker(symbol)
    stock = yf.Ticker(ticker_symbol)

    # fetch company info
    try:
        info = stock.info or {}
    except Exception:
        info = {}

    ticker_short = ticker_symbol.replace('.NS', '').replace('.BO', '')
    company_full = info.get('longName') or ticker_short

    # normalized folder name (strip suffixes) then sanitize
    normalized = normalize_company_name(company_full)
    safe_company = sanitize_folder_name(normalized, fallback=ticker_short)

    # merge any existing folders that normalize to the same name
    base_dir = merge_existing_company_dirs(Path('financial_statements'), safe_company)
    annual_dir = base_dir / 'Annual Reports'
    quarterly_dir = base_dir / 'Quarterly Reports'

    def consolidate_subdirs(parent: Path, subname: str):
        main = parent / subname
        if not parent.exists():
            return
        for child in list(parent.iterdir()):
            if not child.is_dir():
                continue
            if child.name == subname:
                continue
            # match variants that start with the subname (e.g., 'Annual Reports_dup1')
            if child.name.startswith(subname):
                main.mkdir(parents=True, exist_ok=True)
                for item in child.iterdir():
                    dest = main / item.name
                    if dest.exists():
                        stem = dest.stem
                        suffix = dest.suffix
                        n = 1
                        while True:
                            new_name = f"{stem}_dup{n}{suffix}"
                            new_dest = main / new_name
                            if not new_dest.exists():
                                dest = new_dest
                                break
                            n += 1
                    try:
                        shutil.move(str(item), str(dest))
                    except Exception:
                        if item.is_dir():
                            shutil.copytree(str(item), str(dest))
                            shutil.rmtree(str(item))
                        else:
                            shutil.copy2(str(item), str(dest))
                            item.unlink()
                try:
                    child.rmdir()
                except Exception:
                    pass

    # cleanup any previously-created duplicate subfolders
    consolidate_subdirs(base_dir, 'Annual Reports')
    consolidate_subdirs(base_dir, 'Quarterly Reports')

    print(f"Downloading financial statements for {ticker_symbol} -> {company_full}")

    statements_annual = {
        'Income Statement': safe_fetch(lambda: stock.financials, 'Income Statement'),
        'Balance Sheet': safe_fetch(lambda: stock.balance_sheet, 'Balance Sheet'),
        'Cash Flow Statement': safe_fetch(lambda: stock.cashflow, 'Cash Flow Statement'),
    }

    statements_quarterly = {
        'Quarterly Income Statement': safe_fetch(lambda: stock.quarterly_financials, 'Quarterly Income Statement'),
        'Quarterly Balance Sheet': safe_fetch(lambda: stock.quarterly_balance_sheet, 'Quarterly Balance Sheet'),
        'Quarterly Cash Flow Statement': safe_fetch(lambda: stock.quarterly_cashflow, 'Quarterly Cash Flow Statement'),
    }

    saved_any = False

    for pretty_name, df in statements_annual.items():
        filename = f"{ticker_short}_{pretty_name.replace(' ', '_')}.xlsx"
        path = annual_dir / filename
        if save_dataframe(df, path):
            print(f"Saved {pretty_name} to {path}")
            saved_any = True
        else:
            print(f"No data available for {pretty_name}")

    for pretty_name, df in statements_quarterly.items():
        filename = f"{ticker_short}_{pretty_name.replace(' ', '_')}.xlsx"
        path = quarterly_dir / filename
        if save_dataframe(df, path):
            print(f"Saved {pretty_name} to {path}")
            saved_any = True
        else:
            print(f"No data available for {pretty_name}")

    if not saved_any:
        print('No financial statement data could be downloaded.')


def main() -> None:
    symbol = input('Enter NSE symbol (e.g. INFY): ').strip()
    if not symbol:
        print('Ticker symbol cannot be empty.')
        return
    output_dir = Path('financial_statements')
    download_financial_statements(symbol, output_dir)


if __name__ == '__main__':
    main()
