from flask import Flask, jsonify, render_template
from flask_sock import Sock
from time import sleep
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import os, logging, json

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
sock = Sock(app)

@sock.route('/ws')
def subscribe(ws):
    broker = os.getenv("MQTT_BROKER")
    port = int(os.getenv("MQTT_PORT"))
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")
    topic_base = os.getenv("MQTT_TOPIC_BASE")
    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.tls_set()
    client.connect(broker, port, 60)
    client.subscribe(topic_base)
    client.on_message = lambda client, userdata, msg: ws.send(msg.payload.decode().strip())
    client.loop_forever()

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
