import os
import shutil
import uuid
import asyncio
from aiohttp import web

app = web.Application()

# Static folder serve
app.router.add_static('/static/', path=os.path.join(os.getcwd(), 'static'), name='static')

# Favicon route (optional)
async def favicon(request):
    return web.FileResponse(os.path.join(os.getcwd(), 'static', 'favicon.ico'))
app.router.add_get('/favicon.ico', favicon)

# Home page (upload form)
async def home(request):
    return web.Response(text="""
        <html>
            <head><title>Upload File</title></head>
            <body>
                <h1>Upload Video</h1>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" multiple>
                    <input type="submit" value="Upload">
                </form>
            </body>
        </html>
    """, content_type='text/html')

app.router.add_get('/', home)

# Upload route
async def upload(request):
    reader = await request.multipart()
    while True:
        field = await reader.next()
        if field is None:
            break
        if field.name == 'file':
            filename = field.filename
            save_path = os.path.join('uploads', filename)
            with open(save_path, 'wb') as f:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)
            # After upload, start HLS conversion
            await convert_to_hls(save_path)
    return web.Response(text="Uploaded and Converted Successfully! Go to /stream/filename_without_extension")

app.router.add_post('/upload', upload)

# Convert video to HLS
async def convert_to_hls(input_file):
    folder_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join('hls_output', folder_name)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'index.m3u8')

    cmd = f"ffmpeg -i \"{input_file}\" -preset veryfast -g 48 -sc_threshold 0 -map 0:v:0 -map 0:a:0 -b:v:0 2500k -maxrate:v:0 2675k -bufsize:v:0 3750k -b:a:0 128k -hls_time 4 -hls_playlist_type vod -hls_segment_filename \"{output_dir}/file%03d.ts\" \"{output_path}\""
    process = await asyncio.create_subprocess_shell(cmd)
    await process.communicate()

# Stream page
async def stream_page(request):
    video_id = request.match_info['video_id']
    index_file = f'hls_output/{video_id}/index.m3u8'
    if not os.path.exists(index_file):
        return web.Response(text="Video not found.", status=404)
    
    html_content = f"""
    <html>
    <head>
      <link href="/static/video-js.css" rel="stylesheet">
    </head>
    <body style="background-color: black;">
      <video id="video" class="video-js vjs-default-skin" controls autoplay width="100%" height="auto">
        <source src="/hls/{video_id}/index.m3u8" type="application/x-mpegURL">
      </video>

      <script src="/static/video.min.js"></script>
      <script src="/static/hls.min.js"></script>
      <script>
        var video = document.getElementById('video');
        if (Hls.isSupported()) {
            var hls = new Hls();
            hls.loadSource(video.querySelector('source').src);
            hls.attachMedia(video);
        }
        else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = video.querySelector('source').src;
        }
      </script>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

app.router.add_get('/stream/{video_id}', stream_page)

# Serve HLS files (m3u8 and ts)
async def hls_handler(request):
    path = request.match_info['path']
    file_path = os.path.join('hls_output', path)
    if not os.path.exists(file_path):
        return web.Response(text="Not found.", status=404)
    return web.FileResponse(file_path)

app.router.add_get('/hls/{path:.+}', hls_handler)

# Run app
if __name__ == '__main__':
    web.run_app(app, port=int(os.environ.get('PORT', 5000)))
