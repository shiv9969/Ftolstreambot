import logging
import urllib.parse
from aiohttp import web
return web.HTTPFound(direct_file_url)
from biisal.bot import StreamBot
from biisal.utils.file_properties import get_file_ids
from biisal.server.exceptions import InvalidHash
from biisal.vars import Var

async def render_page(id: str, secure_hash: str):
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(id))

    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message ID {id}")
        raise InvalidHash

    # Generate direct file URL
    direct_file_url = f"{Var.URL}/stream/{id}/{urllib.parse.quote_plus(file_data.file_name)}?hash={secure_hash}"

    # Redirect user directly to the file for streaming
    return RedirectResponse(url=direct_file_url)
