# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

# Clone Code Credit : YT - @Tech_VJ / TG - @VJ_Bots / GitHub - @VJBots

import os, logging, string, asyncio, time, re, ast, random, math, pytz, pyrogram
from datetime import datetime, timedelta, date, time
from Script import script
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from utils import get_size, is_subscribed, pub_is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink, get_tutorial, send_all, get_cap, build_result_keyboard, build_filter_menu_keyboard, get_result_page_size
from database.users_chats_db import db
from database.ia_filterdb import get_file_details, get_search_results, get_bad_files

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
lock = asyncio.Lock()

BUTTON = {}
BUTTONS = {}
FRESH = {}
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}
SPELL_CHECK = {}
ACTIVE_SEARCH = {}
UI_TZ = pytz.timezone('Asia/Kolkata')

def _elapsed_seconds(started_at):
    return f"{(datetime.now(UI_TZ) - started_at).total_seconds():.2f}"

async def _edit_result_message(target_message, caption, reply_markup):
    try:
        if getattr(target_message, "media", None):
            await target_message.edit_caption(
                caption=caption,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML,
            )
        else:
            await target_message.edit_text(
                text=caption,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
            )
    except MessageNotModified:
        pass

async def _render_result_page(target_message, context_message, settings, search, files, total_results, key, offset=0, back_callback=None, started_at=None, pagination_total=None, keyboard_page_size=None):
    page_size = keyboard_page_size or get_result_page_size(settings)
    caption = await get_cap(
        settings,
        _elapsed_seconds(started_at or datetime.now(UI_TZ)),
        files,
        context_message,
        total_results,
        search,
        offset=offset,
        page_size=page_size,
    )
    req = context_message.from_user.id if context_message.from_user else 0
    pre = 'filep' if settings['file_secure'] else 'file'
    reply_markup = None
    if settings.get("button", True):
        reply_markup = build_result_keyboard(
            files,
            key,
            req,
            offset,
            total_results,
            pre,
            page_size,
            back_callback=back_callback,
            pagination_total=pagination_total,
        )
    await _edit_result_message(target_message, caption, reply_markup)

async def _show_filter_menu(query, menu_type, key, values, callback_prefix, columns, back_callback):
    try:
        await query.edit_message_reply_markup(
            reply_markup=build_filter_menu_keyboard(menu_type, key, values, callback_prefix, columns, back_callback)
        )
    except MessageNotModified:
        pass

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    ai_search = True
    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
    await auto_filter(client, message.text, message, reply_msg, ai_search)
            
@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#"): return  # ignore commands and hashtags
    ai_search = True
    reply_msg = await bot.send_message(message.from_user.id, f"<b><i>Searching For {content} 🔍</i></b>", reply_to_message_id=message.id)
    await auto_filter(bot, content, message, reply_msg, ai_search)
    
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    _, req, key, offset = query.data.split("_")
    started_at = datetime.now(UI_TZ)
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0

    search = ACTIVE_SEARCH.get(key, FRESH.get(key))
    if not search:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)

    settings = await get_settings(query.message.chat.id)
    page_size = get_result_page_size(settings)
    files, _, total = await get_search_results(query.message.chat.id, search, max_results=page_size, offset=offset, filter=True)
    if not files:
        return await query.answer("No more results found.", show_alert=True)

    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    context_message = query.message.reply_to_message or query.message
    await _render_result_page(
        query.message,
        context_message,
        settings,
        search,
        files,
        total,
        key,
        offset=offset,
        started_at=started_at,
    )
    await query.answer()
@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    movie = re.sub(r"[:\-]", " ", movie)
    movie = re.sub(r"\s+", " ", movie).strip()
    await query.answer(script.TOP_ALRT_MSG)
    files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        ai_search = True
        reply_msg = await query.message.edit_text(f"<b><i>Searching For {movie} 🔍</i></b>")
        await auto_filter(bot, movie, query, reply_msg, ai_search, k)
    else:
        reqstr1 = query.from_user.id if query.from_user else 0
        reqstr = await bot.get_users(reqstr1)
        k = await query.message.edit(script.MVE_NT_FND)
        await asyncio.sleep(10)
        await k.delete()

# Year 
@Client.on_callback_query(filters.regex(r"^years#"))
async def years_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"Hello {query.from_user.first_name},\nthis is not your movie request.\nPlease request your own...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    await _show_filter_menu(query, "year", key, YEARS, "fy", 4, f"fy#homepage#{key}")

@Client.on_callback_query(filters.regex(r"^fy#"))
async def filter_yearss_cb_handler(client: Client, query: CallbackQuery):
    started_at = datetime.now(UI_TZ)
    _, year, key = query.data.split("#")
    base_search = FRESH.get(key)
    if not base_search:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"Hello {query.from_user.first_name},\nthis is not your movie request.\nPlease request your own...",
                show_alert=True,
            )
    except:
        pass

    settings = await get_settings(query.message.chat.id)
    page_size = get_result_page_size(settings)
    search = base_search if year == "homepage" else f"{base_search} {year}"
    ACTIVE_SEARCH[key] = search
    files, _, total_results = await get_search_results(query.message.chat.id, search, max_results=page_size, offset=0, filter=True)
    if not files:
        return await query.answer("No file found for this filter.", show_alert=True)

    temp.GETALL[key] = files
    context_message = query.message.reply_to_message or query.message
    await _render_result_page(
        query.message,
        context_message,
        settings,
        search,
        files,
        total_results,
        key,
        back_callback=None if year == "homepage" else f"fy#homepage#{key}",
        started_at=started_at,
    )
    await query.answer()

# Episode
@Client.on_callback_query(filters.regex(r"^episodes#"))
async def episodes_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"Hello {query.from_user.first_name},\nthis is not your movie request.\nPlease request your own...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    await _show_filter_menu(query, "episode", key, EPISODES, "fe", 4, f"fe#homepage#{key}")

@Client.on_callback_query(filters.regex(r"^fe#"))
async def filter_episodes_cb_handler(client: Client, query: CallbackQuery):
    started_at = datetime.now(UI_TZ)
    _, episode, key = query.data.split("#")
    base_search = FRESH.get(key)
    if not base_search:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"Hello {query.from_user.first_name},\nthis is not your movie request.\nPlease request your own...",
                show_alert=True,
            )
    except:
        pass

    settings = await get_settings(query.message.chat.id)
    page_size = get_result_page_size(settings)
    search = base_search if episode == "homepage" else f"{base_search} {episode}"
    ACTIVE_SEARCH[key] = search
    files, _, total_results = await get_search_results(query.message.chat.id, search, max_results=page_size, offset=0, filter=True)
    if not files:
        return await query.answer("No file found for this filter.", show_alert=True)

    temp.GETALL[key] = files
    context_message = query.message.reply_to_message or query.message
    await _render_result_page(
        query.message,
        context_message,
        settings,
        search,
        files,
        total_results,
        key,
        back_callback=None if episode == "homepage" else f"fe#homepage#{key}",
        started_at=started_at,
    )
    await query.answer()

#languages
@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"Hello {query.from_user.first_name},\nthis is not your movie request.\nPlease request your own...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    await _show_filter_menu(query, "language", key, LANGUAGES, "fl", 2, f"fl#homepage#{key}")

@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    started_at = datetime.now(UI_TZ)
    _, language, key = query.data.split("#")
    base_search = FRESH.get(key)
    if not base_search:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"Hello {query.from_user.first_name},\nthis is not your movie request.\nPlease request your own...",
                show_alert=True,
            )
    except:
        pass

    settings = await get_settings(query.message.chat.id)
    page_size = get_result_page_size(settings)
    search = base_search if language == "homepage" else f"{base_search} {language}"
    ACTIVE_SEARCH[key] = search
    files, _, total_results = await get_search_results(query.message.chat.id, search, max_results=page_size, offset=0, filter=True)
    if not files:
        return await query.answer("No file found for this filter.", show_alert=True)

    temp.GETALL[key] = files
    context_message = query.message.reply_to_message or query.message
    await _render_result_page(
        query.message,
        context_message,
        settings,
        search,
        files,
        total_results,
        key,
        back_callback=None if language == "homepage" else f"fl#homepage#{key}",
        started_at=started_at,
    )
    await query.answer()

@Client.on_callback_query(filters.regex(r"^seasons#"))
async def seasons_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"Hello {query.from_user.first_name},\nthis is not your movie request.\nPlease request your own...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    await _show_filter_menu(query, "season", key, SEASONS, "fs", 2, f"fs#homepage#{key}")

@Client.on_callback_query(filters.regex(r"^fs#"))
async def filter_seasons_cb_handler(client: Client, query: CallbackQuery):
    started_at = datetime.now(UI_TZ)
    _, season, key = query.data.split("#")
    base_search = FRESH.get(key)
    if not base_search:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"Hello {query.from_user.first_name},\nthis is not your movie request.\nPlease request your own...",
                show_alert=True,
            )
    except:
        pass

    settings = await get_settings(query.message.chat.id)
    page_size = get_result_page_size(settings)
    if season == "homepage":
        ACTIVE_SEARCH[key] = base_search
        files, _, total_results = await get_search_results(query.message.chat.id, base_search, max_results=page_size, offset=0, filter=True)
        if not files:
            return await query.answer("No file found for this filter.", show_alert=True)
        temp.GETALL[key] = files
        context_message = query.message.reply_to_message or query.message
        await _render_result_page(
            query.message,
            context_message,
            settings,
            base_search,
            files,
            total_results,
            key,
            started_at=started_at,
        )
        await query.answer()
        return

    short_codes = {
        "season 1": "s01", "season 2": "s02", "season 3": "s03", "season 4": "s04", "season 5": "s05",
        "season 6": "s06", "season 7": "s07", "season 8": "s08", "season 9": "s09", "season 10": "s10",
    }
    long_codes = {
        "season 1": "season 01", "season 2": "season 02", "season 3": "season 03", "season 4": "season 04", "season 5": "season 05",
        "season 6": "season 06", "season 7": "season 07", "season 8": "season 08", "season 9": "season 09", "season 10": "season 10",
    }
    search_terms = [f"{base_search} {season}"]
    ACTIVE_SEARCH[key] = f"{base_search} {season}"
    if season in short_codes:
        search_terms.append(f"{base_search} {short_codes[season]}")
    if season in long_codes:
        search_terms.append(f"{base_search} {long_codes[season]}")

    files = []
    seen_ids = set()
    for term in search_terms:
        batch, _, _ = await get_search_results(query.message.chat.id, term, max_results=page_size, offset=0, filter=True)
        for file_data in batch:
            if file_data["file_id"] not in seen_ids:
                seen_ids.add(file_data["file_id"])
                files.append(file_data)

    if not files:
        return await query.answer("No file found for this filter.", show_alert=True)

    temp.GETALL[key] = files
    context_message = query.message.reply_to_message or query.message
    await _render_result_page(
        query.message,
        context_message,
        settings,
        f"{base_search} {season}",
        files,
        len(files),
        key,
        back_callback=f"fs#homepage#{key}",
        started_at=started_at,
        pagination_total=len(files),
        keyboard_page_size=max(len(files), 1),
    )
    await query.answer()

@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"Hello {query.from_user.first_name},\nthis is not your movie request.\nPlease request your own...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    await _show_filter_menu(query, "quality", key, QUALITIES, "fq", 2, f"fq#homepage#{key}")

@Client.on_callback_query(filters.regex(r"^fq#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    started_at = datetime.now(UI_TZ)
    _, quality, key = query.data.split("#")
    base_search = FRESH.get(key)
    if not base_search:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"Hello {query.from_user.first_name},\nthis is not your movie request.\nPlease request your own...",
                show_alert=True,
            )
    except:
        pass

    settings = await get_settings(query.message.chat.id)
    page_size = get_result_page_size(settings)
    search = base_search if quality == "homepage" else f"{base_search} {quality}"
    ACTIVE_SEARCH[key] = search
    files, _, total_results = await get_search_results(query.message.chat.id, search, max_results=page_size, offset=0, filter=True)
    if not files:
        return await query.answer("No file found for this filter.", show_alert=True)

    temp.GETALL[key] = files
    context_message = query.message.reply_to_message or query.message
    await _render_result_page(
        query.message,
        context_message,
        settings,
        search,
        files,
        total_results,
        key,
        back_callback=None if quality == "homepage" else f"fq#homepage#{key}",
        started_at=started_at,
    )
    await query.answer()
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    me = await client.get_me()
    settings = await db.get_bot(me.id)
    if query.data == "close_data":
        await query.message.delete()

    elif query.data == "pages":
        await query.answer()

    elif query.data == "help":
        text = "<b>👨‍💻 How To Use Bot :-\n\n🔻 /start - check bot is working or not.\n\n🔻 /stats - check bot files and users.\n\n🔻 /settings - configure clone bot settings ( owner only ).\n\n🔻 /reset - reset all settings to default or none ( owner only ).\n\n🔻 /broadcast - broadcast a message to your bot users ( owner only ).</b>"
        btn = [[
            InlineKeyboardButton("🔍 ᴀʙᴏᴜᴛ", callback_data="about"),
            InlineKeyboardButton("🏡 ʜᴏᴍᴇ", callback_data="start")
        ]]
        await query.message.edit_text(text = text, reply_markup = InlineKeyboardMarkup(btn))

    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('⤬ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⤬', url=f'http://t.me/{me.username}?startgroup=true')
        ],[
            InlineKeyboardButton('🕵️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('🔍 ᴀʙᴏᴜᴛ', callback_data='about')
        ]]
        if settings["update_channel_link"] != None:
            buttons.append([[InlineKeyboardButton('🍿 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 🍿', url=f'{settings["update_channel_link"]}')]])
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text=script.CLONE_START_TXT.format(query.from_user.mention, me.username, me.first_name), reply_markup=reply_markup)

    elif query.data == "about":
        btn = [[
            InlineKeyboardButton('🕵️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton("🏡 ʜᴏᴍᴇ", callback_data="start")
        ]]
        await query.message.edit_text(text = script.CLONE_ABOUT_TXT.format(me.mention, temp.U_NAME, temp.B_NAME), reply_markup = InlineKeyboardMarkup(btn))
        
    if query.data.startswith("file"):
        clicked = query.from_user.id
        try:
            typed = query.message.reply_to_message.from_user.id
        except:
            typed = query.from_user.id
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
        files = files_
        title = files['file_name']
        size = get_size(files['file_size'])
        f_caption = files['caption']
        if f_caption is None:
            f_caption = f"{files['file_name']}"

        try:
            if settings['url']:
                if clicked == typed:
                    temp.SHORT[clicked] = query.message.chat.id
                    await query.answer(url=f"https://telegram.me/{me.username}?start=short_{file_id}")
                    return
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !", show_alert=True)
            else:
                if clicked == typed:
                    await query.answer(url=f"https://telegram.me/{me.username}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !", show_alert=True)
        except UserIsBlocked:
            await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{me.username}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://telegram.me/{me.username}?start={ident}_{file_id}")
            
    elif query.data.startswith("sendfiles"):
        clicked = query.from_user.id
        ident, key = query.data.split("#")
        try:
            if settings['url']:
                await query.answer(url=f"https://telegram.me/{me.username}?start=sendfiles1_{key}")
            else:
                await query.answer(url=f"https://telegram.me/{me.username}?start=allfiles_{key}")    
                
        except UserIsBlocked:
            await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{me.username}?start=sendfiles3_{key}")
        except Exception as e:
            logger.exception(e)
            await query.answer(url=f"https://telegram.me/{me.username}?start=sendfiles4_{key}")
    
    elif query.data.startswith("send_fsall"):
        temp_var, ident, key, offset = query.data.split("#")
        settings = await get_settings(query.message.chat.id)
        page_size = get_result_page_size(settings)
        searches = [BUTTONS0.get(key), BUTTONS1.get(key), BUTTONS2.get(key)]
        valid_searches = [search for search in searches if search]
        if not valid_searches:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
            return
        for search in valid_searches:
            files, _, _ = await get_search_results(query.message.chat.id, search, max_results=page_size, offset=int(offset), filter=True)
            if files:
                await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)
        
    elif query.data.startswith("send_fall"):
        temp_var, ident, key, offset = query.data.split("#")
        settings = await get_settings(query.message.chat.id)
        page_size = get_result_page_size(settings)
        search = ACTIVE_SEARCH.get(key, FRESH.get(key))
        files, _, _ = await get_search_results(query.message.chat.id, search, max_results=page_size, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)


async def auto_filter(client, name, msg, reply_msg, ai_search, spoll=False):
    started_at = datetime.now(UI_TZ)
    if not spoll:
        message = msg
        if message.text.startswith("/"):
            return
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) >= 100:
            return

        settings = await get_settings(message.chat.id)
        page_size = get_result_page_size(settings)
        search = name.lower()
        cleaned_words = []
        removes = ["in", "upload", "series", "full", "horror", "thriller", "mystery", "print", "file"]
        for item in search.split(" "):
            if item not in removes:
                cleaned_words.append(item)
        search = " ".join(cleaned_words)
        search = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|bro|bruh|broh|helo|that|find|dubbed|link|venum|iruka|pannunga|pannungga|anuppunga|anupunga|anuppungga|anupungga|film|undo|kitti|kitty|tharu|kittumo|kittum|movie|any(one)|with\ssubtitle(s)?)", "", search, flags=re.IGNORECASE)
        search = re.sub(r"\s+", " ", search).strip()
        search = search.replace("-", " ").replace(":", "").replace(".", "")
        files, _, total_results = await get_search_results(message.chat.id, search, max_results=page_size, offset=0, filter=True)
        if not files:
            return await advantage_spell_chok(client, name, msg, reply_msg, ai_search)
    else:
        message = msg.message.reply_to_message
        search, files, _, total_results = spoll
        settings = await get_settings(message.chat.id)
        page_size = get_result_page_size(settings)
        await msg.message.delete()

    key = f"{message.chat.id}-{message.id}"
    FRESH[key] = search
    ACTIVE_SEARCH[key] = search
    temp.GETALL[key] = files
    if message.from_user:
        temp.SHORT[message.from_user.id] = message.chat.id

    caption = await get_cap(settings, _elapsed_seconds(started_at), files, message, total_results, search, page_size=page_size)
    pre = 'filep' if settings['file_secure'] else 'file'
    req = message.from_user.id if message.from_user else 0
    reply_markup = build_result_keyboard(files, key, req, 0, total_results, pre, page_size) if settings.get("button", True) else None

    imdb = await get_poster(search, file=files[0]['file_name']) if settings["imdb"] else None
    if imdb:
        imdb_caption = script.IMDB_TEMPLATE_TXT.format(
            qurey=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
        )
        if message.from_user:
            temp.IMDB_CAP[key] = imdb_caption
            temp.IMDB_CAP[message.from_user.id] = imdb_caption
        caption = await get_cap(settings, _elapsed_seconds(started_at), files, message, total_results, search, page_size=page_size)

    if imdb and imdb.get('poster'):
        try:
            result_message = await message.reply_photo(photo=imdb.get('poster'), caption=caption, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
            await reply_msg.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            poster = imdb.get('poster').replace('.jpg', '._V1_UX360.jpg')
            result_message = await message.reply_photo(photo=poster, caption=caption, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
            await reply_msg.delete()
        except Exception as e:
            logger.exception(e)
            result_message = await reply_msg.edit_text(text=caption, reply_markup=reply_markup, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
    else:
        result_message = await reply_msg.edit_text(text=caption, reply_markup=reply_markup, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)

    await asyncio.sleep(300)
    await result_message.delete()
    await message.delete()

async def advantage_spell_chok(client, name, msg, reply_msg, vj_search):
    mv_id = msg.id
    mv_rqst = name
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        k = await reply_msg.edit_text(text=script.I_CUDNT.format(mv_rqst), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist = []
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        k = await reply_msg.edit_text(text=script.I_CUDNT.format(mv_rqst), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist += [movie.get('title') for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
    SPELL_CHECK[mv_id] = movielist
    if vj_search == True:
        vj_search_new = False
        vj_ai_msg = await reply_msg.edit_text("<b><i>Advance Ai Of Tech VJ Try To Find Your Movie With Your Wrong Spelling.</i></b>")
        movienamelist = []
        movienamelist += [movie.get('title') for movie in movies]
        for techvj in movienamelist:
            try:
                mv_rqst = mv_rqst.capitalize()
            except:
                pass
            if mv_rqst.startswith(techvj[0]):
                await auto_filter(client, techvj, msg, reply_msg, vj_search_new)
                break
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        k = await reply_msg.edit_text(text=script.I_CUDNT.format(mv_rqst), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(30)
        await k.delete()
        return
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=movie_name.strip(),
                    callback_data=f"spol#{reqstr1}#{k}",
                )
            ]
            for k, movie_name in enumerate(movielist)
        ]
        btn.append([InlineKeyboardButton(text="Close", callback_data=f'spol#{reqstr1}#close_spellcheck')])
        spell_check_del = await reply_msg.edit_text(
            text=script.CUDNT_FND.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(btn)
        )
        await asyncio.sleep(600)
        await spell_check_del.delete()



