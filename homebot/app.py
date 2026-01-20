import os
import json
import requests
import pandas as pd
import duckdb
import urllib3
from flask import Flask, jsonify
from datetime import datetime
from services.mikrotik import MikroTikService

app = Flask(__name__)

# Constants
DB_NAME = "network.db"
PARQUET_DIR = "data"

# Initialize MikroTik service
MIKROTIK_HOST = os.getenv("MIKROTIK_HOST", "10.10.100.1")
MIKROTIK_USER = os.getenv("MIKROTIK_USER", "homebot")
MIKROTIK_PASSWORD = os.getenv("MIKROTIK_PASSWORD", "homebot!2025!")

mt_service = MikroTikService(MIKROTIK_HOST, MIKROTIK_USER, MIKROTIK_PASSWORD)

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def probe_shelly(ip):
    """
    Probes a Shelly device to determine its generation and fetch status.
    Returns: {"gen": int, "data": dict} or None
    """
    # Try Gen 2/3 (RPC API)
    try:
        res = requests.get(f"http://{ip}/rpc/Shelly.GetStatus", timeout=3)
        if res.status_code == 200:
            return {"gen": 2, "data": res.json()}
    except:
        pass
    
    # Fallback to Gen 1
    try:
        res = requests.get(f"http://{ip}/status", timeout=3)
        if res.status_code == 200:
            return {"gen": 1, "data": res.json()}
    except:
        pass
    return None

@app.route('/sync-all')
def sync_all():
    try:
        # 1. Sync MikroTik Leases
        raw_leases = mt_service.get_dhcp_leases()
        df_leases = pd.DataFrame(raw_leases)
        
        os.makedirs(PARQUET_DIR, exist_ok=True)
        df_leases.to_parquet(f"{PARQUET_DIR}/leases_latest.parquet", engine='pyarrow', index=False)

        with duckdb.connect(DB_NAME) as con:
            con.execute("CREATE TABLE IF NOT EXISTS raw_leases AS SELECT * FROM df_leases WHERE 1=0")
            con.execute("DELETE FROM raw_leases")
            con.execute("INSERT INTO raw_leases SELECT * FROM df_leases")
            con.execute("""
                CREATE OR REPLACE VIEW active_shelly AS 
                SELECT address as ip, "host-name" as hostname FROM raw_leases 
                WHERE "host-name" ILIKE 'shelly%'
            """)
            shelly_ips = con.execute("SELECT ip, hostname FROM active_shelly").fetchall()

        # 2. Sync Shelly Statuses
        results = []
        scan_time = datetime.now()
        for ip, hostname in shelly_ips:
            info = probe_shelly(ip)
            if info:
                results.append({
                    "scanned_at": scan_time,
                    "ip": ip,
                    "hostname": hostname,
                    "gen": info["gen"],
                    "raw_status": json.dumps(info["data"])
                })

        if results:
            df_shelly = pd.DataFrame(results)
            df_shelly.to_parquet(f"{PARQUET_DIR}/shelly_raw.parquet", engine='pyarrow', index=False)
            with duckdb.connect(DB_NAME) as con:
                con.execute("CREATE TABLE IF NOT EXISTS raw_shelly_data AS SELECT * FROM df_shelly WHERE 1=0")
                con.execute("INSERT INTO raw_shelly_data SELECT * FROM df_shelly")

        return jsonify({"status": "success", "synced_shelly": len(results)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)