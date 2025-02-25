# README.md

# La Familia Project ESP32

## Description
This project consists of a Python Flask server and an ESP32-based IoT system that collects temperature and humidity data using a DHT11 sensor. The data is sent to both Ubidots and a MongoDB database.

## Requirements
- Python 3.x
- Flask (`pip install flask`)
- PyMongo (`pip install pymongo`)
- Requests (`pip install requests`)
- ESP32 with MicroPython firmware

## Setup Instructions

### Flask Server
1. Install dependencies:
   ```sh
   pip install flask pymongo requests
   ```
2. Run the server:
   ```sh
   python server.py
   ```

### ESP32 Setup
1. Flash MicroPython onto your ESP32.
2. Upload `main.py` to your ESP32.
3. Ensure WiFi credentials are set correctly in the code.
4. Run the script:
   ```python
   import main
   main.run()
   ```

## Code: Flask Server (server.py)
```python
import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Koneksi ke MongoDB menggunakan URI yang diberikan
uri = "mongodb+srv://sirhanrkasyarobot:xhKnsaK9m0y6gR7D@cluster0.tsalh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['data_sensor']
sensor_collection = db['dht11']

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/kirim_data', methods=['POST'])
def sensor1():
    data = request.json  # Pastikan format JSON
    
    # Validasi data
    if not data or 'temperature' not in data or 'kelembapan' not in data:
        return jsonify({'error': 'Bad Request', 'message': 'Temperature and kelembapan are required!'}), 400

    try:
        temperature = float(data['temperature'])
        kelembapan = float(data['kelembapan'])
    except ValueError:
        return jsonify({'error': 'Bad Request', 'message': 'Temperature and kelembapan must be numeric!'}), 400

    # Menyimpan data dengan timestamp
    sensor_data = {
        'temperature': temperature,
        'kelembapan': kelembapan,
        'timestamp': datetime.utcnow()
    }

    result = sensor_collection.insert_one(sensor_data)

    return jsonify({'message': 'Data inserted successfully!', 'id': str(result.inserted_id)}), 201

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
```

## Code: ESP32 (main.py)
```python
import network
import machine as m
import socket
import time
import requests
import dht
import json
from machine import Pin

# Konfigurasi WiFi
SSID = "JUS KODE"
PASSWORD = "12345678"
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(SSID, PASSWORD)

def checkwifi():
    while not sta_if.isconnected():
        time.sleep(1)
        print("Menunggu koneksi WiFi...")
        sta_if.connect(SSID, PASSWORD)

# Konfigurasi Ubidots
TOKEN = "BBUS-3lfofvvtRU5j05KZeC5yET4cjXyjjZ"
DEVICE_LABEL = "esp-lafamila"
VARIABLE_LABEL_TEMP = "temperature"
VARIABLE_LABEL_HUM = "humidity"

# Konfigurasi MongoDB
SERVER_URL = "http://192.168.1.32:5000/kirim_data"

# Inisialisasi sensor DHT11
sensor1 = dht.DHT11(Pin(27))

def send_data_to_ubidots(temp, hum):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/{}".format(DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
    payload = {
        VARIABLE_LABEL_TEMP: temp,
        VARIABLE_LABEL_HUM: hum
    }
    
    try:
        req = requests.post(url, headers=headers, json=payload)
        print("Status Code (Ubidots):", req.status_code)
        print("Response (Ubidots):", req.json())
    except Exception as e:
        print("[ERROR] Gagal mengirim data ke Ubidots:", e)

def send_data_to_mongodb(temp, hum):
    payload = json.dumps({"temperature": temp, "kelembapan": hum})
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(SERVER_URL, data=payload, headers=headers)
        print("Status Code (MongoDB):", response.status_code)
        print("Response (MongoDB):", response.text)
        response.close()
    except Exception as e:
        print("[ERROR] Gagal mengirim data ke MongoDB:", e)

def main():
    checkwifi()
    while True:
        try:
            sensor1.measure()
            temp = sensor1.temperature()
            hum = sensor1.humidity()
            print(f"Temperature: {temp} C")
            print(f"Humidity: {hum} %")
            send_data_to_ubidots(temp, hum)
            send_data_to_mongodb(temp, hum)
        except OSError as e:
            print("[ERROR] Gagal membaca sensor.")
        time.sleep(5)

if __name__ == '__main__':
    main()
```

## Gitignore File
```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
build/
dist/
.eggs/
*.egg-info/

# Virtual environments
.env
.venv
venv/

# Logs and cache
*.log
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints/

# Others
.DS_Store
```
