import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "Data" / "Input" / "company_universe.xlsx"

def get_company_list():
    df = pd.read_excel(
        INPUT_FILE,
        sheet_name="50 Companies",
        usecols="A:B"
    )
    return df[['Ticker']]