import os
import subprocess

HLS_FOLDER = 'hls_output'

def generate_hls(filepath, video_id):
    output_dir = os.path.join(HLS_FOLDER, video_id)
    os.makedirs(output_dir, exist_ok=True)
    
    command = [
        'ffmpeg', '-i', filepath,
        '-filter:v', "scale=w=1280:h=720:force_original_aspect_ratio=decrease",
        '-c:a', 'aac', '-ar', '48000',
        '-c:v', 'h264', '-profile:v', 'main', '-crf', '20', '-sc_threshold', '0',
        '-g', '48', '-keyint_min', '48',
        '-hls_time', '4', '-hls_playlist_type', 'vod',
        '-b:v', '1500k',
        '-maxrate', '2679k', '-bufsize', '4000k',
        '-b:a', '128k',
        '-hls_segment_filename', os.path.join(output_dir, 'segment_%03d.ts'),
        os.path.join(output_dir, 'master.m3u8')
    ]
    subprocess.run(command) 
