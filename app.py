import os
import uuid
import aiohttp
import asyncio
import aiofiles
from aiohttp import web
import subprocess

# Folders auto-create
os.makedirs("uploads", exist_ok=True)
os.makedirs("hls_output", exist_ok=True)

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.Response(text="Server is Running! Upload at /upload", content_type='text/html')

@routes.post('/upload')
async def upload(request):
    reader = await request.multipart()
    field = await reader.next()
    filename = field.filename

    if not filename:
        return web.Response(text="No file uploaded", status=400)

    # Save file to uploads
    unique_id = str(uuid.uuid4())
    save_path = f'uploads/{unique_id}_{filename}'

    async with aiofiles.open(save_path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            await f.write(chunk)

    # Start HLS conversion
    output_folder = f"hls_output/{unique_id}"
    os.makedirs(output_folder, exist_ok=True)
    hls_path = os.path.join(output_folder, "index.m3u8")

    ffmpeg_cmd = [
        "ffmpeg",
        "-i", save_path,
        "-preset", "veryfast",
        "-g", "48",
        "-sc_threshold", "0",
        "-map", "0",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:v", "1500k",
        "-b:a", "128k",
        "-hls_time", "4",
        "-hls_playlist_type", "vod",
        hls_path
    ]

    subprocess.run(ffmpeg_cmd)

    stream_url = f"/stream/{unique_id}"
    download_url = f"/download/{unique_id}"

    return web.json_response({"stream_url": stream_url, "download_url": download_url})

@routes.get('/stream/{video_id}')
async def stream(request):
    video_id = request.match_info['video_id']
    hls_file = f"hls_output/{video_id}/index.m3u8"

    if not os.path.exists(hls_file):
        return web.Response(text="Stream not found", status=404)

    return web.FileResponse('./templates/stream.html')

@routes.get('/hls/{video_id}/{file}')
async def hls_files(request):
    video_id = request.match_info['video_id']
    file = request.match_info['file']
    file_path = f"hls_output/{video_id}/{file}"

    if not os.path.exists(file_path):
        return web.Response(text="HLS File not found", status=404)

    return web.FileResponse(file_path)

@routes.get('/download/{video_id}')
async def download(request):
    video_id = request.match_info['video_id']
    for file in os.listdir('uploads'):
        if file.startswith(video_id):
            return web.FileResponse(path=f'uploads/{file}', headers={
                'Content-Disposition': f'attachment; filename="{file.split("_", 1)[-1]}"'
            })

    return web.Response(text="File not found", status=404)

@routes.get('/static/{filename}')
async def static_files(request):
    filename = request.match_info['filename']
    return web.FileResponse(f'static/{filename}')

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app, port=int(os.environ.get("PORT", 8080)))
