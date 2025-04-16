from flask import Flask, request
from pymongo import MongoClient
import gridfs
import numpy as np
import cv2
from ultralytics import YOLO
from datetime import datetime

flask_app = Flask(__name__)

# MongoDB setup
MONGO_URI = "mongodb+srv://khalisazhrm:0S2Gxq0KFj93ZDU3@sigma.kykmvmz.mongodb.net/?retryWrites=true&w=majority&appName=SIGMA"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["esp_images"]
fs = gridfs.GridFS(db)

model = YOLO("yolov8n.pt")

@flask_app.route('/upload', methods=['POST'])
def upload_image():
    if not request.data:
        return "No image data received", 400
    image_bytes = request.data
    if len(image_bytes) < 1000:
        return "Image too small or corrupted", 400
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        results = model(img)
        detected_ids = results[0].boxes.cls.int().tolist()
        class_names = results[0].names
        label_str = "_".join(sorted(set([class_names[i] for i in detected_ids]))) if detected_ids else "unknown"
        filename = f"image_detected_{label_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        fs.put(image_bytes, filename=filename, content_type='image/jpeg')
        print(f"[✔] Uploaded to MongoDB: {filename}")
        return f"Image received and detected as: {label_str}", 200
    except Exception as e:
        print(f"[❌] Error processing image: {e}")
        return "Internal server error", 500

def run_flask():
    flask_app.run(host='0.0.0.0', port=5000)
