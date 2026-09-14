import time
import math
import secrets

from pyrogram import filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import search_files, schedule_file_deletion
from database import has_active_user_access
from handlers.file_delivery import deliver_file
from utils.access_tokens import generate_access_token
from utils.arolinks import create_access_link


FILES_PER_PAGE = 10
POWERED_BY = "⚡ @Team_XHPT"
SEARCH_STATES = {}


def format_file_size(size):
    if not size:
        return "0 B"

    size = float(size)
    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if size < 1024:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


def create_file_button(number, file_data):
    db_id = file_data[0]
    file_name = file_data[2]
    file_size = file_data[5]

    display_name = file_name

    for extension in [
        ".mkv",
        ".mp4",
        ".avi",
        ".mov",
        ".webm",
        ".m4v",
        ".ts"
    ]:
        if display_name.lower().endswith(extension):
            display_name = display_name[:-len(extension)]
            break

    return InlineKeyboardButton(
        text=f"{number}. [{format_file_size(file_size)}] {display_name}",
        callback_data=f"getfile:{db_id}"
    )


def _value_text(value, kind):
    if value is None or str(value).strip() == "":
        return "Unknown"

    return str(value)


def _get_filter_values(results, kind):

    indexes = {
        "language": 11,
        "year": 10,
        "quality": 12,
        "episode": 14,
        "season": 13
    }

    idx = indexes[kind]

    values = []
    seen = set()

    for row in results:

        value = row[idx]

        key = "" if value is None else str(value).strip()

        if key not in seen:

            seen.add(key)
            values.append(value)

    if kind in ("year", "episode", "season"):

        def number_key(v):

            try:
                return (0, int(v))

            except Exception:
                return (1, str(v).lower())

        values.sort(key=number_key)

    else:

        values.sort(
            key=lambda v: str(v or "").lower()
        )

    return values


def _apply_filters(results, selected):

    indexes = {
        "language": 11,
        "year": 10,
        "quality": 12,
        "episode": 14,
        "season": 13
    }

    filtered = results

    for kind, wanted in selected.items():

        idx = indexes[kind]

        filtered = [
            row
            for row in filtered
            if (
                ""
                if row[idx] is None
                else str(row[idx]).strip()
            ) == wanted
        ]

    return filtered


def _filter_row(state_id, kind, label):

    return InlineKeyboardButton(
        label,
        callback_data=f"sr:{state_id}:filter:{kind}"
    )


def create_filter_keyboard(state_id, results, selected):

    return InlineKeyboardMarkup(
        [
            [
                _filter_row(
                    state_id,
                    "language",
                    "LANGUAGES"
                ),
                _filter_row(
                    state_id,
                    "year",
                    "YEARS"
                ),
            ],
            [
                _filter_row(
                    state_id,
                    "quality",
                    "QUALITY"
                ),
                _filter_row(
                    state_id,
                    "episode",
                    "EPISODES"
                ),
                _filter_row(
                    state_id,
                    "season",
                    "SEASONS"
                ),
            ],
        ]
    )


def create_pagination_keyboard(
    state_id,
    page,
    total_pages
):

    row = [
        InlineKeyboardButton(
            f"PAGE {page}/{total_pages}",
            callback_data="search_current"
        )
    ]

    if page < total_pages:

        row.append(
            InlineKeyboardButton(
                "NEXT ➡",
                callback_data=(
                    f"sr:{state_id}:page:{page + 1}"
                )
            )
        )

    return row


def build_keyboard(
    state_id,
    results,
    page,
    selected
):

    total_pages = max(
        1,
        math.ceil(
            len(results) / FILES_PER_PAGE
        )
    )

    start = (
        page - 1
    ) * FILES_PER_PAGE

    page_results = results[
        start:start + FILES_PER_PAGE
    ]

    keyboard = []

    for index, file_data in enumerate(
        page_results,
        start=start + 1
    ):

        keyboard.append(
            [
                create_file_button(
                    index,
                    file_data
                )
            ]
        )

    keyboard.extend(
        create_filter_keyboard(
            state_id,
            results,
            selected
        ).inline_keyboard
    )

    keyboard.append(
        create_pagination_keyboard(
            state_id,
            page,
            total_pages
        )
    )

    return InlineKeyboardMarkup(keyboard)


def build_result_message(
    query,
    results,
    page,
    user,
    elapsed,
    selected=None
):

    selected = selected or {}

    total_files = len(results)

    total_pages = max(
        1,
        math.ceil(
            total_files / FILES_PER_PAGE
        )
    )

    if user.username:

        requested_by = (
            f"@{user.username}"
        )

    else:

        requested_by = (
            user.first_name or "User"
        )

    text = (

        f"🏷 **ᴛɪᴛʟᴇ :** `{query}`\n"

        f"🧱 **ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ :** "
        f"`{total_files}`\n"

        f"⏰ **ʀᴇꜱᴜʟᴛ ɪɴ :** "
        f"`{elapsed:.2f} Sᴇᴄᴏɴᴅs`\n\n"

        f"📝 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** "
        f"**{requested_by}**\n"

        f"⚜️ **ᴘᴏᴡᴇʀᴇᴅ ʙʏ :** "
        f"**{POWERED_BY}**\n\n"

        f"> 🗑️ **This message will be "
        f"deleted after 1 minute.**\n\n"

        f"**Your Requested Files Are Here** 👇\n\n"
    )

    return text, build_keyboard(
        state_id="PLACEHOLDER",
        results=results,
        page=page,
        selected=selected,
    )


def _make_state(
    user_id,
    query,
    results,
    elapsed
):

    state_id = secrets.token_hex(4)

    SEARCH_STATES[state_id] = {

        "user_id": user_id,

        "query": query,

        "results": results,

        "elapsed": elapsed,

        "selected": {},

        "created": time.time(),
    }

    # Keep memory bounded.

    if len(SEARCH_STATES) > 200:

        oldest = sorted(
            SEARCH_STATES.items(),
            key=lambda x: x[1]["created"]
        )[:50]

        for key, _ in oldest:

            SEARCH_STATES.pop(
                key,
                None
            )

    return state_id


def _render_state(
    state_id,
    page=1
):

    state = SEARCH_STATES[state_id]

    filtered = _apply_filters(
        state["results"],
        state["selected"]
    )

    total_pages = max(
        1,
        math.ceil(
            len(filtered) / FILES_PER_PAGE
        )
    )

    page = max(
        1,
        min(
            page,
            total_pages
        )
    )

    text = (

        f"🏷 **ᴛɪᴛʟᴇ :** "
        f"`{state['query']}`\n"

        f"🧱 **ᴛᴏᴛᴀʟ ꜱʜᴏᴡɴ :** "
        f"`{len(filtered)}`\n"

        f"⏰ **ʀᴇꜱᴜʟᴛ ɪɴ :** "
        f"`{state['elapsed']:.2f} Sᴇᴄᴏɴᴅs`\n\n"

        f"📝 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** "
        f"**{(' @' + str(state['username'])) if state.get('username') else 'User'}**\n"

        f"⚜️ **ᴘᴏᴡᴇʀᴇᴅ ʙʏ :** "
        f"**{POWERED_BY}**\n\n"

        f"> 🗑️ **This message will be "
        f"deleted after 1 minute.**\n\n"

        f"**Your Requested Files Are Here** 👇\n\n"
    )

    # Correct username formatting for stored state.

    if state.get("requested_by"):

        text = text.replace(
            f"**{(' @' + str(state['username'])) if state.get('username') else 'User'}**",
            f"**{state['requested_by']}**"
        )

    start = (
        page - 1
    ) * FILES_PER_PAGE

    keyboard = []

    for index, row in enumerate(
        filtered[
            start:start + FILES_PER_PAGE
        ],
        start=start + 1
    ):

        keyboard.append(
            [
                create_file_button(
                    index,
                    row
                )
            ]
        )

    keyboard.extend(
        create_filter_keyboard(
            state_id,
            filtered,
            state["selected"]
        ).inline_keyboard
    )

    keyboard.append(
        create_pagination_keyboard(
            state_id,
            page,
            total_pages
        )
    )

    return (
        text,
        InlineKeyboardMarkup(keyboard)
    )


async def _delete_later(
    client,
    chat_id,
    message_id,
    minutes=1
):

    from datetime import (
        datetime,
        timedelta,
        timezone
    )

    delete_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=minutes)
    ).isoformat()

    schedule_file_deletion(
        chat_id=chat_id,
        message_id=message_id,
        delete_at=delete_at
    )


async def search_handler(
    client,
    message
):

    # Ignore Telegram commands.

    if message.command:
        return

    query = message.text.strip()

    # Ignore the bot's online/start message.

    if "HPAutoFilter is online!" in query:
        return

    if not query:

        result = await message.reply_text(
            "🔎 Please enter a movie or series name."
        )

        await _delete_later(
            client,
            message.chat.id,
            result.id
        )

        return

    print(
        f"🔎 Search request: "
        f"{query} from "
        f"{message.from_user.id}"
    )

    start_time = time.perf_counter()

    try:

        results = search_files(query)

        elapsed = (
            time.perf_counter()
            - start_time
        )

        if not results:

            result = await message.reply_text(
                f"❌ **No files found.**\n\n"
                f"Search: `{query}`"
            )

            await _delete_later(
                client,
                message.chat.id,
                result.id
            )

            return

        state_id = _make_state(
            message.from_user.id,
            query,
            results,
            elapsed
        )

        state = SEARCH_STATES[state_id]

        state["requested_by"] = (
            f"@{message.from_user.username}"
            if message.from_user.username
            else (
                message.from_user.first_name
                or "User"
            )
        )

        text, keyboard = _render_state(
            state_id,
            1
        )

        result_message = await message.reply_text(
            text,
            reply_markup=keyboard
        )

        await _delete_later(
            client,
            message.chat.id,
            result_message.id
        )

        print(
            f"✅ Results sent: "
            f"{len(results)} files"
        )

    except Exception as error:

        print(
            "❌ Search error:",
            error
        )

        result = await message.reply_text(
            "❌ An error occurred while searching."
        )

        await _delete_later(
            client,
            message.chat.id,
            result.id
        )


async def search_callback_handler(
    client,
    callback_query
):

    data = callback_query.data

    if not data.startswith("sr:"):
        return

    parts = data.split(":")

    if len(parts) < 3:

        await callback_query.answer(
            "❌ Invalid request.",
            show_alert=True
        )

        return

    state_id = parts[1]

    state = SEARCH_STATES.get(
        state_id
    )

    if not state:

        await callback_query.answer(
            "❌ This search has expired. "
            "Please search again.",
            show_alert=True
        )

        return

    if (
        callback_query.from_user.id
        != state["user_id"]
    ):

        await callback_query.answer(
            "❌ This search belongs to another user.",
            show_alert=True
        )

        return

    action = parts[2]

    try:

        if action == "page":

            page = int(parts[3])

            text, keyboard = _render_state(
                state_id,
                page
            )

            await callback_query.message.edit_text(
                text,
                reply_markup=keyboard
            )

            await callback_query.answer()

            return

        if action == "filter":

            kind = parts[3]

            values = _get_filter_values(
                _apply_filters(
                    state["results"],
                    state["selected"]
                ),
                kind
            )

            if not values:

                await callback_query.answer(
                    f"❌ No {kind} values available.",
                    show_alert=True
                )

                return

            rows = [
                InlineKeyboardButton(
                    "ALL",
                    callback_data=(
                        f"sr:{state_id}:clear:{kind}"
                    )
                )
            ]

            for i, value in enumerate(values):

                label = _value_text(
                    value,
                    kind
                )

                rows.append(
                    InlineKeyboardButton(
                        label,
                        callback_data=(
                            f"sr:{state_id}:value:"
                            f"{kind}:{i}"
                        )
                    )
                )

            # Two buttons per row.

            keyboard = [
                rows[i:i + 2]
                for i in range(
                    0,
                    len(rows),
                    2
                )
            ]

            keyboard.append(
                [
                    InlineKeyboardButton(
                        "↩️ BACK",
                        callback_data=(
                            f"sr:{state_id}:back"
                        )
                    )
                ]
            )

            await callback_query.message.edit_reply_markup(
                InlineKeyboardMarkup(keyboard)
            )

            await callback_query.answer()

            return

        if action == "value":

            kind = parts[3]

            index = int(parts[4])

            values = _get_filter_values(
                _apply_filters(
                    state["results"],
                    state["selected"]
                ),
                kind
            )

            if index >= len(values):

                raise ValueError(
                    "filter index"
                )

            value = (
                ""
                if values[index] is None
                else str(values[index]).strip()
            )

            state["selected"][kind] = value

            text, keyboard = _render_state(
                state_id,
                1
            )

            await callback_query.message.edit_text(
                text,
                reply_markup=keyboard
            )

            await callback_query.answer(
                f"✅ {kind.title()}: "
                f"{value or 'Unknown'}"
            )

            return

        if action == "clear":

            kind = parts[3]

            state["selected"].pop(
                kind,
                None
            )

            text, keyboard = _render_state(
                state_id,
                1
            )

            await callback_query.message.edit_text(
                text,
                reply_markup=keyboard
            )

            await callback_query.answer(
                f"✅ {kind.title()} filter cleared"
            )

            return

        if action == "back":

            text, keyboard = _render_state(
                state_id,
                1
            )

            await callback_query.message.edit_text(
                text,
                reply_markup=keyboard
            )

            await callback_query.answer()

            return

    except Exception as error:

        print(
            "❌ Search callback error:",
            error
        )

        await callback_query.answer(
            "❌ Unable to process that request.",
            show_alert=True
        )


def register_search_handler(app):

    app.add_handler(
        MessageHandler(
            search_handler,
            filters.private
            & filters.text
            & ~filters.command("start")
        )
    )

    app.add_handler(
        MessageHandler(
            search_handler,
            filters.group
            & filters.text
            & ~filters.command("start")
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            search_callback_handler,
            filters.regex(r"^sr:")
        )
    )

    print(
        "✅ Search handler registered"
    )