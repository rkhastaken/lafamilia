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
SERVER_URL = "http://192.168.1.32:5000/kirim_data"  # Alamat server MongoDB (misalnya menggunakan Flask)

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
        print("Status Code (Ubidots):", req.status_code)  # STA 201
        print("Response (Ubidots):", req.json())
    except Exception as e:
        print("[ERROR] Gagal mengirim data ke Ubidots:", e)

def send_data_to_mongodb(temp, hum):
    """Mengirim data sensor ke server MongoDB dalam format JSON."""
    payload = json.dumps({
        "temperature": temp,
        "kelembapan": hum
    })
    
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
            
            # Kirim data ke Ubidots dan MongoDB
            send_data_to_ubidots(temp, hum)
            send_data_to_mongodb(temp, hum)

        except OSError as e:
            print("[ERROR] Gagal membaca sensor.")
        
        time.sleep(5)  # Kirim data setiap 5 detik

if __name__ == '__main__':
    main()

