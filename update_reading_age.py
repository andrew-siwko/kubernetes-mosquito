# Connection info (PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD) comes from the
# environment - psycopg.connect() with no arguments reads the standard libpq
# env vars automatically.
from psycopg import connect

ALTER_STATEMENT = (
    "ALTER TABLE recent_readings ADD COLUMN IF NOT EXISTS reading_age_minutes integer"
)

UPDATE_STATEMENT = """
    UPDATE recent_readings
    SET reading_age_minutes = floor(
        extract(epoch FROM (now() - (reading::jsonb ->> 'time')::timestamp)) / 60
    )::int
"""

with connect() as connection:
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute(ALTER_STATEMENT)
        cursor.execute(UPDATE_STATEMENT)
        print(f"updated {cursor.rowcount} rows", flush=True)
