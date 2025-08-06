import oracledb
import json
import traceback

# === DB connection details for all 4 databases ===
DB_CONFIG = {
    "PR": {
        "MIPR": {"dsn": "10.191.170.107:1787/MIIBPRDB_SRV", "user": "sys", "password": "your_password"},
        "SIPR": {"dsn": "10.191.170.109:1787/sbisipr", "user": "sys", "password": "your_password"},
        "RepoPR": {"dsn": "10.191.170.110:1787/REPODB_SRV", "user": "sys", "password": "your_password"},
        "ArchivalPR": {"dsn": "10.191.170.111:1787/ARCHNPR_SRV", "user": "sys", "password": "your_password"},
        "HIDR": {"dsn": "10.191.170.107:1787/hiibprdb", "user": "sys", "password": "your_password"}
    }
}

# === Query to run on each DB ===
TABLESPACE_QUERY = """
WITH ts_data AS (
  SELECT df.tablespace_name tspace,
         ROUND(SUM(fs.bytes_free + fs.bytes_used) / 1024 / 1024, 2) tot_ts_size,
         ROUND(SUM(fs.bytes_used) / 1024 / 1024, 2) used_ts_size,
         ROUND(SUM(fs.bytes_free) / 1024 / 1024, 2) free_ts_size,
         ROUND(SUM(fs.bytes_used) * 100 / SUM(fs.bytes_free + fs.bytes_used)) used_pct,
         ROUND(SUM(fs.bytes_free) * 100 / SUM(fs.bytes_free + fs.bytes_used)) free_pct,
         DECODE(SIGN(SUM(ROUND(((fs.bytes_free + fs.bytes_used) - fs.bytes_free) * 100 / (fs.bytes_free + fs.bytes_used))) - 80), 1, '!ALERT', '') warning
  FROM SYS.V_$TEMP_SPACE_HEADER fs
  JOIN dba_temp_files df ON fs.tablespace_name = df.tablespace_name AND fs.file_id = df.file_id
  GROUP BY df.tablespace_name

  UNION ALL

  SELECT df.tablespace_name tspace,
         df.bytes / (1024 * 1024) tot_ts_size,
         ROUND((df.bytes - SUM(fs.bytes)) / (1024 * 1024)) used_ts_size,
         SUM(fs.bytes) / (1024 * 1024) free_ts_size,
         ROUND((df.bytes - SUM(fs.bytes)) * 100 / df.bytes) used_pct,
         ROUND(SUM(fs.bytes) * 100 / df.bytes) free_pct,
         DECODE(SIGN(ROUND((df.bytes - SUM(fs.bytes)) * 100 / df.bytes) - 80), 1, '!ALERT', '') warning
  FROM dba_free_space fs
  JOIN (
    SELECT tablespace_name, SUM(bytes) bytes
    FROM dba_data_files
    GROUP BY tablespace_name
  ) df ON fs.tablespace_name = df.tablespace_name
  GROUP BY df.tablespace_name, df.bytes

  UNION ALL

  SELECT tablespace_name tspace,
         1 tot_ts_size,
         1 used_ts_size,
         0 free_ts_size,
         100 used_pct,
         0 free_pct,
         '!' warning
  FROM dba_data_files
  GROUP BY tablespace_name
  MINUS
  SELECT tablespace_name tspace,
         1 tot_ts_size,
         1 used_ts_size,
         0 free_ts_size,
         100 used_pct,
         0 free_pct,
         '!' warning
  FROM dba_free_space
  GROUP BY tablespace_name
)
SELECT JSON_ARRAYAGG(
         JSON_OBJECT(
           'tablespace' VALUE tspace,
           'tot_ts_size' VALUE tot_ts_size,
           'used_ts_size' VALUE used_ts_size,
           'free_ts_size' VALUE free_ts_size,
           'used_pct' VALUE used_pct,
           'free_pct' VALUE free_pct,
           'warning' VALUE warning
         )
       ) AS tablespace_usage
FROM ts_data
"""

def fetch_tablespace_data(env, dbname, config):
    try:
        connection = oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=config["dsn"],
            mode=oracledb.SYSDBA  # since you're connecting as SYS
        )
        cursor = connection.cursor()
        cursor.execute(TABLESPACE_QUERY)
        result = cursor.fetchone()
        connection.close()

        return {
            "database": f"{env}.{dbname}",
            "status": "success",
            "data": json.loads(result[0]) if result and result[0] else []
        }

    except Exception as e:
        return {
            "database": f"{env}.{dbname}",
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc()
        }

def main():
    all_results = []

    for env in DB_CONFIG:
        for dbname, config in DB_CONFIG[env].items():
            print(f"Fetching tablespace data from {env}.{dbname}...")
            result = fetch_tablespace_data(env, dbname, config)
            all_results.append(result)

    # Save to file
    with open("tbs_output.json", "w") as outfile:
        json.dump(all_results, outfile, indent=4)

    print("✅ Data saved to tbs_output.json")

if __name__ == "__main__":
    main()
