from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# Configure Upload Folder
UPLOAD_FOLDER = "results"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    file.save(filepath)  # Save the image

    return jsonify({"message": "Upload successful", "saved_as": filename})

# =======================
# 📌 Serve Uploaded Files
# =======================
@app.route("/results/<filename>")
def get_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

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
