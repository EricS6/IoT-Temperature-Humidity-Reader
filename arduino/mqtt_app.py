import serial, json, time, os, datetime
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from datetime import timedelta, timezone, datetime

load_dotenv()

# --- MQTT Client Setup ---
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

# --- Serial Connection ---
serial_port = os.getenv("ARDUINO_SERIAL_PORT")
baud_rate = int(os.getenv("ARDUINO_BAUD_RATE"))
ser = serial.Serial(serial_port, baud_rate, timeout=2)
print(f"Connected to {serial_port}, publishing to {broker}")

while True:
    try:
        line = ser.readline().decode().strip()
        if not line:
            continue
        # Parse Arduino JSON output
        data = json.loads(line)
        tz = timezone(timedelta())
        data["timestamp"] = datetime.now(tz).isoformat() + "Z"
        payload = json.dumps(data)

        client.publish(topic_base, payload)
        print("Published:", payload)
        time.sleep(1)
    except Exception as e:
        print("Error:", e)
