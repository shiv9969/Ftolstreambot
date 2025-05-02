from flask import Flask, render_template, request, send_file
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Bisal_Files'

@app.route('/watch/<int:msg_id>/<filename>')
def watch(msg_id, filename):
    file_url = f"https://api.telegram.org/file/bot{os.environ['BOT_TOKEN']}/{msg_id}/{filename}"
    return render_template('player.html', video_url=file_url, filename=filename)
