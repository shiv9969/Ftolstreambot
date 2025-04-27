from flask import Flask, request, render_template, send_from_directory
import os
from utils_bot import generate_hls

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
HLS_FOLDER = 'hls_output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HLS_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        filepath = os.path.join(UPLOAD_FOLDER, f.filename)
        f.save(filepath)
        video_id = os.path.splitext(f.filename)[0]
        generate_hls(filepath, video_id)
        return f"File Uploaded. Stream Link: /stream/{video_id}"
    return '''
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/stream/<video_id>')
def stream_video(video_id):
    return render_template('stream.html', video_id=video_id)

@app.route('/hls/<path:filename>')
def serve_hls(filename):
    return send_from_directory(HLS_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
