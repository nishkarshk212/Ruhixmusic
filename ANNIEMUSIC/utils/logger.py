from pyrogram.enums import ParseMode

from ANNIEMUSIC import app
from ANNIEMUSIC.utils.database import is_on_off
from config import LOGGER_ID
import asyncio

# Cache to prevent duplicate log messages within short time periods
_log_cache = {}
_cache_timeout = 2  # seconds


async def play_logs(message, streamtype):
    if await is_on_off(2):
        # Create a unique key for this message to prevent duplicates
        cache_key = f"{message.from_user.id}_{message.chat.id}_{message.text}_{streamtype}"
        
        # Check if we've logged this exact action recently
        if cache_key in _log_cache:
            last_log_time = _log_cache[cache_key]
            if (asyncio.get_event_loop().time() - last_log_time) < _cache_timeout:
                return  # Skip duplicate log
        
        # Cache this log
        _log_cache[cache_key] = asyncio.get_event_loop().time()
        
        # Clean old cache entries periodically
        if len(_log_cache) > 100:
            current_time = asyncio.get_event_loop().time()
            _log_cache = {
                k: v for k, v in _log_cache.items() 
                if (current_time - v) < _cache_timeout * 10
            }
        
        logger_text = f"""
<b>{app.mention} ᴘʟᴀʏ ʟᴏɢ</b>

<b>ᴄʜᴀᴛ ɪᴅ :</b> <code>{message.chat.id}</code>
<b>ᴄʜᴀᴛ ɴᴀᴍᴇ :</b> {message.chat.title}
<b>ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.chat.username}

<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>
<b>ɴᴀᴍᴇ :</b> {message.from_user.mention}
<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}

<b>ǫᴜᴇʀʏ :</b> {message.text.split(None, 1)[1]}
<b>sᴛʀᴇᴀᴍᴛʏᴘᴇ :</b> {streamtype}"""
        if message.chat.id != LOGGER_ID:
            try:
                await app.send_message(
                    chat_id=LOGGER_ID,
                    text=logger_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except:
                pass
        return
