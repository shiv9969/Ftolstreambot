# --- app.py optimized by ChatGPT ---

import os
import asyncio
from flask import Flask, request, send_file, jsonify
from utils_bot import save_file_async, generate_link
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "biisal"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return jsonify({"message": "Bot is running!"})

@app.route('/upload', methods=['POST'])
async def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    await save_file_async(file, file_path)

    link = generate_link(file_path)
    return jsonify({"link": link})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filename = secure_filename(filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
