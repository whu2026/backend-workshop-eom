from flask import Flask, jsonify
from datetime import datetime, timezone
import random
import threading
import time
import os
import json
import pika

app = Flask(__name__)

latest_data = {
    "sensor_id": "sensor-001",
    "timestamp": None,
    "temperature": None,
    "humidity": None,
    "sequence": 0,
}

RABBITMQ_HOST = os.getenv(
    "RABBITMQ_HOST",
    "rabbitmq-service.backend-workshop.svc.cluster.local",
)
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ["RABBITMQ_USER"]
RABBITMQ_PASS = os.environ["RABBITMQ_PASS"]
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "sim_sensor_exchange")
ROUTING_KEY = os.getenv("ROUTING_KEY", "sensor.data")


def generate_sensor_data():
    """Generate a new sensor measurement every second."""
    while True:
        latest_data["sequence"] += 1
        latest_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        latest_data["temperature"] = round(random.uniform(18.0, 28.0), 2)
        latest_data["humidity"] = round(random.uniform(35.0, 70.0), 2)
        time.sleep(1)


def publish_to_rabbitmq():
    """Publish the latest measurement and retry when RabbitMQ is unavailable."""
    connection = None
    channel = None
    while True:
        try:
            if connection is None or connection.is_closed:
                credentials = pika.PlainCredentials(
                    RABBITMQ_USER,
                    RABBITMQ_PASS,
                )
                parameters = pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    virtual_host=RABBITMQ_VHOST,
                    credentials=credentials,
                    heartbeat=30,
                    blocked_connection_timeout=5,
                    connection_attempts=3,
                    retry_delay=2,
                )
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                print(
                    f"Connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}",
                    flush=True,
                )

            message = latest_data.copy()
            if message["timestamp"] is not None:
                channel.basic_publish(
                    exchange=EXCHANGE_NAME,
                    routing_key=ROUTING_KEY,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        content_type="application/json",
                        delivery_mode=2,
                    ),
                )
            time.sleep(1)
        except (pika.exceptions.AMQPError, OSError) as error:
            print(
                f"RabbitMQ is unavailable: {error}. Retrying in 5 seconds.",
                flush=True,
            )
            connection = None
            channel = None
            time.sleep(5)


@app.get("/sensor")
def get_sensor_data():
    return jsonify(latest_data.copy())


if __name__ == "__main__":
    threading.Thread(target=generate_sensor_data, daemon=True).start()
    threading.Thread(target=publish_to_rabbitmq, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
