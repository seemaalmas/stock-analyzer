import os
import zipfile
import requests
import pandas as pd
from sqlalchemy import text
from database.engine import engine
from datetime import date, timedelta, datetime
# ---------------- CONFIG ---------------- #

BHAVCOPY_BASE_URL = "https://archives.nseindia.com/content/historical/EQUITIES"
RAW_DIR = "data/raw/nse_bhavcopy"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

os.makedirs(RAW_DIR, exist_ok=True)

# --------------------------------------- #


def get_bhavcopy_url(trade_date: datetime):
    dd = trade_date.strftime("%d")
    mon = trade_date.strftime("%b").upper()
    yyyy = trade_date.strftime("%Y")
    filename = f"cm{dd}{mon}{yyyy}bhav.csv.zip"
    return f"{BHAVCOPY_BASE_URL}/{yyyy}/{mon}/{filename}", filename


def download_bhavcopy(trade_date: datetime):
    url, filename = get_bhavcopy_url(trade_date)
    zip_path = os.path.join(RAW_DIR, filename)

    if os.path.exists(zip_path):
        print(f"📁 Already downloaded: {filename}")
        return zip_path

    print(f"⬇️ Downloading Bhavcopy: {filename}")
    resp = requests.get(url, headers=HEADERS, timeout=20)

    if resp.status_code != 200:
        raise RuntimeError(f"❌ Bhavcopy not available for {trade_date.date()}")

    with open(zip_path, "wb") as f:
        f.write(resp.content)

    return zip_path


def extract_csv(zip_path):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(RAW_DIR)
        for name in zip_ref.namelist():
            if name.endswith(".csv"):
                return os.path.join(RAW_DIR, name)
    raise RuntimeError("❌ CSV not found inside ZIP")


def load_symbol_universe():
    df = pd.read_sql(
        """
        SELECT symbol
        FROM symbols_master
        WHERE is_active = TRUE
        AND index_name != 'INDEX'
        """,
        engine
    )
    return set(df["symbol"].tolist())


def parse_and_insert(csv_path, trade_date: datetime):
    print("📄 Parsing Bhavcopy CSV")

    df = pd.read_csv(csv_path)

    required_cols = {
        "SYMBOL", "SERIES", "OPEN", "HIGH", "LOW", "CLOSE",
        "TOTTRDQTY", "DELIV_QTY", "DELIV_PER", "TIMESTAMP"
    }

    if not required_cols.issubset(df.columns):
        raise RuntimeError("❌ Bhavcopy format mismatch")

    df = df[df["SERIES"] == "EQ"]

    universe = load_symbol_universe()
    df = df[df["SYMBOL"].isin(universe)]

    if df.empty:
        print("⚠️ No matching symbols found in Bhavcopy")
        return

    df["trade_date"] = pd.to_datetime(df["TIMESTAMP"], format="%d-%b-%Y").dt.date
    df["source"] = "NSE"

    df = df.rename(columns={
        "SYMBOL": "symbol",
        "OPEN": "open",
        "HIGH": "high",
        "LOW": "low",
        "CLOSE": "close",
        "TOTTRDQTY": "volume",
        "DELIV_QTY": "delivery_qty",
        "DELIV_PER": "delivery_pct"
    })

    df = df[
        [
            "symbol", "trade_date", "open", "high", "low", "close",
            "volume", "delivery_qty", "delivery_pct", "source"
        ]
    ]

    print(f"🧮 Inserting {len(df)} rows into price_daily")

    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(
                text("""
                    INSERT INTO price_daily
                    (symbol, trade_date, open, high, low, close,
                     volume, delivery_qty, delivery_pct, source)
                    VALUES
                    (:symbol, :trade_date, :open, :high, :low, :close,
                     :volume, :delivery_qty, :delivery_pct, :source)
                    ON CONFLICT (symbol, trade_date) DO NOTHING
                """),
                row.to_dict()
            )

    print("✅ Bhavcopy ingestion complete")

def get_latest_possible_trading_date():
    today = date.today()

    # NSE publishes bhavcopy after market close
    if datetime.now().hour < 19:
        today = today - timedelta(days=1)

    # Skip weekends
    while today.weekday() >= 5:
        today -= timedelta(days=1)

    return today


def run_bhavcopy_ingestion(trade_date: str = None):
    if trade_date:
        trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()

        if trade_date > date.today():
            raise ValueError("❌ Cannot download Bhavcopy for future date")

    else:
        trade_date = get_latest_possible_trading_date()

    zip_path = download_bhavcopy(datetime.combine(trade_date, datetime.min.time()))
    csv_path = extract_csv(zip_path)
    parse_and_insert(csv_path, trade_date)

from datetime import date, timedelta, datetime

def find_latest_available_bhavcopy(max_lookback=10):
    d = date.today() - timedelta(days=1)

    for _ in range(max_lookback):
        if d.weekday() >= 5:  # Skip weekends
            d -= timedelta(days=1)
            continue

        try:
            zip_path = download_bhavcopy(datetime.combine(d, datetime.min.time()))
            return d, zip_path
        except RuntimeError:
            print(f"⚠️ Bhavcopy not found for {d}, trying previous day")
            d -= timedelta(days=1)

    raise RuntimeError("❌ No Bhavcopy found in lookback window")


def run_bhavcopy_ingestion(trade_date: str = None):
    if trade_date:
        trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        zip_path = download_bhavcopy(datetime.combine(trade_date, datetime.min.time()))
    else:
        trade_date, zip_path = find_latest_available_bhavcopy()

    csv_path = extract_csv(zip_path)
    parse_and_insert(csv_path, trade_date)


if __name__ == "__main__":
    run_bhavcopy_ingestion()
