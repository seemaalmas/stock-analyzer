import requests
import pandas as pd
import zipfile
import io

def download_bhavcopy(trade_date):
    date_str = trade_date.strftime("%d%b%Y").upper()
    year = trade_date.strftime("%Y")
    month = trade_date.strftime("%b").upper()

    url = (
        f"https://archives.nseindia.com/content/historical/"
        f"EQUITIES/{year}/{month}/cm{date_str}bhav.csv.zip"
    )

    print("Trying URL:", url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/zip,application/octet-stream",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }

    r = requests.get(url, headers=headers, timeout=30)

    if r.status_code != 200:
        raise Exception("Bhavcopy not available for date")