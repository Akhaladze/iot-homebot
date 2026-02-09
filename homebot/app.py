import os
import json
import requests
import pandas as pd
import duckdb
import urllib3
from flask import request, Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
from services.mikrotik import MikroTikService
from homebot.services.telegrambot import tg_service

app = Flask(__name__)


app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Constants
DB_NAME = "network.db"
PARQUET_DIR = "data"

# Initialize MikroTik service (Берем из ENV, которые мы настроили в k3s)
MIKROTIK_HOST = os.getenv("MIKROTIK_HOST", "10.10.100.1")
MIKROTIK_USER = os.getenv("MIKROTIK_USER", "homebot")
MIKROTIK_PASSWORD = os.getenv("MIKROTIK_PASSWORD") # Пароль берем только из ENV!

mt_service = MikroTikService(MIKROTIK_HOST, MIKROTIK_USER, MIKROTIK_PASSWORD)

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def probe_shelly(ip):
    # ... (ваш код без изменений) ...
    try:
        res = requests.get(f"http://{ip}/rpc/Shelly.GetStatus", timeout=3)
        if res.status_code == 200:
            return {"gen": 2, "data": res.json()}
    except:
        pass
    
    try:
        res = requests.get(f"http://{ip}/status", timeout=3)
        if res.status_code == 200:
            return {"gen": 1, "data": res.json()}
    except:
        pass
    return None

@app.route('/sync-all', methods=['POST', 'GET']) # Разрешил POST для webhook вызова
def sync_all():
    # ... (ваш код без изменений) ...
    try:
        raw_leases = mt_service.get_dhcp_leases()
        df_leases = pd.DataFrame(raw_leases)
        
        os.makedirs(PARQUET_DIR, exist_ok=True)
        df_leases.to_parquet(f"{PARQUET_DIR}/leases_latest.parquet", engine='pyarrow', index=False)

        with duckdb.connect(DB_NAME) as con:
            con.execute("CREATE TABLE IF NOT EXISTS raw_leases AS SELECT * FROM df_leases WHERE 1=0")
            con.execute("DELETE FROM raw_leases")
            con.execute("INSERT INTO raw_leases SELECT * FROM df_leases")
            # ... остальная логика базы данных ...
            con.execute("""
                CREATE OR REPLACE VIEW active_shelly AS 
                SELECT address as ip, "host-name" as hostname FROM raw_leases 
                WHERE "host-name" ILIKE 'shelly%'
            """)
            shelly_ips = con.execute("SELECT ip, hostname FROM active_shelly").fetchall()

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
            # ... сохранение parquet ...

        return jsonify({"status": "success", "synced_shelly": len(results)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Webhook Endpoint ---
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        # Передаем обновление в телеграм сервис
        update = tg_service.process_new_updates([telebot.types.Update.de_json(json_string)])
        return 'OK', 200
    else:
        return jsonify({"error": "Forbidden"}), 403

# Эндпоинт для инициализации вебхука (чтобы не дергать curl вручную)
@app.route('/init-webhook', methods=['GET'])
def init_webhook_route():
    webhook_url = os.getenv("WEBHOOK_URL") # https://api.cloudpak.info
    if not webhook_url:
        return "WEBHOOK_URL env not set", 500
    
    # Удаляем и ставим заново
    tg_service.bot.remove_webhook()
    success = tg_service.bot.set_webhook(url=f"{webhook_url}/webhook")
    
    return f"Webhook set to {webhook_url}/webhook: {success}"

if __name__ == '__main__':
    # Этот блок срабатывает ТОЛЬКО при локальном запуске (python app.py)
    # В k3s (через gunicorn) он игнорируется
    app.run(host='0.0.0.0', port=5000, debug=True)
