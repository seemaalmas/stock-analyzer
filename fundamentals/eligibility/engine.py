import pandas as pd
from database.connection import get_connection, engine

GRADE_RULES = {
    "STRONG": {
        "allowed": ["weekly", "monthly"],
        "blocked": ["intraday"],
        "reason": "Final grade STRONG"
    },
    "GOOD": {
        "allowed": ["weekly"],
        "blocked": ["monthly"],
        "reason": "Final grade GOOD"
    },
    "AVERAGE": {
        "allowed": ["intraday"],
        "blocked": ["weekly", "monthly"],
        "reason": "Final grade AVERAGE"
    },
    "WEAK": {
        "allowed": ["intraday"],
        "blocked": ["weekly", "monthly"],
        "reason": "Final grade WEAK"
    },
    "AVOID": {
        "allowed": [],
        "blocked": ["intraday", "weekly", "monthly"],
        "reason": "Final grade AVOID (risk override)"
    }
}

def apply_trade_eligibility(symbol):
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT final_grade
        FROM fundamental_grades_final
        WHERE symbol = %s
        ORDER BY calculated_at DESC
        LIMIT 1
        """,
        engine,
        params=(symbol,)
    )

    if df.empty:
        conn.close()
        return

    final_grade = df.iloc[0]["final_grade"]
    rules = GRADE_RULES.get(final_grade)

    cur = conn.cursor()
    cur.execute(
        """
        DELETE FROM trade_eligibility WHERE symbol = %s
        """,
        (symbol,)
    )

    cur.execute(
        """
        INSERT INTO trade_eligibility
        (symbol, allowed_trade_types, blocked_trade_types, reason)
        VALUES (%s, %s, %s, %s)
        """,
        (
            symbol,
            rules["allowed"],
            rules["blocked"],
            rules["reason"]
        )
    )

    conn.commit()
    cur.close()
    conn.close()
