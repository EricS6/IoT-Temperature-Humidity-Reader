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
    m = msg.payload.decode().strip()
    data = json.loads(m)
    
    temp_table = db.Table('Temperature')
    if last_temp_index == -1 or data['temperature'] == last_temp:
        last_temp_index += 1
        last_temp = data['temperature']
        item={
            'index': last_temp_index,
            'temp': data['temperature'],
            'timestamp': data['timestamp']
        }
        try:
            temp_table.put_item(Item=item)
            logging.info(f"Inserted item into Temperature: {item}")
        except Exception as e:
            logging.error(f"Error inserting item into Temperature: {e}")
            
    hum_table = db.Table('Humidity')
    if last_hum_index == -1 or data['humidity'] == last_hum:
        last_hum_index += 1
        last_hum = data['humidity']
        item={
            'index': last_hum_index,
            'temp': data['humidity'],
            'timestamp': data['timestamp']
        }
        try:
            hum_table.put_item(Item=item)
            logging.info(f"Inserted item into Humidity: {item}")
        except Exception as e:
            logging.error(f"Error inserting item into Humidity: {e}")
            
    print(f"Received message on topic {msg.topic}: {m}")
    ws.send(m)

@sock.route('/ws')
def subscribe(ws):
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
        client.on_message = lambda client, userdata, msg: ws.send(msg.payload.decode().strip())
        sleep(2)  # Give some time for subscription to take effect

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
