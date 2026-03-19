import os, sys
import psycopg
SQL = """
select
  n.nspname as schema,
  c.relname as table,
  a.attname as column,
  pg_catalog.format_type(a.atttypid, a.atttypmod) as type,
  a.attnotnull as not_null
from pg_catalog.pg_attribute a
join pg_catalog.pg_class c on a.attrelid = c.oid
join pg_catalog.pg_namespace n on c.relnamespace = n.oid
where c.relkind = 'r'
  and n.nspname not in ('pg_catalog','information_schema')
  and a.attnum > 0
  and not a.attisdropped
order by 1,2, a.attnum;
"""
IDX = """
select
  schemaname, tablename, indexname, indexdef
from pg_indexes
where schemaname not in ('pg_catalog','information_schema')
order by 1,2,3;
"""
def main():
    dsn = os.getenv("DATABASE_URL","").strip()
    if not dsn:
        print("ERROR: DATABASE_URL is required")
        sys.exit(2)
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(SQL)
            rows = cur.fetchall()
            cur.execute(IDX)
            idx = cur.fetchall()
    print("# Database Schema Snapshot")
    print()
    print("## Tables & columns")
    cur_table = None
    for schema, table, col, typ, not_null in rows:
        key = (schema, table)
        if key != cur_table:
            cur_table = key
            print(f"\n### {schema}.{table}")
        nn = " NOT NULL" if not_null else ""
        print(f"- {col}: {typ}{nn}")
    print("\n## Indexes")
    for schemaname, tablename, indexname, indexdef in idx:
        print(f"- {schemaname}.{tablename} :: {indexname}\n  {indexdef}")
if __name__ == "__main__":
    main()
