import urllib.parse
import logging
from biisal.bot import StreamBot
from biisal.utils.file_properties import get_file_ids
from biisal.server.exceptions import InvalidHash
from biisal.vars import Var

async def render_page(id, secure_hash):
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(id))

    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message ID {id}")
        raise InvalidHash

    # Generate direct file URL
    direct_file_url = urllib.parse.urljoin(
        Var.URL, f"stream/{id}/{urllib.parse.quote_plus(file_data.file_name)}?hash={secure_hash}"
    )

    return direct_file_url  # Return direct file link instead of HTML 
