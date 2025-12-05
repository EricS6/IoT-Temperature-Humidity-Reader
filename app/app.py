from flask import Flask, jsonify, render_template
from flask_sock import Sock
from time import sleep
from database.db import db
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, logging, json
from datetime import datetime
import pytz

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
sock = Sock(app)

def message(ws, msg):
    m = msg.payload.decode().strip()
    data = json.loads(m)
    
    item={
        'timestamp': {
            'S': data['timestamp'],
        },
        'temperature': {
            'N': str(data['temperature']),
        },
        'humidity': {
            'N': str(data['humidity']),
        },
    }
    try:
        db.put_item(TableName='Reader', Item=item)
        logging.info(f"Inserted item into database: {item}")
    except Exception as e:
        logging.error(f"Error inserting item into database: {e}")
            
    try:
        ws.send(json.dumps({
            'type': 'data_update',
        }))
    except Exception as e:
        logging.error(f"Error sending message over WebSocket: {e}")
        
def get_time_offsets(items):
    # Parse timestamps and calculate minutes ago relative to the most recent datapoint
    parsed_times = []
    for item in items:
        try:
            ts_str = item['timestamp']['S']
            if ts_str.endswith('Z'):
                ts_str = ts_str[:-1]
            try:
                ts = datetime.fromisoformat(ts_str)
            except ValueError:
                ts = datetime.fromisoformat(ts_str + '+00:00')
            if ts.tzinfo is None:
                ts = pytz.UTC.localize(ts)
            parsed_times.append(ts)
        except Exception as e:
            logging.warning(f"Could not parse timestamp {item['timestamp']['S']}: {e}")
            parsed_times.append(None)

    # Use the most recent valid timestamp as reference so offsets only change when data changes
    most_recent = max([t for t in parsed_times if t is not None], default=None)
    time_offsets = []
    for ts in parsed_times:
        if ts is None or most_recent is None:
            time_offsets.append(0)
        else:
            delta = (most_recent - ts).total_seconds() / 60.0
            time_offsets.append(delta)
            
    return time_offsets
        
def get_temp_plot():
    try:
        response = db.scan(TableName='Reader')
        items = response.get('Items', [])
        
        if not items:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            ax.set_title('Temperature over Time')
            return fig
        
        items = sorted(items, key=lambda x: x['timestamp']['S'])
        temps = [float(item['temperature']['N']) for item in items]
        
        time_offsets = get_time_offsets(items)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(time_offsets, temps, marker='none', linestyle='-', color='red', linewidth=2)
        ax.set_title('Temperature over Time')
        ax.set_xlabel('Minutes Ago')
        ax.set_ylabel('Temperature (°F)')
        ax.grid(True, alpha=0.3)
        # Invert x-axis so most recent is on the right
        ax.invert_xaxis()
        logging.info("Temperature plot generated successfully")
        return fig
    except Exception as e:
        logging.error(f"Error generating temperature plot: {e}")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, f'Error: {str(e)}', ha='center', va='center')
        return fig

def get_humidity_plot():
    try:
        response = db.scan(TableName='Reader')
        items = response.get('Items', [])
        
        if not items:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            ax.set_title('Humidity over Time')
            return fig
        
        items = sorted(items, key=lambda x: x['timestamp']['S'])
        humidities = [float(item['humidity']['N']) for item in items]  
        
        time_offsets = get_time_offsets(items)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(time_offsets, humidities, marker='none', linestyle='-', color='blue', linewidth=2)
        ax.set_title('Humidity over Time')
        ax.set_xlabel('Minutes Ago')
        ax.set_ylabel('Humidity (%)')
        ax.grid(True, alpha=0.3)
        # Invert x-axis so most recent is on the right
        ax.invert_xaxis()
        logging.info("Humidity plot generated successfully")
        return fig
    except Exception as e:
        logging.error(f"Error generating humidity plot: {e}")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, f'Error: {str(e)}', ha='center', va='center')
        return fig

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

@app.get("/api/temperature-graph")
def get_temperature_graph():
    import io
    import base64
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    
    fig = get_temp_plot()
    img = io.BytesIO()
    FigureCanvasAgg(fig).print_png(img)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return jsonify(image=plot_url)

@app.get("/api/humidity-graph")
def get_humidity_graph():
    import io
    import base64
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    
    fig = get_humidity_plot()
    img = io.BytesIO()
    FigureCanvasAgg(fig).print_png(img)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return jsonify(image=plot_url)

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
