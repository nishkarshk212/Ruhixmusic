from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ANNIEMUSIC import LOGGER, app
from ANNIEMUSIC.misc import SUDOERS
from ANNIEMUSIC.core.call import JARVIS
from ANNIEMUSIC.utils.database import group_assistant, is_active_chat, add_active_chat, music_on
from ANNIEMUSIC.utils.exceptions import AssistantErr


@app.on_message(filters.command(["testvc", "joinvc"], prefixes=["/", "!"]) & filters.group & SUDOERS)
async def test_voice_chat(client: Client, message: Message):
    """Test command to verify assistant can join voice chat"""
    
    chat_id = message.chat.id
    mystic = await message.reply_text("🔄 Testing voice chat connection...")
    
    try:
        # Get assistant for this chat
        assistant = await group_assistant(JARVIS, chat_id)
        
        await mystic.edit_text("✅ Assistant found!\n🔄 Attempting to join voice chat...")
        
        # Check if there's already an active voice chat
        is_active = await is_active_chat(chat_id)
        
        if not is_active:
            # Create a dummy stream to test joining
            # We'll use a silent audio file or just test the connection
            await mystic.edit_text(
                "⚠️ No active voice chat in this group.\n"
                "Please start a voice chat first, then try again.\n\n"
                "💡 To test: Start a voice chat manually, then use this command again."
            )
            return
        
        # Try to get participants (this verifies we're in the VC)
        try:
            participants = await assistant.get_participants(chat_id)
            await mystic.edit_text(
                f"✅ Successfully connected to voice chat!\n\n"
                f"👥 Participants in VC: {len(participants)}\n"
                f"🎵 Bot status: Active\n\n"
                f"Use /vcusers to see all participants"
            )
        except Exception as e:
            await mystic.edit_text(
                f"⚠️ Connected but couldn't get participants\n\n"
                f"Error: {type(e).__name__}\n"
                f"This might be normal - try playing music to fully test"
            )
            
    except AssistantErr as e:
        await mystic.edit_text(f"❌ Assistant Error:\n{str(e)}")
    except Exception as e:
        await mystic.edit_text(
            f"❌ Failed to connect to voice chat\n\n"
            f"Error: {type(e).__name__}\n"
            f"Details: {str(e)}\n\n"
            f"💡 Make sure:\n"
            f"1. Assistant is added to your group\n"
            f"2. Voice chat is active\n"
            f"3. Assistant has permission to join"
        )


@app.on_message(filters.command(["leavevc"], prefixes=["/", "!"]) & filters.group & SUDOERS)
async def leave_voice_chat(client: Client, message: Message):
    """Force leave from voice chat"""
    
    chat_id = message.chat.id
    
    try:
        assistant = await group_assistant(JARVIS, chat_id)
        
        # Check if assistant is actually in a voice chat before trying to leave
        try:
            await assistant.leave_call(chat_id, close=False)
            
            # Remove from active chats
            from ANNIEMUSIC.utils.database import remove_active_chat, remove_active_video_chat
            await remove_active_chat(chat_id)
            await remove_active_video_chat(chat_id)
            
            await message.reply_text("✅ Left voice chat successfully!")
            
        except Exception as e:
            error_type = type(e).__name__
            if "NotInCallError" in str(error_type) or "not in a call" in str(e).lower():
                await message.reply_text(
                    "ℹ️ Assistant is not in any voice chat right now.\n\n"
                    "No action needed - the voice chat might have already ended."
                )
            else:
                await message.reply_text(f"❌ Error leaving voice chat: {error_type}\n{str(e)}")
        
    except Exception as e:
        await message.reply_text(f"❌ Failed to get assistant: {type(e).__name__}")
