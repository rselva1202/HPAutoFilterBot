from pyrogram import filters
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def ui_callback_handler(client, callback_query):

    data = callback_query.data

    # ---------------------------------------------
    # SEARCH
    # ---------------------------------------------

    if data == "search":

        await callback_query.answer()

        await callback_query.message.reply_text(
            "🔎 **Search Mode**\n\n"
            "Send the file name or keyword you want to find.\n\n"
            "Example:\n"
            "`Python`\n"
            "`Java`\n"
            "`C Programming`"
        )

        return

    # ---------------------------------------------
    # HELP
    # ---------------------------------------------

    if data == "help":

        await callback_query.answer()

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔎 Search Files",
                        callback_data="search"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="back"
                    )
                ]
            ]
        )

        await callback_query.message.edit_text(
            "📚 **AutoFilterPro Help**\n\n"
            "1️⃣ Press **Search Files**\n"
            "2️⃣ Enter a file name or keyword\n"
            "3️⃣ Choose the file you want\n"
            "4️⃣ Press **Get File**\n\n"
            "Example:\n"
            "`Python`",
            reply_markup=keyboard
        )

        return

    # ---------------------------------------------
    # ABOUT
    # ---------------------------------------------

    if data == "about":

        await callback_query.answer()

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="back"
                    )
                ]
            ]
        )

        await callback_query.message.edit_text(
            "ℹ️ **About AutoFilterPro**\n\n"
            "AutoFilterPro is a Telegram-based file "
            "search system.\n\n"
            "📦 Files are stored in Telegram.\n"
            "🔎 Metadata is indexed automatically.\n"
            "⚡ Search is powered by SQLite.\n\n"
            "Built with Python + Pyrogram.",
            reply_markup=keyboard
        )

        return

    # ---------------------------------------------
    # BACK
    # ---------------------------------------------

    if data == "back":

        await callback_query.answer()

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔎 Search Files",
                        callback_data="search"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📚 Help",
                        callback_data="help"
                    ),
                    InlineKeyboardButton(
                        "ℹ️ About",
                        callback_data="about"
                    )
                ]
            ]
        )

        await callback_query.message.edit_text(
            "🤖 **Welcome to AutoFilterPro!**\n\n"
            "🔎 Search and find files quickly.",
            reply_markup=keyboard
        )


def register_ui_handler(app):

    app.add_handler(
        CallbackQueryHandler(
            ui_callback_handler,
            filters.regex(r"^(search|help|about|back)$")
        )
    )