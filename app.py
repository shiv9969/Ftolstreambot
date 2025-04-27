from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/stream/<path:filename>')
def stream(filename):
    stream_url = f"https://your-cdn-or-server-link/{filename}"  # Update as per your hosting
    return render_template('stream.html', stream_url=stream_url)


if __name__ == "__main__":
    app.run()
