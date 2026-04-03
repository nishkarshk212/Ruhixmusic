from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ANNIEMUSIC import LOGGER, app
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
        try:
            participants = await assistant.get_participants(chat_id)
            
            if not participants or len(participants) == 0:
                return await mystic.edit_text(
                    "📭 No participants found in the voice chat.\n\n"
                    "💡 This might happen if:\n"
                    "• The bot just joined\n"
                    "• Voice chat is empty\n"
                    "• Assistant isn't actually in the VC"
                )
            
            # Build the participants list
            text = f"🎤 <b>Voice Chat Participants</b>\n\n"
            text += f"👥 <b>Total Users:</b> {len(participants)}\n\n"
            text += f"<b>Users List:</b>\n"
            text += "━" * 30 + "\n"
            
            for i, participant in enumerate(participants, 1):
                # Safely access participant attributes - PyTgCalls uses 'peer' or direct attributes
                try:
                    # Try different attribute patterns based on PyTgCalls version
                    if hasattr(participant, 'peer'):
                        # Newer PyTgCalls versions use peer.id
                        user_id = participant.peer.id
                        user_name = participant.username or f"User_{user_id}"
                        username = f"@{participant.username}" if participant.username else "No username"
                    elif hasattr(participant, 'id'):
                        # Some versions have direct id
                        user_id = participant.id
                        user_name = getattr(participant, 'username', None) or f"User_{user_id}"
                        username = f"@{participant.username}" if hasattr(participant, 'username') and participant.username else "No username"
                    elif hasattr(participant, 'user'):
                        # Fallback to old .user attribute
                        user = participant.user
                        user_name = user.first_name + (f" {user.last_name}" if user.last_name else "")
                        user_id = user.id
                        username = f"@{user.username}" if user.username else "No username"
                    else:
                        # Last resort - try to get any ID-like attribute
                        user_id = getattr(participant, 'chat_id', getattr(participant, 'channel_id', 'Unknown'))
                        user_name = f"User_{user_id}"
                        username = "Unknown"
                    
                    text += f"\n{i}. <b>{user_name}</b>\n"
                    text += f"   └─ 🆔 <code>{user_id}</code>\n"
                    text += f"   └─ 📛 @{username}\n"
                except Exception as attr_err:
                    LOGGER(__name__).warning(f"Could not get user info for participant {i}: {attr_err} - Type: {type(participant)}")
                    # Try to at least show something
                    try:
                        user_id = str(getattr(participant, 'peer', getattr(participant, 'id', 'Unknown')))
                        text += f"\n{i}. <b>User_{user_id}</b>\n"
                        text += f"   └─ 🆔 <code>{user_id}</code>\n"
                    except:
                        text += f"\n{i}. <b>Unknown Participant</b>\n"
                    continue  # Continue with other participants
            
            text += "\n" + "━" * 30
            
            # Add button to close
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("✯ Close ✯", callback_data="close")]]
            )
            
            await mystic.edit_text(text, reply_markup=keyboard)
            
        except Exception as vc_error:
            error_type = type(vc_error).__name__
            
            # Handle specific error types
            if "NotInCallError" in error_type or "not in a call" in str(vc_error).lower():
                await mystic.edit_text(
                    "❌ Assistant is not in the voice chat!\n\n"
                    "💡 To fix this:\n"
                    "1. Make sure there's an active voice chat\n"
                    "2. Play music to make the assistant join\n"
                    "3. Then try /vcusers again"
                )
            elif "AttributeError" in error_type:
                await mystic.edit_text(
                    "⚠️ Error reading participant data\n\n"
                    "This usually means the assistant isn't properly connected to the voice chat.\n\n"
                    "💡 Try playing music first, then use this command again."
                )
            else:
                await mystic.edit_text(
                    f"❌ Error: {error_type}\n\n"
                    f"Details: {str(vc_error)}\n\n"
                    "Make sure the assistant is in the voice chat and it's active."
                )
        
    except Exception as e:
        await mystic.edit_text(
            f"❌ Failed to connect to assistant: {type(e).__name__}\n"
            f"Details: {str(e)}\n\n"
            "Make sure the assistant is added to your group."
        )
