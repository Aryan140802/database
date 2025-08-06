import os
from django.http import HttpResponse
import xlsxwriter
from io import BytesIO


def convert_report_to_excel(request):
    # Set the path to your Linux server report file
    report_path = "/opt/reports/report.txt"
    if not os.path.exists(report_path):
        return HttpResponse("Report file not found", status=404)

    with open(report_path, "r") as f:
        text = f.read()

    # Create an in-memory output file for the new workbook.
    output = BytesIO()
    wb = xlsxwriter.Workbook(output, {'in_memory': True})

    # Add sheets for each section
    write_volume_trend(wb, text)
    write_net_count(wb, text)
    write_db_sizes(wb, text)
    write_tablespaces(wb, text)
    write_disk_space(wb, text)
    write_rman(wb, text)
    write_archive_threads(wb, text)
    write_daily_volume_trend(wb, text)
    write_mountpoints(wb, text)

    wb.close()
    output.seek(0)

    # Return the Excel file as a response
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response['Content-Disposition'] = 'attachment; filename=full_report.xlsx'
    return response


# === Define parser functions below ===
def write_volume_trend(wb, text):
    sheet = wb.add_worksheet("Volume Trend")
    sheet.write_row(0, 0, ["DateTime", "Count"])
    row = 1
    capture = False
    for line in text.splitlines():
        if "TRUNC(REQUEST_DATE_" in line:
            capture = True
        elif "Elapsed:" in line:
            capture = False
        elif capture:
            parts = line.strip().split()
            if len(parts) >= 2:
                sheet.write_row(row, 0, parts[:2])
                row += 1


def write_net_count(wb, text):
    sheet = wb.add_worksheet("Net Count")
    sheet.write_row(0, 0, ["DateTime", "Count"])
    row = 1
    capture = False
    for line in text.splitlines():
        if "TRUNC(REQ_TIME,'HH'" in line:
            capture = True
        elif "Elapsed:" in line:
            capture = False
        elif capture:
            parts = line.strip().split()
            if len(parts) >= 2:
                sheet.write_row(row, 0, parts[:2])
                row += 1


def write_db_sizes(wb, text):
    sheet = wb.add_worksheet("DB Sizes")
    sheet.write_row(0, 0, ["DB", "Metric", "Value"])
    row = 1
    current_db = ""
    lines = text.splitlines()
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith("* * *") and "DB SIZE" in line.upper():
            current_db = line.replace("*", "").split("(")[0].strip().replace(" ", "")
        elif line in ["DB_TOTAL_SIZE", "DB_ACTUAL_SIZE", "EISAPP_SCHEMA_SIZE"]:
            value = lines[i+2].strip() if i+2 < len(lines) else ""
            if value:
                sheet.write_row(row, 0, [current_db, line, value])
                row += 1


def write_tablespaces(wb, text):
    sheet = wb.add_worksheet("Tablespaces")
    headers = ["DB", "Tablespace", "Size (Mb)", "Used (Mb)", "Free (Mb)", "% Used", "% Free", "Message"]
    sheet.write_row(0, 0, headers)
    row = 1
    current_db = ""
    capture = False
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("TABLESPACE"):
            current_db = line.split()[1]
        elif line.startswith("Tablespace") and "Size (Mb)" in line:
            capture = True
        elif "rows selected" in line:
            capture = False
        elif capture:
            parts = line.split()
            if len(parts) >= 6:
                values = [current_db] + parts[:6] + [" ".join(parts[6:])] if len(parts) > 6 else [""]
                sheet.write_row(row, 0, values)
                row += 1


def write_disk_space(wb, text):
    sheet = wb.add_worksheet("Disk Space")
    headers = ["NAME", "STATE", "TOTAL_MB/1024", "FREE_MB/1024", "USABLE(GB)"]
    sheet.write_row(0, 0, headers)
    row = 1
    capture = False
    for line in text.splitlines():
        line = line.strip()
        if "NAME" in line and "STATE" in line:
            capture = True
        elif line == "" or "rows selected" in line:
            capture = False
        elif capture and not line.startswith("-"):
            parts = line.split()
            if len(parts) == 5:
                sheet.write_row(row, 0, parts)
                row += 1


def write_rman(wb, text):
    current_db = ""
    sheet = None
    row = 1
    for line in text.splitlines():
        line = line.strip()
        if "BACKUP" in line and "(" in line and ")" in line:
            current_db = line.split("(")[0].replace("*", "").strip().replace(" ", "")
            sheet = wb.add_worksheet(f"RMAN - {current_db[:31]}")
            sheet.write_row(0, 0, ["SESSION_KEY", "INPUT_TYPE", "STATUS", "START_TIME", "END_TIME", "HOURS", "SIZE(GB)"])
            row = 1
        elif sheet and line and line[0].isdigit():
            parts = line.split()
            if len(parts) >= 7:
                sheet.write_row(row, 0, parts[:7])
                row += 1


def write_archive_threads(wb, text):
    sheet = wb.add_worksheet("Archive Threads")
    sheet.write_row(0, 0, ["DB", "DAY", "THREAD#", "GB", "ARCHIVES_GENERATED", "MIN(SEQUENCE#)", "MAX(SEQUENCE#)"])
    row = 1
    current_db = ""
    for line in text.splitlines():
        if line.startswith("* * *") and "(" in line:
            current_db = line.replace("*", "").split("(")[0].strip().replace(" ", "")
        elif line and line[0].isdigit():
            parts = line.split()
            if len(parts) == 6:
                sheet.write_row(row, 0, [current_db] + parts)
                row += 1


def write_daily_volume_trend(wb, text):
    sheet = wb.add_worksheet("Daily Volume Trend")
    sheet.write_row(0, 0, ["DB", "DAY", "COUNT#", "MIN#", "MAX#", "MIN(SEQ#)", "MAX(SEQ#)", "AVG_MB"])
    row = 1
    current_db = ""
    for line in text.splitlines():
        if line.startswith("* * *") and "(" in line:
            current_db = line.replace("*", "").split("(")[0].strip().replace(" ", "")
        elif line and line[0].isdigit():
            parts = line.split()
            if len(parts) == 7:
                sheet.write_row(row, 0, [current_db] + parts)
                row += 1


def write_mountpoints(wb, text):
    import re
    blocks = text.split("* * *")
    for block in blocks:
        ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", block)
        if not ip_match:
            continue
        ip = ip_match.group(1)
        lines = block.splitlines()
        headers = []
        rows = []
        capture = False
        for line in lines:
            line = line.strip()
            if line.startswith("Filesystem"):
                headers = line.split()
                capture = True
            elif capture and line:
                parts = line.split()
                if len(parts) >= len(headers):
                    rows.append(parts[:len(headers)])
        if headers and rows:
            sheet = wb.add_worksheet(f"Mount {ip}")
            sheet.write_row(0, 0, headers)
            for r, row_data in enumerate(rows, 1):
                sheet.write_row(r, 0, row_data)
