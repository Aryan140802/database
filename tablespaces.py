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






==================================================================

def fetch_tablespace_data(config):
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
    for config in DB_CONFIGS:
        print(f"Fetching from {config['name']}...")
        result = fetch_tablespace_data(config)
        final_output.append(result)

    print(json.dumps(final_output, indent=4))

if __name__ == "__main__":
    main()
