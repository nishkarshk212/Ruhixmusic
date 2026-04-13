import json
import os

STICKER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stickers.json")

def get_stickers():
    if not os.path.exists(STICKER_FILE):
        return {"stickers": [], "emojis": []}
    with open(STICKER_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"stickers": [], "emojis": []}

def save_sticker_id(sticker_id):
    data = get_stickers()
    if sticker_id not in data["stickers"]:
        data["stickers"].append(sticker_id)
        with open(STICKER_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return True
    return False

def save_emoji_id(emoji_id):
    data = get_stickers()
    if emoji_id not in data["emojis"]:
        data["emojis"].append(emoji_id)
        with open(STICKER_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return True
    return False

def get_random_sticker():
    import random
    data = get_stickers()
    if data["stickers"]:
        return random.choice(data["stickers"])
    return None

def get_random_emoji():
    import random
    data = get_stickers()
    if data["emojis"]:
        return random.choice(data["emojis"])
    return None
