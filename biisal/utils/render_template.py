import logging
import urllib.parse
from aiohttp import web
from biisal.bot import StreamBot
from biisal.utils.file_properties import get_file_ids
from biisal.vars import Var

async def render_page(request: web.Request):
    # Extract query parameters
    id = request.match_info.get("id")
    secure_hash = request.rel_url.query.get("hash")

    if not id or not secure_hash:
        return web.Response(text="Invalid request parameters", status=400)

    # Get file data
    try:
        file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(id))
    except Exception as e:
        logging.error(f"Error fetching file data: {e}")
        return web.Response(text="File not found", status=404)

    # Validate file hash
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message ID {id}")
        return web.Response(text="Invalid hash", status=403)

    # Generate direct file URL
    direct_file_url = f"{Var.URL}/stream/{id}/{urllib.parse.quote_plus(file_data.file_name)}?hash={secure_hash}"

    # Redirect user to the direct file URL
    return web.HTTPFound(direct_file_url) 
