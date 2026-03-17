import pandas as pd
from database.connection import get_connection, engine

def fetch_annual_financials(symbol: str) -> pd.DataFrame:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT current_database(), current_user, current_schema();")
    print(cursor.fetchone())

    query = """
        SELECT fiscal_year, revenue, operating_profit,
               net_profit, equity, debt
        FROM financials_annual_raw
        WHERE symbol = %s
        ORDER BY fiscal_year;
    """

    df = pd.read_sql(query, engine, params=(symbol,))
    cursor.close()
    conn.close()
    return df

def save_fundamental_grade(
    symbol: str,
    score: int,
    grade: str,
    red_flags: list,
    trade_types: list
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO fundamental_grades
        (symbol, grade, score, red_flags, allowed_trade_types)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (symbol, grade, score, red_flags, trade_types)
    )

    conn.commit()
    cur.close()
    conn.close()
