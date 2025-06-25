import oracledb
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Combined database mapping with credentials
DB_CONFIG = {
    "PR": {
        "MIPR": {"dsn": "10.191.171.107:1521/MIPR", "user": "sys", "password": "pass1"},
        "SIPR": {"dsn": "10.191.171.108:1521/SIPR", "user": "sys", "password": "pass2"},
        "RepoPR": {"dsn": "10.191.171.109:1521/REPOPR", "user": "sys", "password": "pass3"},
        "ArchivalPR": {"dsn": "10.191.171.110:1521/ARCHPR", "user": "sys", "password": "pass4"},
        "HIPR": {"dsn": "10.191.171.111:1521/HIPR", "user": "sys", "password": "pass5"}
    },
    "DR": {
        "MIDR": {"dsn": "10.176.0.107:1521/MIDR", "user": "sys", "password": "pass6"},
        "SIDR": {"dsn": "10.176.0.108:1521/SIDR", "user": "sys", "password": "pass7"},
        "RepoDR": {"dsn": "10.176.0.109:1521/REPODR", "user": "sys", "password": "pass8"},
        "ArchivalDR": {"dsn": "10.176.0.110:1521/ARCHDR", "user": "sys", "password": "pass9"},
        "HIDR": {"dsn": "10.176.0.111:1521/HIDR", "user": "sys", "password": "pass10"}
    }
}

@csrf_exempt
def get_stats(request):
    env = request.GET.get("env")
    db = request.GET.get("db")

    if env not in DB_CONFIG or db not in DB_CONFIG[env]:
        return JsonResponse({"error": "Invalid environment or database name."}, status=400)

    config = DB_CONFIG[env][db]

    try:
        conn = oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=config["dsn"],
            mode=oracledb.AUTH_MODE_SYSDBA
        )
        cursor = conn.cursor()

        # FRA %
        cursor.execute("SELECT ROUND(SPACE_USED * 100 / SPACE_LIMIT, 2) FROM V$RECOVERY_FILE_DEST")
        fra = cursor.fetchone()[0]

        # Active Sessions
        cursor.execute("SELECT COUNT(*) FROM v$session WHERE status = 'ACTIVE'")
        active_sessions = cursor.fetchone()[0]

        # PR/DR Sync
        cursor.execute("""
            SELECT thread#, MAX(sequence#) AS seq_received
            FROM v$archived_log
            WHERE destination = 'REMOTE'
            GROUP BY thread#
        """)
        received = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("""
            SELECT thread#, MAX(sequence#) AS seq_applied
            FROM v$log_history
            GROUP BY thread#
        """)
        applied = {row[0]: row[1] for row in cursor.fetchall()}

        sync_status = []
        for thread in sorted(set(received) | set(applied)):
            r = received.get(thread, 0)
            a = applied.get(thread, 0)
            sync_status.append({
                "thread": thread,
                "received": r,
                "applied": a,
                "diff": r - a
            })

        conn.close()

        return JsonResponse({
            "fra": fra,
            "active_sessions": active_sessions,
            "sync_status": sync_status
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
