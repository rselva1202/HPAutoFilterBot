import time
import math

from pyrogram import filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import search_files


# ==================================================
# SETTINGS
# ==================================================

FILES_PER_PAGE = 10

POWERED_BY = "⚡ Team_XHPT"


# ==================================================
# FORMAT FILE SIZE
# ==================================================

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


# ==================================================
# CREATE FILE BUTTON
# ==================================================

def create_file_button(number, file_data):

    db_id = file_data[0]
    file_name = file_data[2]
    file_size = file_data[5]

    size_text = format_file_size(file_size)

    # Remove extension from displayed name
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

    button_text = (
        f"{number}. "
        f"[{size_text}] "
        f"{display_name}"
    )

    return InlineKeyboardButton(
        text=button_text,
        callback_data=f"getfile:{db_id}"
    )


# ==================================================
# PAGINATION KEYBOARD
# ==================================================

def create_pagination_keyboard(
    query,
    page,
    total_pages
):

    buttons = []

    if page > 1:

        buttons.append(
            InlineKeyboardButton(
                "⬅ Previous",
                callback_data=f"searchpage:{page - 1}:{query}"
            )
        )

    buttons.append(
        InlineKeyboardButton(
            f"{page}/{total_pages}",
            callback_data="search_current"
        )
    )

    if page < total_pages:

        buttons.append(
            InlineKeyboardButton(
                "Next ➡",
                callback_data=f"searchpage:{page + 1}:{query}"
            )
        )

    return InlineKeyboardMarkup([buttons])


# ==================================================
# BUILD SEARCH RESULT
# ==================================================

def build_result_message(
    query,
    results,
    page,
    user,
    elapsed
):

    total_files = len(results)

    total_pages = max(
        1,
        math.ceil(total_files / FILES_PER_PAGE)
    )

    start = (
        (page - 1)
        * FILES_PER_PAGE
    )

    end = start + FILES_PER_PAGE

    page_results = results[start:end]

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    title = query

    # --------------------------------------------------
    # USER NAME
    # --------------------------------------------------

    if user.username:

        requested_by = f"@{user.username}"

    else:

        requested_by = user.first_name or "User"

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    text = (
        f"🏷 **ᴛɪᴛʟᴇ :** `{title}`\n"
        f"🧱 **ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ :** `{total_files}`\n"
        f"⏰ **ʀᴇꜱᴜʟᴛ ɪɴ :** `{elapsed:.2f} Sᴇᴄᴏɴᴅs`\n\n"
        f"📝 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** "
        f"**{requested_by}**\n"
        f"⚜️ **ᴘᴏᴡᴇʀᴇᴅ ʙʏ :** "
        f"**{POWERED_BY}**\n\n"
        f"**Your Requested Files Are Here** 👇\n\n"
    )

    # --------------------------------------------------
    # FILE BUTTONS
    # --------------------------------------------------

    keyboard = []

    for index, file_data in enumerate(
        page_results,
        start=start + 1
    ):

        keyboard.append([
            create_file_button(
                index,
                file_data
            )
        ])

    # --------------------------------------------------
    # PAGINATION
    # --------------------------------------------------

    keyboard.append(
        create_pagination_keyboard(
            query,
            page,
            total_pages
        ).inline_keyboard[0]
    )

    return (
        text,
        InlineKeyboardMarkup(keyboard)
    )


# ==================================================
# SEARCH HANDLER
# ==================================================

async def search_handler(client, message):

    query = message.text.strip()

    if not query:

        await message.reply_text(
            "🔎 Please enter a movie or series name."
        )

        return

    print(
        f"🔎 Search request: "
        f"{query} "
        f"from {message.from_user.id}"
    )

    start_time = time.perf_counter()

    try:

        results = search_files(query)

        elapsed = (
            time.perf_counter()
            - start_time
        )

        # --------------------------------------------------
        # NO RESULTS
        # --------------------------------------------------

        if not results:

            await message.reply_text(
                f"❌ **No files found.**\n\n"
                f"Search: `{query}`"
            )

            return

        # --------------------------------------------------
        # SEND RESULT
        # --------------------------------------------------

        text, keyboard = build_result_message(
            query=query,
            results=results,
            page=1,
            user=message.from_user,
            elapsed=elapsed
        )

        await message.reply_text(
            text,
            reply_markup=keyboard
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

        await message.reply_text(
            "❌ An error occurred while searching."
        )


# ==================================================
# PAGINATION CALLBACK
# ==================================================

async def search_page_handler(
    client,
    callback_query
):

    data = callback_query.data

    if not data.startswith("searchpage:"):

        return

    try:

        parts = data.split(":", 2)

        page = int(parts[1])
        query = parts[2]

    except (ValueError, IndexError):

        await callback_query.answer(
            "❌ Invalid page.",
            show_alert=True
        )

        return

    try:

        start_time = time.perf_counter()

        results = search_files(query)

        elapsed = (
            time.perf_counter()
            - start_time
        )

        if not results:

            await callback_query.answer(
                "❌ No files found.",
                show_alert=True
            )

            return

        total_pages = max(
            1,
            math.ceil(
                len(results)
                / FILES_PER_PAGE
            )
        )

        # Keep page inside valid range

        page = max(
            1,
            min(page, total_pages)
        )

        text, keyboard = build_result_message(
            query=query,
            results=results,
            page=page,
            user=callback_query.from_user,
            elapsed=elapsed
        )

        await callback_query.message.edit_text(
            text,
            reply_markup=keyboard
        )

        await callback_query.answer()

    except Exception as error:

        print(
            "❌ Pagination error:",
            error
        )

        await callback_query.answer(
            "❌ Unable to change page.",
            show_alert=True
        )


# ==================================================
# REGISTER HANDLERS
# ==================================================

def register_search_handler(app):

    # --------------------------------------------------
    # PRIVATE SEARCH
    # --------------------------------------------------

    app.add_handler(
        MessageHandler(
            search_handler,
            filters.private & filters.text
        )
    )

    # --------------------------------------------------
    # GROUP SEARCH
    # --------------------------------------------------

    app.add_handler(
        MessageHandler(
            search_handler,
            filters.group & filters.text
        )
    )

    # --------------------------------------------------
    # PAGINATION
    # --------------------------------------------------

    app.add_handler(
        CallbackQueryHandler(
            search_page_handler,
            filters.regex(r"^searchpage:")
        )
    )

    print(
        "✅ Search handler registered"
    )