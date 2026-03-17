import pandas as pd
from database.connection import engine

def fetch_all_symbols():
    df = pd.read_sql(
        "SELECT DISTINCT symbol FROM companies",
        engine
    )
    return df["symbol"].tolist()
