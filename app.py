from flask import Flask, request, Response, render_template, send_file
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Base URL configuration (Heroku ya manually set karoge)
BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")

# Video streaming route
@app.route('/stream/<path:filename>')
def stream_file(filename):
    file_path = os.path.join("uploads", filename)
    file_size = os.path.getsize(file_path)

    range_header = request.headers.get('Range', None)
    if not range_header:
        return send_file(file_path)

    byte1, byte2 = 0, None
    m = range_header.replace('bytes=', '').split('-')
    if len(m) == 2:
        byte1 = int(m[0])
        if m[1]:
            byte2 = int(m[1])

    length = file_size - byte1
    if byte2 is not None:
        length = byte2 - byte1 + 1

    with open(file_path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    rv = Response(data, 
                  206,
                  mimetype="video/mp4",
                  content_type="video/mp4",
                  direct_passthrough=True)
    rv.headers.add('Content-Range', f'bytes {byte1}-{byte1 + length - 1}/{file_size}')
    return rv

# Streaming page with player
@app.route('/watch/<path:filename>')
def watch(filename):
    stream_url = f"{BASE_URL}/stream/{filename}"
    return render_template("stream.html", stream_url=stream_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
