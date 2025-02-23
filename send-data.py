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
