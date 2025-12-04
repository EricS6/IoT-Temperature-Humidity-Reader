from flask import Flask, jsonify, render_template
from flask_sock import Sock
from time import sleep
from database.db import db
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import os, logging, json

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
sock = Sock(app)
last_temp_index = -1
last_temp = None
last_hum_index = -1
last_hum = None

def message(ws, msg):
    print("Message received")
    global last_temp_index, last_temp, last_hum_index, last_hum
    m = msg.payload.decode().strip()
    data = json.loads(m)
    
    if last_temp_index == -1 or data['temperature'] == last_temp:
        last_temp_index += 1
        last_temp = data['temperature']
        item={
            'index': {
                'N': str(last_temp_index),
            },
            'temp': {
                'N': str(data['temperature']),
            },
            'timestamp': {
                'S': data['timestamp'],
            },
        }
        try:
            db.put_item(TableName='Temperature', Item=item)
            logging.info(f"Inserted item into Temperature: {item}")
        except Exception as e:
            logging.error(f"Error inserting item into Temperature: {e}")
            
    if last_hum_index == -1 or data['humidity'] == last_hum:
        last_hum_index += 1
        last_hum = data['humidity']
        item={
            'index': {
                'N': str(last_hum_index),
            },
            'temp': {
                'N': str(data['humidity']),
            },
            'timestamp': {
                'S': data['timestamp'],
            },
        }
        try:
            db.put_item(TableName='Humidity', Item=item)
            logging.info(f"Inserted item into Humidity: {item}")
        except Exception as e:
            logging.error(f"Error inserting item into Humidity: {e}")
            
    try:
        ws.send(m)
    except Exception as e:
        logging.error(f"Error sending message over WebSocket: {e}")

@sock.route('/ws')
def subscribe(ws):
    try:
        print("WebSocket connection established")
        broker = os.getenv("MQTT_BROKER")
        port = int(os.getenv("MQTT_PORT"))
        username = os.getenv("MQTT_USERNAME")
        password = os.getenv("MQTT_PASSWORD")
        topic_base = os.getenv("MQTT_TOPIC_BASE")
        client = mqtt.Client()
        client.username_pw_set(username, password)
        client.tls_set()
        client.connect(broker, port, 60)
        client.loop_start()
        while True:
            client.subscribe(topic_base)
            client.on_message = lambda client, userdata, msg: message(ws, msg)
            sleep(2)  # Give some time for subscription to take effect
    except Exception as e:
        logging.error(f"WebSocket error: {e}")

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
