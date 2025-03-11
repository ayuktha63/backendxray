from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # Import CORS
import os
import cv2
import torch
from ultralytics import YOLO  # YOLOv8

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes

# Configure Upload and Results Folders
UPLOAD_FOLDER = "uploads"  # Change this to 'uploads'
RESULTS_FOLDER = "results"  # Use 'results' for processed images

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULTS_FOLDER"] = RESULTS_FOLDER

# ✅ Load YOLO model
MODEL_PATH = "weights.pt"
model = YOLO(MODEL_PATH)  # Load YOLO model

def process_image(input_path, output_path):
    """Run YOLO model on input image and save labeled output."""
    results = model(input_path)  # Run inference

    for result in results:
        img = result.plot()  # Get labeled image with bounding boxes
        cv2.imwrite(output_path, img)  # Save to results folder

# =======================
# 📌 Upload Image Route
# =======================
@app.route("/upload", methods=["POST"])
def upload_file():
    if "image" not in request.files:
        return jsonify({"error": "No image found"}), 400

    file = request.files["image"]
    name = request.form.get("name", "unknown")
    age = request.form.get("age", "0")
    gender = request.form.get("gender", "unknown")

    filename = f"{name}_{age}_{gender}.png"
    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # Save the original image to "uploads"
    file.save(upload_path)

    # Process image using YOLO model and save to "results"
    result_filename = f"processed_{filename}"
    result_path = os.path.join(app.config["RESULTS_FOLDER"], result_filename)
    process_image(upload_path, result_path)  # Process image with YOLO

    return jsonify({
        "message": "Upload successful, image processed",
        "saved_as": filename,
        "processed_as": result_filename
    })

# =======================
# 📌 Serve Processed Files
# =======================
@app.route("/results/<filename>")
def get_file(filename):
    return send_from_directory(app.config["RESULTS_FOLDER"], filename)

# =======================
# 📌 Health Check Route
# =======================
@app.route("/")
def home():
    return jsonify({"status": "Backend is running!"})

# =======================
# 📌 Run Flask App
# =======================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5050))  # Get PORT from environment, default to 5050
    app.run(debug=True, host="0.0.0.0", port=port)  # Bind to 0.0.0.0 for external access
