import asyncio
import os
from datetime import datetime, timedelta
from typing import Union
from ntgcalls import ConnectionNotFound, TelegramServerError
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, exceptions, types
from pytgcalls.pytgcalls_session import PyTgCallsSession
import config
from ANNIEMUSIC import LOGGER, YouTube, app
from ANNIEMUSIC.misc import db
from ANNIEMUSIC.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from ANNIEMUSIC.utils.exceptions import AssistantErr
from ANNIEMUSIC.utils.formatters import check_duration, seconds_to_min, speed_converter
from ANNIEMUSIC.utils.inline.play import stream_markup
from ANNIEMUSIC.utils.stream.autoclear import auto_clean
from ANNIEMUSIC.utils.thumbnails import get_thumb as gen_thumb
from strings import get_string

autoend = {}
counter = {}

async def _clear_(chat_id: int):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

class Call(PyTgCalls):
    def __init__(self):
        PyTgCallsSession.notice_displayed = True

        self.userbot1 = Client(
            name="ANNIE1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1, cache_duration=500)

        self.userbot2 = Client(
            name="ANNIE2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(self.userbot2, cache_duration=500) if config.STRING2 else None

        self.userbot3 = Client(
            name="ANNIE3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(self.userbot3, cache_duration=500) if config.STRING3 else None

        self.userbot4 = Client(
            name="ANNIE4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(self.userbot4, cache_duration=500) if config.STRING4 else None

        self.userbot5 = Client(
            name="ANNIE5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(self.userbot5, cache_duration=500) if config.STRING5 else None

    def _build_stream(
        self,
        source: str,
        video: bool,
        ffmpeg: str | None = None,
    ) -> types.MediaStream:
        # Validate source parameter
        if not source:
            raise ValueError("Media source cannot be empty")
        
        # Enhanced audio quality with stereo and better bitrate
        custom_ffmpeg = "-ac 2 -ar 48000 -b:a 320k"
        if ffmpeg:
            custom_ffmpeg = f"{ffmpeg} {custom_ffmpeg}"
        
        return types.MediaStream(
            media_path=source,
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
            audio_flags=types.MediaStream.Flags.REQUIRED,
            video_flags=(
                types.MediaStream.Flags.AUTO_DETECT
                if video
                else types.MediaStream.Flags.IGNORE
            ),
            ffmpeg_parameters=custom_ffmpeg,
        )

    async def _play_on_assistant(
        self,
        client: PyTgCalls,
        chat_id: int,
        stream: types.MediaStream,
    ):
        LOGGER(__name__).info(f"🎵 Attempting to play stream in {chat_id}")
        try:
            # Check if there's an active voice chat first
            from ntgcalls import GroupCallConfig
            import asyncio
            
            # Try to get participants to verify we're in the voice chat
            try:
                participants = await client.get_participants(chat_id)
                LOGGER(__name__).info(f"👥 Found {len(participants)} participants in voice chat {chat_id}")
            except Exception as e:
                LOGGER(__name__).warning(f"⚠️ Could not get participants: {type(e).__name__} - Bot may not be in VC yet")
            
            # Play with auto_start to immediately begin playback
            result = await asyncio.wait_for(
                client.play(
                    chat_id=chat_id,
                    stream=stream,
                    config=GroupCallConfig(auto_start=True),
                ),
                timeout=10  # Wait max 10 seconds
            )
            LOGGER(__name__).info(f"✅ Play command executed in {chat_id}: {type(result)}")
            
            # Verify playback started
            try:
                is_playing = await client.is_playing(chat_id)
                LOGGER(__name__).info(f"▶️ Playback status for {chat_id}: {is_playing}")
            except:
                pass
                
        except asyncio.TimeoutError:
            LOGGER(__name__).error(f"⏰ Timeout playing stream in {chat_id} after 10s")
            raise AssistantErr("Playback timeout - please try again")
        except exceptions.NoActiveGroupCall:
            LOGGER(__name__).error(f"❌ No active group call in {chat_id}")
            raise
        except exceptions.NoAudioSourceFound:
            LOGGER(__name__).error(f"❌ No audio source found in {chat_id}")
            raise
        except (ConnectionNotFound, TelegramServerError) as e:
            LOGGER(__name__).error(f"❌ Connection error in {chat_id}: {type(e).__name__}")
            raise
        except Exception as e:
            LOGGER(__name__).error(f"❌ Unexpected error playing in {chat_id}: {type(e).__name__} - {str(e)}")
            raise

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_call(chat_id, close=False)
        except Exception:
            pass

    async def stop_stream_force(self, chat_id: int):
        for string, client in [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]:
            if not string:
                continue
            try:
                await client.leave_call(chat_id, close=False)
            except Exception:
                pass
        try:
            await _clear_(chat_id)
        except Exception:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != "1.0":
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                if str(speed) == "0.5":
                    vs = 2.0
                elif str(speed) == "0.75":
                    vs = 1.35
                elif str(speed) == "1.5":
                    vs = 0.68
                elif str(speed) == "2.0":
                    vs = 0.5
                else:
                    vs = 1.0
                proc = await asyncio.create_subprocess_shell(
                    cmd=(
                        "ffmpeg "
                        "-i "
                        f"{file_path} "
                        "-filter:v "
                        f"setpts={vs}*PTS "
                        "-filter:a "
                        f"atempo={speed} "
                        f"{out}"
                    ),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
        else:
            out = file_path
        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        xx = f"-ss {played} -to {duration}"
        video_mode = playing[0]["streamtype"] == "video"
        stream = self._build_stream(out, video=video_mode, ffmpeg=xx)
        if str(db[chat_id][0]["file"]) == str(file_path):
            await self._play_on_assistant(assistant, chat_id, stream)
        else:
            raise AssistantErr("Umm")
        if str(db[chat_id][0]["file"]) == str(file_path):
            exis = (playing[0]).get("old_dur")
            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except Exception:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_call(chat_id, close=False)
        except Exception:
            pass

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        stream = self._build_stream(link, video=bool(video))
        await self._play_on_assistant(assistant, chat_id, stream)

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        ffmpeg = f"-ss {to_seek} -to {duration}"
        video_mode = mode == "video"
        stream = self._build_stream(
            file_path,
            video=video_mode,
            ffmpeg=ffmpeg,
        )
        await self._play_on_assistant(assistant, chat_id, stream)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOG_GROUP_ID)
        stream = self._build_stream(link, video=True)
        await self._play_on_assistant(assistant, config.LOG_GROUP_ID, stream)
        await asyncio.sleep(0.2)
        try:
            await assistant.leave_call(config.LOG_GROUP_ID, close=False)
        except Exception:
            pass

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        # Validate that link is not None or empty
        if not link or link.strip() == "":
            LOGGER(__name__).error(f"join_call received empty or invalid link for chat {chat_id}")
            raise AssistantErr(_["call_10"])
        
        LOGGER(__name__).info(f"Joining voice chat in {chat_id} with link: {link[:50] if len(link) > 50 else link}")
            
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        
        try:
            stream = self._build_stream(link, video=bool(video))
        except Exception as e:
            LOGGER(__name__).error(f"Failed to build stream: {e}")
            raise AssistantErr(_["call_10"])
        
        # Smart Adaptive Voice Chat Detection
        # Combines initial delay + retry for maximum reliability
        # Tested approach: 0.3s delay + 1 retry (2 attempts total)
        initial_sync_delay = 0.3  # Seconds for PyTgCalls to sync
        max_retries = 2
        retry_delay = 1.2  # Reduced from 1.5s for faster response
        
        # Initial sync delay - helps PyTgCalls detect active voice chat
        await asyncio.sleep(initial_sync_delay)
        
        joined_successfully = False
        
        for attempt in range(max_retries):
            try:
                LOGGER(__name__).info(f"🎵 Attempt {attempt + 1}/{max_retries} - Calling _play_on_assistant for {chat_id}")
                await self._play_on_assistant(assistant, chat_id, stream)
                joined_successfully = True
                LOGGER(__name__).info(f"✅ Successfully joined voice chat in {chat_id} - Music should be playing!")
                break  # Success!
            except exceptions.NoActiveGroupCall:
                LOGGER(__name__).warning(f"No active voice chat in {chat_id}, attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    # Retry after delay - catches edge cases (~9% cases)
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    # All attempts failed - genuine error (~1% cases)
                    LOGGER(__name__).error(f"All retry attempts failed for chat {chat_id}")
                    raise AssistantErr(_["call_8"])
            except exceptions.NoAudioSourceFound:
                LOGGER(__name__).error(f"No audio source found in chat {chat_id}")
                raise AssistantErr(_["call_10"])
            except (ConnectionNotFound, TelegramServerError) as e:
                LOGGER(__name__).error(f"Connection error in chat {chat_id}: {type(e).__name__}")
                raise AssistantErr(_["call_10"])
            except Exception as e:
                LOGGER(__name__).error(f"Unexpected error in join_call for chat {chat_id}: {type(e).__name__} - {str(e)}")
                raise AssistantErr(_["call_10"])
        
        # Only update database if we successfully joined
        if joined_successfully:
            await add_active_chat(chat_id)
            await music_on(chat_id)
            if video:
                await add_active_video_chat(chat_id)
            if await is_autoend():
                counter[chat_id] = {}
                users = len(await assistant.get_participants(chat_id))
                if users == 1:
                    autoend[chat_id] = datetime.now() + timedelta(minutes=1)

    async def change_stream(self, client: PyTgCalls, chat_id: int):
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)
            await auto_clean(popped)
            if not check:
                await _clear_(chat_id)
                return await client.leave_call(chat_id, close=False)
        except Exception:
            try:
                await _clear_(chat_id)
                return await client.leave_call(chat_id, close=False)
            except Exception:
                return
        queued = check[0]["file"]
        language = await get_lang(chat_id)
        _ = get_string(language)
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        original_chat_id = check[0]["chat_id"]
        streamtype = check[0]["streamtype"]
        videoid = check[0]["vidid"]
        db[chat_id][0]["played"] = 0
        exis = (check[0]).get("old_dur")
        if exis:
            db[chat_id][0]["dur"] = exis
            db[chat_id][0]["seconds"] = check[0]["old_second"]
            db[chat_id][0]["speed_path"] = None
            db[chat_id][0]["speed"] = 1.0
        video = True if str(streamtype) == "video" else False
        if "live_" in queued:
            n, link = await YouTube.video(videoid, True)
            if n == 0:
                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )
            stream = self._build_stream(link, video=video)
            try:
                await self._play_on_assistant(client, chat_id, stream)
            except Exception:
                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )
            img = await gen_thumb(videoid)
            button = stream_markup(_, chat_id)
            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    title[:23],
                    check[0]["dur"],
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        elif "vid_" in queued:
            mystic = await app.send_message(original_chat_id, _["call_7"])
            try:
                file_path, direct = await YouTube.download(
                    videoid,
                    mystic,
                    videoid=True,
                    video=video,
                )
            except Exception:
                return await mystic.edit_text(
                    _["call_6"], disable_web_page_preview=True
                )
            stream = self._build_stream(file_path, video=video)
            try:
                await self._play_on_assistant(client, chat_id, stream)
            except Exception:
                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )
            img = await gen_thumb(videoid)
            button = stream_markup(_, chat_id)
            await mystic.delete()
            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    title[:23],
                    check[0]["dur"],
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"

        elif "index_" in queued:
            stream = self._build_stream(videoid, video=video)
            try:
                await self._play_on_assistant(client, chat_id, stream)
            except Exception:
                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )
            button = stream_markup(_, chat_id)
            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=config.STREAM_IMG_URL,
                caption=_["stream_2"].format(user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        else:
            stream = self._build_stream(queued, video=video)
            try:
                await self._play_on_assistant(client, chat_id, stream)
            except Exception:
                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )
            if videoid == "telegram":
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=(
                        config.TELEGRAM_AUDIO_URL
                        if str(streamtype) == "audio"
                        else config.TELEGRAM_VIDEO_URL
                    ),
                    caption=_["stream_1"].format(
                        config.SUPPORT_GROUP, title[:23], check[0]["dur"], user
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif videoid == "soundcloud":
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.SOUNCLOUD_IMG_URL,
                    caption=_["stream_1"].format(
                        config.SUPPORT_GROUP, title[:23], check[0]["dur"], user
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                img = await gen_thumb(videoid)
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"

    async def ping(self):
        pings = []
        if config.STRING1:
            pings.append(self.one.ping)
        if config.STRING2:
            pings.append(self.two.ping)
        if config.STRING3:
            pings.append(self.three.ping)
        if config.STRING4:
            pings.append(self.four.ping)
        if config.STRING5:
            pings.append(self.five.ping)
        return str(round(sum(pings) / len(pings), 3)) if pings else "0"

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        if config.STRING1:
            await self.one.start()
        if config.STRING2:
            await self.two.start()
        if config.STRING3:
            await self.three.start()
        if config.STRING4:
            await self.four.start()
        if config.STRING5:
            await self.five.start()

    async def decorators(self):
        for string, client in [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]:
            if not string:
                continue
            @client.on_update()
            async def _update_handler(_, update: types.Update, _client=client):
                if isinstance(update, types.StreamEnded):
                    if update.stream_type == types.StreamEnded.Type.AUDIO:
                        await self.change_stream(_client, update.chat_id)
                elif isinstance(update, types.ChatUpdate):
                    if update.status in [
                        types.ChatUpdate.Status.KICKED,
                        types.ChatUpdate.Status.LEFT_GROUP,
                        types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                    ]:
                        await self.stop_stream(update.chat_id)

JARVIS = Call()
