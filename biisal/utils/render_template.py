import aiohttp
import logging
from aiohttp import web
from biisal.bot import StreamBot
from biisal.utils.file_properties import get_file_ids
from biisal.server.exceptions import InvalidHash
from biisal.vars import Var

async def render_page(request):
    id = request.match_info.get("id")
    secure_hash = request.rel_url.query.get("hash")

    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(id))

    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message ID {id}")
        raise InvalidHash

    # Serve the video file directly instead of returning a text URL
    file_url = f"{Var.URL}/stream/{id}/{file_data.file_name}?hash={secure_hash}"
    
    return web.Response(
        body=f'<html><body><video controls autoplay><source src="{file_url}" type="video/mp4"></video></body></html>',
        content_type="text/html"
    ) 
