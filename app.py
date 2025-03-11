from flask import Flask, request, jsonify, send_from_directory
import os
import cv2
import torch
from flask_cors import CORS
from ultralytics import YOLO  # YOLOv8
import numpy as np

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
RESULTS_FOLDER = "results"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULTS_FOLDER"] = RESULTS_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# ✅ Load YOLO model
MODEL_PATH = "weights.pt"
model = YOLO(MODEL_PATH)  # Load YOLO model

def process_image(input_path, output_path):
    """Run YOLO model on input image and save labeled output."""
    results = model(input_path)  # Run inference

    for result in results:
        img = result.plot()  # Get labeled image with bounding boxes
        cv2.imwrite(output_path, img)  # Save to results folder

@app.route("/upload", methods=["POST"])
def upload_file():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    name = request.form.get("name", "Unknown").replace(" ", "_")
    age = request.form.get("age", "Unknown")
    gender = request.form.get("gender", "Unknown")

    filename = f"{name}_{age}_{gender}.png"

    # Save original image to "uploads"
    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(upload_path)

    # Process image using YOLO model and save to "results"
    result_path = os.path.join(app.config["RESULTS_FOLDER"], filename)
    process_image(upload_path, result_path)

    return jsonify({
        "message": "Image uploaded and processed",
        "uploaded_filename": filename,
        "processed_filename": filename
    })

# ✅ Serve original images from "uploads" folder
@app.route("/uploads/<path:filename>")
def get_uploaded_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ✅ Serve processed images from "results" folder
@app.route("/results/<path:filename>")
def get_processed_image(filename):
    return send_from_directory(app.config["RESULTS_FOLDER"], filename)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5050))  # Get PORT from environment, default to 5050
    app.run(debug=True, host="0.0.0.0", port=port)  # Bind to 0.0.0.0 for external access
