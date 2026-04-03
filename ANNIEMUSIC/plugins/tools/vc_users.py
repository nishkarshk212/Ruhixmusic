from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ANNIEMUSIC import app
from ANNIEMUSIC.misc import SUDOERS
from ANNIEMUSIC.core.call import JARVIS
from ANNIEMUSIC.utils.database import group_assistant, is_active_chat


@app.on_message(filters.command(["vcusers", "voicechatusers", "vcmembers"], prefixes=["/", "!"]) & filters.group)
async def get_voice_chat_users(client: Client, message: Message):
    """Get list of all users currently in the voice chat with their names and IDs"""
    
    # Check if there's an active voice chat
    chat_id = message.chat.id
    
    # First check if bot is in an active voice chat
    is_active = await is_active_chat(chat_id)
    if not is_active:
        return await message.reply_text(
            "❌ No active voice chat in this group.\n"
            "Play some music first to use this command."
        )
    
    mystic = await message.reply_text("🔄 Getting voice chat participants...")
    
    try:
        # Get the assistant for this chat
        assistant = await group_assistant(JARVIS, chat_id)
        
        # Get participants from the voice chat
        participants = await assistant.get_participants(chat_id)
        
        if not participants or len(participants) == 0:
            return await mystic.edit_text(
                "📭 No participants found in the voice chat.\n"
                "This might happen if the bot just joined."
            )
        
        # Build the participants list
        text = f"🎤 <b>Voice Chat Participants</b>\n\n"
        text += f"👥 <b>Total Users:</b> {len(participants)}\n\n"
        text += f"<b>Users List:</b>\n"
        text += "━" * 30 + "\n"
        
        for i, participant in enumerate(participants, 1):
            user = participant.user
            user_name = user.first_name + (f" {user.last_name}" if user.last_name else "")
            user_id = user.id
            username = f"@{user.username}" if user.username else "No username"
            
            text += f"\n{i}. <b>{user_name}</b>\n"
            text += f"   └─ 🆔 <code>{user_id}</code>\n"
            text += f"   └─ 📛 @{username}\n"
        
        text += "\n" + "━" * 30
        
        # Add button to close
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✯ Close ✯", callback_data="close")]]
        )
        
        await mystic.edit_text(text, reply_markup=keyboard)
        
    except Exception as e:
        error_msg = f"❌ Error getting participants: {type(e).__name__}"
        await mystic.edit_text(error_msg)
