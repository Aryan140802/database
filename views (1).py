import oracledb
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Database host mapping
DB_MAP = {
    "PR": {
        "MIPR": "10.191.171.107:1521/MIPR",
        "SIPR": "10.191.171.108:1521/SIPR",
        "RepoPR": "10.191.171.109:1521/REPOPR",
        "ArchivalPR": "10.191.171.110:1521/ARCHPR",
        "HIPR": "10.191.171.111:1521/HIPR"
    },
    "DR": {
        "MIDR": "10.176.0.107:1521/MIDR",
        "SIDR": "10.176.0.108:1521/SIDR",
        "RepoDR": "10.176.0.109:1521/REPODR",
        "ArchivalDR": "10.176.0.110:1521/ARCHDR",
        "HIDR": "10.176.0.111:1521/HIDR"
    }
}

# Credentials (secure in env or settings in production)
DB_USER = "your_user"
DB_PASSWORD = "your_password"

@csrf_exempt
def get_stats(request):
    env = request.GET.get("env")
    db = request.GET.get("db")

    if env not in DB_MAP or db not in DB_MAP[env]:
        return JsonResponse({"error": "Invalid environment or database name."}, status=400)

    dsn = DB_MAP[env][db]

    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=dsn
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
