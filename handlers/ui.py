from pyrogram import filters
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio


async def delete_message_after_one_minute(client, chat_id, message_id):
    """Delete a UI message after 1 minute."""
    await asyncio.sleep(60)

    try:
        await client.delete_messages(chat_id, message_id)
    except Exception:
        pass


async def ui_callback_handler(client, callback_query):

    data = callback_query.data

    # ---------------------------------------------
    # SEARCH
    # ---------------------------------------------

    if data == "search":

        await callback_query.answer()

        message = await callback_query.message.reply_text(
            "🔎 **Search Mode**\n\n"
            "Send the file name or keyword you want to find.\n\n"
            "Example:\n"
            "`Interstellar`\n"
            "`Iron Man`\n"
            "`Stranger Things S01`"
        )

        asyncio.create_task(
            delete_message_after_one_minute(
                client,
                callback_query.message.chat.id,
                message.id
            )
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
            "`Interstellar`",
            reply_markup=keyboard
        )

        # Delete the edited welcome/help message after 1 minute
        asyncio.create_task(
            delete_message_after_one_minute(
                client,
                callback_query.message.chat.id,
                callback_query.message.id
            )
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
            "AutoFilterPro is a Telegram-based file search system\n"
            "And is created by @Itz_Ragnar",
            reply_markup=keyboard
        )

        # Delete About message after 1 minute
        asyncio.create_task(
            delete_message_after_one_minute(
                client,
                callback_query.message.chat.id,
                callback_query.message.id
            )
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
            "🔎 Search and find files quickly.\n\n"
            "Use the button below to start searching.",
            reply_markup=keyboard
        )

        # Delete returned welcome message after 1 minute
        asyncio.create_task(
            delete_message_after_one_minute(
                client,
                callback_query.message.chat.id,
                callback_query.message.id
            )
        )

        return


def register_ui_handler(app):

    app.add_handler(
        CallbackQueryHandler(
            ui_callback_handler,
            filters.regex(r"^(search|help|about|back)$")
        )
    )