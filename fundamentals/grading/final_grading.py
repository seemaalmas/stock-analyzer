import pandas as pd
from database.connection import engine, get_connection

GRADE_ORDER = ["STRONG", "GOOD", "AVERAGE", "WEAK", "AVOID"]

def downgrade_grade(grade, steps=1):
    idx = GRADE_ORDER.index(grade)
    return GRADE_ORDER[min(idx + steps, len(GRADE_ORDER) - 1)]

def apply_risk_downgrades(symbol):
    conn = get_connection()

    base = pd.read_sql(
        """
        SELECT grade
        FROM fundamental_grades
        WHERE symbol = %s
        ORDER BY calculated_at DESC
        LIMIT 1
        """,
        engine,
        params=(symbol,)
    )

    if base.empty:
        conn.close()
        return

    base_grade = base.iloc[0]["grade"]
    final_grade = base_grade

    flags = pd.read_sql(
        """
        SELECT flag, severity
        FROM fundamental_risk_flags
        WHERE symbol = %s
        """,
        engine,
        params=(symbol,)
    )

    applied_flags = flags["flag"].tolist()

    # HARD BLOCK
    if "HIGH" in flags["severity"].values:
        final_grade = "AVOID"
    else:
        # Downgrade per MEDIUM flag
        medium_count = (flags["severity"] == "MEDIUM").sum()
        for _ in range(medium_count):
            final_grade = downgrade_grade(final_grade, 1)

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO fundamental_grades_final
        (symbol, base_grade, final_grade, applied_flags)
        VALUES (%s, %s, %s, %s)
        """,
        (symbol, base_grade, final_grade, applied_flags)
    )

    conn.commit()
    cur.close()
    conn.close()
