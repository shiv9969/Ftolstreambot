# --- utils_bot.py optimized for Heroku env ---

import os
import aiofiles

FQDN = os.getenv("FQDN") or "https://your-default-app-name.herokuapp.com"

async def save_file_async(file_storage, destination_path):
    """Save uploaded file asynchronously to disk."""
    async with aiofiles.open(destination_path, 'wb') as f:
        while True:
            chunk = file_storage.stream.read(4096)
            if not chunk:
                break
            await f.write(chunk)

def generate_link(file_path):
    """Generate downloadable link based on filename."""
    filename = os.path.basename(file_path)
    return f"{FQDN}/download/{filename}"
