import os
import pandas as pd
import oracledb
from dotenv import load_dotenv
import os
load_dotenv()


# --- config (use env vars in practice) ---
USER = os.getenv("ORACLE_USER")
PWD  = os.getenv("ORACLE_PASSWORD")
HOST = os.getenv("ORACLE_HOST")
PORT = os.getenv("ORACLE_PORT")
SERVICE = os.getenv("ORACLE_SERVICE")

def get_data():
  # build DSN and connect (Thin mode is default; do NOT call init_oracle_client)
  # dsn = oracledb.makedsn(HOST, PORT, service_name=SERVICE)
  with oracledb.connect(user=USER, password=PWD, host=HOST, service_name=SERVICE, port=PORT) as conn:
      # performance knobs for big reads
      conn.prefetchrows = 10000
      with conn.cursor() as cur:
          cur.arraysize = 10000

      # parameterized query -> DataFrame
      sql = """
      WITH params AS (
        SELECT
          TRUNC(SYSDATE)            AS today,
          TRUNC(SYSDATE) - 6        AS start_date,   -- inclusive
          TRUNC(SYSDATE) + 1        AS end_date_excl -- exclusive
        FROM dual
      ),
      base_data AS (
        SELECT
          CASE
            WHEN MAIN_BILLER_ID IN (14, 175) THEN 14
            WHEN MAIN_BILLER_ID IN (13, 160) THEN 13
            ELSE MAIN_BILLER_ID
          END AS GROUPED_BILLER_ID,
          SERVICE_ID,
          TOTAL_AMOUNT,
          CREATED_AT
        FROM NEWREP.TRANSACTIONS_NBP_TEMP t
        JOIN params p
          ON t.CREATED_AT >= p.start_date
        AND t.CREATED_AT <  p.end_date_excl
        WHERE t.MAIN_BILLER_ID IN (13, 14, 15, 16, 175, 160)
          AND t.SERVICE_ID   NOT IN (235, 236, 1783, 1784, 1434, 1435)
      ),
      agg AS (
        SELECT
          GROUPED_BILLER_ID AS MAIN_BILLER_ID,
          SERVICE_ID,
          SUM(TOTAL_AMOUNT) AS TOTAL_AMOUNT,
          COUNT(*)          AS TRANSACTION_COUNT
        FROM base_data
        GROUP BY GROUPED_BILLER_ID, SERVICE_ID
      )
      SELECT
        p.start_date                      AS WINDOW_START,     -- 7-day window start
        p.today                           AS WINDOW_END,       -- inclusive end (today)
        a.MAIN_BILLER_ID,
        a.SERVICE_ID,
        EXTRACT(YEAR  FROM p.start_date)  AS TXN_YEAR,
        EXTRACT(MONTH FROM p.start_date)  AS TXN_MONTH,
        TO_CHAR(p.start_date, 'IW')       AS WEEK_NUMBER,
        a.TOTAL_AMOUNT,
        a.TRANSACTION_COUNT
      FROM agg a
      CROSS JOIN params p
      ORDER BY a.MAIN_BILLER_ID, a.SERVICE_ID;
      """
  df = pd.read_sql_query(sql, conn)
  return df
