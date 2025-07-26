import base64
import oracledb
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import paramiko
import pandas as pd
from django.http import HttpResponse
from io import BytesIO

# Read and decode base64 passwords from file
def load_db_passwords(file_path="/var/www/cgi-bin/database/databaseOps/databaseMain/db_passwords1.txt"):
    passwords = {}
    with open(file_path, "r") as file:
        for line in file:
            if ":" in line:
                key, encoded_pw = line.strip().split(":", 1)
                key = key.strip()
                encoded_pw = encoded_pw.strip()
                try:
                    #decoded_pw = base64.b64decode(encoded_pw).decode("utf-8")
                   # passwords[key] = decoded_pw
                    passwords[key] = encoded_pw
                except Exception as e:
                    print(f"Failed to decode password for {key}: {e}")
    print(passwords)
    return passwords

# Load passwords from file
PASSWORDS = load_db_passwords()

# Database config without passwords
DB_CONFIG = {
    "PR": {
        "MIPR": {"dsn": "10.191.170.107:1787/MIIBPRDB_SRV", "user": "sys"},
        "SIPR": {"dsn": "10.191.170.109:1787/sbisipr", "user": "sys"},
        "RepoPR": {"dsn": "10.191.170.110:1787/REPODB_SRV", "user": "sys"},
        "ArchivalPR": {"dsn": "10.191.170.111:1787/ARCHNPR_SRV", "user": "sys"},
        "HIDR": {"dsn": "10.191.170.107:1787/hiibprdb", "user": "sys"}
    },
    "DR": {
        "MIDR": {"dsn": "10.176.0.107:1787/MIBDRCDB_SRV", "user": "sys"},
        "SIDR": {"dsn": "10.176.0.109:1787/sbisidr", "user": "sys"},
        "RepoDR": {"dsn": "10.176.0.110:1787/SIDASHDB_SRV", "user": "sys"},
        "ArchivalDR": {"dsn": "10.176.0.111:1787/archpdb", "user": "sys"},
        "HIPR": {"dsn": "10.176.0.107:1787/HIIBPRDB_SRV", "user": "sys"}
    }
}

@csrf_exempt
def get_stats(request):
    env = request.GET.get("env")
    db = request.GET.get("db")
    active_sessions=0;
    mi_max = None;
    hi_max = None;
    if env not in DB_CONFIG or db not in DB_CONFIG[env]:
        return JsonResponse({"error": "Invalid environment or database name."}, status=400)

    config = DB_CONFIG[env][db]
    key = f"{env}.{db}"

    if key not in PASSWORDS:
        return JsonResponse({"error": f"Password not found for {key}."}, status=500)

    try:
        conn = oracledb.connect(
            user=config["user"],
            password=PASSWORDS[key],
            dsn=config["dsn"],
            mode=oracledb.SYSDBA
        )
        cursor = conn.cursor()
        print("here")
        # FRA %
        cursor.execute("""
            SELECT ROUND(((SPACE_LIMIT/1024/1024/1024/1024 - SPACE_USED/1024/1024/1024/1024) /
                         (SPACE_LIMIT/1024/1024/1024/1024) * 100), 2)
            FROM V$RECOVERY_FILE_DEST
        """)
        fra = cursor.fetchone()[0]


        cursor.execute(""" select  count(1) COUNT from  v$session where status='ACTIVE'""")
        active_sessions= cursor.fetchone()[0]
        # PR/DR Sync
        cursor.execute("""
            SELECT thread#, MAX(sequence#) AS seq_received
            FROM v$archived_log
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

                # MAX%
        if(env == "PR" and  db=="ArchivalPR"):
            print("1")
            cursor.execute("""
                select /*+parallel(32)*/ max(creation_date_time) from iibarch.api_log_25Q3 partition(JUL_25) where EXP_IP like '10.188%'
                      """)

            mi_max = cursor.fetchone()[0]
            mi_max.strftime("%d-%m-%Y %I:%M:%S %p")
            cursor.execute("""
                select /*+parallel(32)*/ max(creation_date_time) from iibarch.api_log_25Q3 partition(JUL_25) where EXP_IP like '10.177%'
                      """)
            hi_max = cursor.fetchone()[0]
            hi_max.strftime("%d-%m-%Y %I:%M:%S %p")
        conn.close()

        return JsonResponse({
            "fra": fra,
            "sync_status": sync_status,
            "active_sessions":active_sessions,
            "mi_max":str(mi_max),
            "hi_max":str(hi_max)
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def download_latest_report(request):
    host = "10.191.170.107"
    username = "oracle"  # or another SSH-access user
    password = "your_password"  # only if you're using password auth
    remote_path = "/home/oracle/scripts/daily_report/"

    # Connect via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password)

    # Use SFTP to list and get the latest file
    sftp = ssh.open_sftp()
    sftp.chdir(remote_path)
    files = sftp.listdir_attr()
    latest_file = sorted(files, key=lambda f: f.st_mtime, reverse=True)[0]
    remote_file_path = remote_path + latest_file.filename

    # Read file content
    with sftp.open(latest_file.filename, 'r') as remote_file:
        lines = remote_file.readlines()

    sftp.close()
    ssh.close()

    # Example: Convert to Excel (assuming CSV-like structure)
    data = [line.strip().split(",") for line in lines]
    df = pd.DataFrame(data[1:], columns=data[0])  # Assuming first line is header

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{latest_file.filename}.xlsx"'
    return response

