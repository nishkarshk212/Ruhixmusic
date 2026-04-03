from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ANNIEMUSIC import LOGGER, app
from ANNIEMUSIC.misc import SUDOERS
from ANNIEMUSIC.core.call import JARVIS
from ANNIEMUSIC.utils.database import group_assistant


@app.on_message(filters.command(["vcusers", "voicechatusers", "vcmembers"], prefixes=["/", "!"]) & filters.group)
async def get_voice_chat_users(client: Client, message: Message):
    """Get list of all users currently in the voice chat with their names and IDs"""
    
    chat_id = message.chat.id
    mystic = await message.reply_text("🔄 Getting voice chat participants...")
    
    try:
        assistant = await group_assistant(JARVIS, chat_id)
        
        # Try to get participants - this proves assistant is in VC
        try:
            participants = await assistant.get_participants(chat_id)
        except Exception as vc_error:
            error_type = type(vc_error).__name__
            if "NotInCallError" in str(error_type) or "not in a call" in str(vc_error).lower():
                return await mystic.edit_text(
                    "❌ Assistant is not in the voice chat!\n\n"
                    "💡 To fix this:\n"
                    "1. Make sure there's an active voice chat\n"
                    "2. Play music to make the assistant join\n"
                    "3. Then try /vcusers again"
                )
            else:
                return await mystic.edit_text(
                    f"❌ Error accessing voice chat: {error_type}\n\n"
                    "Make sure the assistant is added to your group and has permission to join voice chats."
                )
        
        # If we got here, we have participants! Build the list
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
            # Safely access participant attributes - Multiple PyTgCalls API versions supported
            try:
                # YOUR VERSION: Uses user_id directly (ntgcalls/newer PyTgCalls)
                if hasattr(participant, 'user_id'):
                    user_id = participant.user_id
                    user_name = f"User {user_id}"
                    username = "In Voice Chat"
                
                # Newer PyTgCalls versions use peer.id
                elif hasattr(participant, 'peer'):
                    user_id = participant.peer.id
                    user_name = participant.username or f"User_{user_id}"
                    username = f"@{participant.username}" if participant.username else "No username"
                
                # Some versions have direct id
                elif hasattr(participant, 'id'):
                    user_id = participant.id
                    user_name = getattr(participant, 'username', None) or f"User_{user_id}"
                    username = f"@{participant.username}" if hasattr(participant, 'username') and participant.username else "No username"
                
                # Fallback to old .user attribute
                elif hasattr(participant, 'user'):
                    user = participant.user
                    user_name = user.first_name + (f" {user.last_name}" if user.last_name else "")
                    user_id = user.id
                    username = f"@{user.username}" if user.username else "No username"
                
                # Last resort
                else:
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
                    if hasattr(participant, 'user_id'):
                        user_id = participant.user_id
                        text += f"\n{i}. <b>User {user_id}</b>\n"
                        text += f"   └─ 🆔 <code>{user_id}</code>\n"
                        text += f"   └─ 📛 In Voice Chat\n"
                    else:
                        text += f"\n{i}. <b>Unknown Participant</b>\n"
                except:
                    text += f"\n{i}. <b>Unknown Participant</b>\n"
                continue
        
        text += "\n" + "━" * 30
        
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✯ Close ✯", callback_data="close")]]
        )
        
        await mystic.edit_text(text, reply_markup=keyboard)
        
    except Exception as e:
        await mystic.edit_text(
            f"❌ Failed to connect to assistant: {type(e).__name__}\n"
            f"Details: {str(e)}\n\n"
            "Make sure the assistant is added to your group."
        )
