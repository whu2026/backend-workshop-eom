from flask import Flask, jsonify
from datetime import datetime, timezone
import random
import threading
import time

app = Flask(__name__)

latest_data = {
    "sensor_id": "sensor-001",
    "timestamp": None,
    "temperature": None,
    "humidity": None,
    "sequence": 0
}


def generate_sensor_data():
    while True:
        latest_data["sequence"] += 1
        latest_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        latest_data["temperature"] = round(random.uniform(18.0, 28.0), 2)
        latest_data["humidity"] = round(random.uniform(35.0, 65.0), 2)
        print(latest_data, flush=True)
        time.sleep(1)


@app.route("/sensor")
def get_sensor_data():
    return jsonify(latest_data)


if __name__ == "__main__":
    sensor_thread = threading.Thread(target=generate_sensor_data, daemon=True)
    sensor_thread.start()
    app.run(host="0.0.0.0", port=5000)
