import oracledb
import json
import traceback

# === DB connection details for all 4 databases ===
DB_CONFIG = {
    "PR": {
        "MIPR": {"dsn": "10.191.170.107:1787/MIIBPRDB_SRV", "user": "sys"},
        "SIPR": {"dsn": "10.191.170.109:1787/sbisipr", "user": "sys"},
        "RepoPR": {"dsn": "10.191.170.110:1787/REPODB_SRV", "user": "sys"},
        "ArchivalPR": {"dsn": "10.191.170.111:1787/ARCHNPR_SRV", "user": "sys"},
        "HIDR": {"dsn": "10.191.170.107:1787/hiibprdb", "user": "sys"}
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
all_results={}

def fetch_tablespace_data(config):
        env = request.GET.get("env")
    db = request.GET.get("db")
    if env not in DB_CONFIG or db not in DB_CONFIG[env]:
        return JsonResponse({"error": "Invalid environment or database name."}, status=400)

    config = DB_CONFIG[env][db]
    key = f"{env}.{db}"

    if key not in PASSWORDS:
        return JsonResponse({"error": f"Password not found for {key}."}, status=500)


    try:
        connection = oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=config["dsn"]
        )
        cursor = connection.cursor()
        cursor.execute(TABLESPACE_QUERY)
        result = cursor.fetchone()
        connection.close()

        return {
            "database": config["name"],
            "status": "success",
            "data": json.loads(result[0]) if result and result[0] else []
        }

    except Exception as e:
        return {
            "database": config["name"],
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc()
        }

def main():
    final_output = []
    for config in DB_CONFIG:
        print(f"Fetching from {config['name']}...")
        result = fetch_tablespace_data(config)
        final_output.append(result)

    print(json.dumps(final_output, indent=4))

if __name__ == "__main__":
    main()
