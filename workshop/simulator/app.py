"""Workshop-app: één proces, één meting per seconde, HTTP op 5000."""
import json
import random
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os

lock = threading.Lock()
latest = {}

def measure():
    sequence = 0
    while True:
        sequence += 1
        data = {
            "sensor_id": os.getenv("HOSTNAME", "simulator"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": round(random.uniform(18, 25), 1),
            "humidity": round(random.uniform(35, 65), 1),
            "sequence": sequence,
        }
        with lock:
            latest.clear()
            latest.update(data)
        print(json.dumps(data), flush=True)
        time.sleep(1)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/healthz":
            data, status = {"status": "ok"}, 200
        elif path in ("/", "/sensor"):
            with lock:
                data = dict(latest)
            status = 200 if data else 503
        else:
            data, status = {"error": "Gebruik /sensor of /healthz"}, 404
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    threading.Thread(target=measure, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
