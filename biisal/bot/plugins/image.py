from telegraph import upload_file

async def upload_to_telegraph(file_path):
    """Uploads an image to Telegraph and returns the link."""
    try:
        response = upload_file(file_path)
        return f"https://telegra.ph{response[0]}"
    except Exception as e:
        return f"Error: {e}"
