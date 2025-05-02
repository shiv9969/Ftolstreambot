from flask import Flask, render_template, send_file, request, abort
import os
from biisal.vars import Var  # Make sure Var.URL and Var.DATABASE_URL are correct

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Bisal_Files'

@app.route('/watch/<int:msg_id>/<filename>')
def watch_video(msg_id, filename):
    try:
        video_path = os.path.join("downloads", f"{msg_id}_{filename}")
        if not os.path.exists(video_path):
            return abort(404, description="File not found")

        return render_template("player.html", video_url=f"/video/{msg_id}/{filename}", filename=filename)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/video/<int:msg_id>/<filename>')
def stream_video(msg_id, filename):
    video_path = os.path.join("downloads", f"{msg_id}_{filename}")
    if not os.path.exists(video_path):
        return abort(404, description="Video not found")

    range_header = request.headers.get('Range', None)
    if not range_header:
        return send_file(video_path)

    try:
        size = os.path.getsize(video_path)
        byte1, byte2 = 0, None

        if range_header:
            match = range_header.replace('bytes=', '').split('-')
            byte1 = int(match[0])
            if len(match) == 2 and match[1]:
                byte2 = int(match[1])

        length = size - byte1
        with open(video_path, 'rb') as f:
            f.seek(byte1)
            data = f.read(length if byte2 is None else byte2 - byte1 + 1)

        rv = app.response_class(data,
                                status=206,
                                mimetype='video/mp4',
                                direct_passthrough=True)
        rv.headers.add('Content-Range', f'bytes {byte1}-{byte1 + len(data) - 1}/{size}')
        return rv
    except Exception as e:
        return f"Streaming error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
