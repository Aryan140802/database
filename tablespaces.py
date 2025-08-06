# Collect all results here
all_results = {}

for config in db_configs:
    db_name = config["name"]
    try:
        connection = oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=config["dsn"]
        )
        cursor = connection.cursor()
        cursor.execute(query)
        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        result = [dict(zip(columns, row)) for row in rows]
        all_results[db_name] = result
        cursor.close()
        connection.close()
    except Exception as e:
        all_results[db_name] = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# Write to tbs_output.json
with open("tbs_output.json", "w") as f:
    json.dump(all_results, f, indent=4)
