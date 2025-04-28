import os
from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import subprocess

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount static folders
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/hls_output", StaticFiles(directory="hls_output"), name="hls_output")


# Upload page
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


# Upload and convert
@app.post("/upload")
async def upload_file(file: UploadFile):
    upload_path = f"uploads/{file.filename}"
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create HLS output
    output_folder = "hls_output"
    output_filename = os.path.splitext(file.filename)[0]
    output_path = f"{output_folder}/{output_filename}.m3u8"

    # Run ffmpeg command
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", upload_path,
        "-profile:v", "baseline",
        "-level", "3.0",
        "-start_number", "0",
        "-hls_time", "10",
        "-hls_list_size", "0",
        "-f", "hls",
        output_path
    ]
    subprocess.run(ffmpeg_cmd)

    return {"message": "Upload and conversion done!", "watch_url": f"/watch/{output_filename}"}


# Watch video route
@app.get("/watch/{filename}", response_class=HTMLResponse)
async def watch_video(request: Request, filename: str):
    stream_url = f"/hls_output/{filename}.m3u8"
    return templates.TemplateResponse("stream.html", {"request": request, "stream_url": stream_url})


