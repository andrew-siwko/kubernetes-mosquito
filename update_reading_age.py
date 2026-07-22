# Connection info (PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD) comes from the
# environment - psycopg.connect() with no arguments reads the standard libpq
# env vars automatically.
from psycopg import connect

ALTER_STATEMENTS = (
    "ALTER TABLE recent_readings ADD COLUMN IF NOT EXISTS reading_age_minutes integer",
    "ALTER TABLE recent_readings ADD COLUMN IF NOT EXISTS local_time timestamp",
)

# The reading JSON's "time" field is a naive timestamp in UTC.
UPDATE_STATEMENT = """
    UPDATE recent_readings
    SET reading_age_minutes = floor(
            extract(epoch FROM (now() - (reading::jsonb ->> 'time')::timestamp)) / 60
        )::int,
        local_time = (reading::jsonb ->> 'time')::timestamp
            AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York'
"""

with connect() as connection:
    connection.autocommit = True
    with connection.cursor() as cursor:
        for statement in ALTER_STATEMENTS:
            cursor.execute(statement)
        cursor.execute(UPDATE_STATEMENT)
        print(f"updated {cursor.rowcount} rows", flush=True)
