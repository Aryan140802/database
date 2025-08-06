import oracledb
import json
import traceback

# === DB connection details for all 4 databases ===
DB_CONFIGS = [
    {
        "name": "DB1",
        "user": "user1",
        "password": "pass1",
        "dsn": "host1:1521/service1"
    },
    {
        "name": "DB2",
        "user": "user2",
        "password": "pass2",
        "dsn": "host2:1521/service2"
    },
    {
        "name": "DB3",
        "user": "user3",
        "password": "pass3",
        "dsn": "host3:1521/service3"
    },
    {
        "name": "DB4",
        "user": "user4",
        "password": "pass4",
        "dsn": "host4:1521/service4"
    }
]

# === Query to run on each DB ===
QUERY = "SELECT * FROM your_table FETCH FIRST 10 ROWS ONLY"

def fetch_data_from_db(config):
    try:
        connection = oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=config["dsn"]
        )
        cursor = connection.cursor()
        cursor.execute(QUERY)

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

        # Format result as list of dicts
        results = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        connection.close()

        return {
            "database": config["name"],
            "status": "success",
            "rows": results
        }

    except Exception as e:
        return {
            "database": config["name"],
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc()
        }

def main():
    all_results = []

    for config in DB_CONFIGS:
        result = fetch_data_from_db(config)
        all_results.append(result)

    print(json.dumps(all_results, indent=4, default=str))

if __name__ == "__main__":
    main()
