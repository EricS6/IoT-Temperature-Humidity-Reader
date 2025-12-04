# IoT-Temperature-Humidity-Reader

## Description

An application that that reads data from an Arduino DHT11 Temperature/Humidity Sensor and displays the data in the form of graphs in a Flask-based Python web application.

## Installation

1. Clone the code onto your device/devices.

2. Install Python version 3.10 or later

3. Create and activate a virtual environment.

Powershell:
```ps1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/MacOS:
```sh
python -m venv .venv
source .venv/bin/activate
```

4. Install all required Python libraries

```sh
pip install -r requirements.txt
```

5. Set up your Arduino board an sensor.

6. Install the DHT Sensor Library by Adafruit onto the Arduino IDE

7. Upload `arduino/sensor1/sensor1.ino` to your Arduino board.

8. Create a cluster with an MQTT broker (ex. HiveMQ) with TLS enabled.

9. Create a user to access the MQTT data.

10. Create an AWS IAM role with access to DynamoDB.

11. Create a file named ".env" and use `.env.example` for an example on what to put in it.

12. Initialize the database.

```sh
python app/database/init_db.py
```

## Usage

To run the mqtt Python application on the device plugged into your Arduino board:
```sh
python arduino/mqtt_app.py
```

To run the Flask application:
```sh
python app/app.py
```

You can delete the database by running `app/database/delete_db.py`.

## License

This software is licensed under [MIT](https://github.com/EricS6/IoT-Temperature-Humidity-Reader/blob/main/LICENSE).