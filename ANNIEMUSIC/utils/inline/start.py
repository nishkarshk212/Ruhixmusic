from pyrogram.types import InlineKeyboardButton

import config
from ANNIEMUSIC import app


def start_panel(_):
    # Convert @username to https://t.me/username format for buttons
    support_channel = config.SUPPORT_CHANNEL
    if support_channel.startswith("@"):
        support_channel = f"https://t.me/{support_channel[1:]}"
    
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_11"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=support_channel),
        ],
    ]
    return buttons


def private_panel(_):
    # Convert @username to https://t.me/username format for buttons
    support_chat = config.SUPPORT_CHAT
    if support_chat.startswith("@"):
        support_chat = f"https://t.me/{support_chat[1:]}"
    
    support_channel = config.SUPPORT_CHANNEL
    if support_channel.startswith("@"):
        support_channel = f"https://t.me/{support_channel[1:]}"
    
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text=_["S_B_10"], user_id=config.OWNER_ID),
            InlineKeyboardButton(text=_["S_B_6"], url=support_chat),
        ],
        [
            InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper"),
        ],
    ]
    return buttons
