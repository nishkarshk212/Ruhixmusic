from pyrogram import filters, enums
from pyrogram.types import Message
from ANNIEMUSIC import app
from ANNIEMUSIC.utils.stickers import save_sticker_id, save_emoji_id, get_stickers
from ANNIEMUSIC.misc import SUDOERS
import logging

# Set up logging
logger = logging.getLogger(__name__)

@app.on_message(filters.private & SUDOERS)
async def sticker_debug_handler(client, message: Message):
    """Debug handler to log and save sticker/emoji details in private messages (Sudo/Owner Only)"""
    
    if message.sticker:
        sticker = message.sticker
        
        # Determine sticker type
        if sticker.is_video:
            sticker_type = "video"
        elif sticker.is_animated:
            sticker_type = "animated"
        else:
            sticker_type = "static"
        
        # Check if premium (using hasattr for safety)
        is_premium = getattr(sticker, 'premium_animation', None) is not None
        
        # Auto-save sticker to separate file
        saved = save_sticker_id(sticker.file_id)
        
        # Build detailed information message
        info_text = f"""
🎨 **STICKER DETAILS & SAVED** 🎨

📋 **Basic Info:**
• File ID: `{sticker.file_id}`
• Unique ID: `{sticker.file_unique_id}`
• Set Name: `{sticker.set_name or 'N/A'}`

🎭 **Type:**
• Type: {sticker_type.upper()}
• Static: {not sticker.is_animated and not sticker.is_video}
• Animated: {sticker.is_animated}
• Video: {sticker.is_video}

📏 **Dimensions:**
• Width: {sticker.width}px
• Height: {sticker.height}px
• File Size: {sticker.file_size or 0} bytes

🎬 **Premium Info:**
• Is Premium: {is_premium}

✨ **Emoji:**
• Associated Emoji: `{sticker.emoji or 'N/A'}`

💾 **Storage:**
• Status: {"✅ Saved to stickers.json" if saved else "ℹ️ Already in storage"}
"""
        # Send info to user
        await message.reply_text(info_text, parse_mode=enums.ParseMode.MARKDOWN)

    # Check for custom emojis in message entities
    if message.entities:
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.CUSTOM_EMOJI:
                emoji_id = entity.custom_emoji_id
                saved = save_emoji_id(emoji_id)
                
                info_text = f"""
✨ **CUSTOM EMOJI DETAILS & SAVED** ✨

📋 **Basic Info:**
• Custom Emoji ID: `{emoji_id}`

💾 **Storage:**
• Status: {"✅ Saved to stickers.json" if saved else "ℹ️ Already in storage"}
"""
                await message.reply_text(info_text, parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.command("savedids") & SUDOERS)
async def view_saved_ids(client, message: Message):
    data = get_stickers()
    stickers = data.get("stickers", [])
    emojis = data.get("emojis", [])
    
    text = f"📦 **SAVED STICKER & EMOJI IDS** 📦\n\n"
    text += f"🖼 **Stickers ({len(stickers)}):**\n"
    for sid in stickers[-10:]: # Show last 10
        text += f"• `{sid}`\n"
    
    text += f"\n✨ **Emojis ({len(emojis)}):**\n"
    for eid in emojis[-10:]: # Show last 10
        text += f"• `{eid}`\n"
    
    text += f"\nUse `/testsaved` to see a random saved sticker/emoji."
    await message.reply_text(text)

@app.on_message(filters.command("testsaved") & SUDOERS)
async def test_saved_ids(client, message: Message):
    from ANNIEMUSIC.utils.stickers import get_random_sticker, get_random_emoji
    import random
    
    choice = random.choice(["sticker", "emoji"])
    if choice == "sticker":
        sid = get_random_sticker()
        if sid:
            await client.send_sticker(message.chat.id, sid)
        else:
            await message.reply_text("No stickers saved yet!")
    else:
        eid = get_random_emoji()
        if eid:
            # Send as a sticker because custom emojis are technically stickers in some contexts
            try:
                await client.send_sticker(message.chat.id, eid)
            except:
                await message.reply_text(f"Emoji ID: `{eid}` (cannot send directly)")
        else:
            await message.reply_text("No emojis saved yet!")
