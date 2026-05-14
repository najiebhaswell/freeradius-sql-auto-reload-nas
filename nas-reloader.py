#!/usr/bin/env python3
# FreeRADIUS NAS Change Restarter (Python 3, modernized)

import json
import pymysql
import subprocess
import sys
import os

MARKER_PATH = "/var/lib/reloader/marker"
CONFIG_PATH = "/etc/reloader.json"

def get_db_version(config):
    conn = pymysql.connect(
        host=config['host'],
        user=config['username'],
        password=config['password'],
        database=config['database']
    )
    with conn.cursor() as cur:
        cur.execute("SELECT `id` FROM `nas_changes` ORDER BY `id` DESC LIMIT 1")
        row = cur.fetchone()
    conn.close()
    return int(row[0]) if row else 0

def get_local_version():
    if not os.path.exists(MARKER_PATH):
        with open(MARKER_PATH, 'w') as f:
            f.write('0')
    with open(MARKER_PATH, 'r') as f:
        return int(f.read().strip() or '0')

def set_local_version(ver):
    with open(MARKER_PATH, 'w') as f:
        f.write(str(ver))

def restart_radius():
    result = subprocess.run(
        ["systemctl", "restart", "freeradius"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("FreeRADIUS restarted successfully.")
    else:
        print(f"Restart failed: {result.stderr}")
    return result.returncode

# Load config
config_path = sys.argv[1] if len(sys.argv) == 2 else CONFIG_PATH
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except IOError:
    print(f"Cannot open config: {config_path}")
    sys.exit(1)

db_ver = get_db_version(config['database'])
local_ver = get_local_version()

if db_ver > local_ver:
    print(f"NAS change detected (db={db_ver}, local={local_ver}). Restarting FreeRADIUS...")
    status = restart_radius()
    if status == 0:
        set_local_version(db_ver)
else:
    print("No NAS changes detected. Nothing to do.")
