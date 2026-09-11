from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.access_tokens import (
    verify_access_token,
    consume_access_token
)

from handlers.file_delivery import deliver_file


# ==================================================
# START HANDLER
# ==================================================

async def start_handler(client, message):

    # --------------------------------------------------
    # GET /START PAYLOAD
    # --------------------------------------------------

    payload = None

    if message.command and len(message.command) > 1:
        payload = message.command[1]

    # --------------------------------------------------
    # ACCESS TOKEN FLOW
    # --------------------------------------------------

    if payload and payload.startswith("af_"):

        token = payload[3:]

        print("\n" + "=" * 50)
        print("🔐 ACCESS TOKEN REQUEST")
        print("User ID :", message.from_user.id)
        print("Token   :", token)
        print("=" * 50)

        # ----------------------------------------------
        # VERIFY TOKEN
        # ----------------------------------------------

        token_data = verify_access_token(
            token=token,
            user_id=message.from_user.id
        )

        if not token_data:

            await message.reply_text(
                "❌ **Invalid or expired access link.**\n\n"
                "Please go back to the search results "
                "and generate a new link."
            )

            return

        # ----------------------------------------------
        # GET FILE ID
        # ----------------------------------------------

        file_db_id = token_data["file_db_id"]

        # ----------------------------------------------
        # DELIVER FILE
        # ----------------------------------------------

        success, result = await deliver_file(
            client=client,
            user_id=message.from_user.id,
            db_id=file_db_id
        )

        if not success:

            await message.reply_text(
                "❌ Sorry, this file could not be delivered."
            )

            return

        # ----------------------------------------------
        # CONSUME TOKEN
        # ----------------------------------------------

        consume_access_token(token)

        await message.reply_text(
            "✅ **File sent successfully!**\n\n"
            "⏱️ This file will be automatically deleted "
            "from this chat after **15 minutes**."
        )

        print(
            f"✅ Access token completed: "
            f"user={message.from_user.id}, "
            f"file={file_db_id}"
        )

        return

    # ==================================================
    # NORMAL /START
    # ==================================================

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

    await message.reply_text(
        "🤖 **Welcome to AutoFilterPro!**\n\n"
        "🔎 Search and find files quickly.\n\n"
        "Use the button below to start searching.",
        reply_markup=keyboard
    )


# ==================================================
# REGISTER HANDLER
# ==================================================

def register_start_handler(app):

    app.add_handler(
        MessageHandler(
            start_handler,
            filters.private & filters.command("start")
        )
    )

    print(
        "✅ Start handler registered"
    )