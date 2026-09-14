from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.access_tokens import (
    verify_access_token,
    consume_access_token
)

from database import schedule_file_deletion, grant_user_access
from handlers.file_delivery import deliver_file


# ==================================================
# DELETE MESSAGE AFTER 1 MINUTE
# ==================================================

async def delete_after_one_minute(client, chat_id, message_id):

    import asyncio

    await asyncio.sleep(60)

    try:
        await client.delete_messages(
            chat_id=chat_id,
            message_ids=message_id
        )

        print(
            f"🗑️ Start message {message_id} deleted after 1 minute"
        )

    except Exception as e:

        print(
            f"⚠️ Could not delete start message "
            f"{message_id}: {e}"
        )


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

    # ==================================================
    # ACCESS TOKEN FLOW
    # ==================================================

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
        # GRANT 8-HOUR USER ACCESS
        # ----------------------------------------------

        from datetime import datetime, timedelta, timezone

        verified_at = datetime.now(timezone.utc)

        access_until = (
            verified_at
            + timedelta(hours=8)
        )

        access_granted = grant_user_access(
            user_id=message.from_user.id,
            verified_at=verified_at.isoformat(),
            access_until=access_until.isoformat()
        )

        if not access_granted:

            await message.reply_text(
                "❌ **Could not activate file access.**\n\n"
                "Please try the verification again."
            )

            return

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

        file_message_id = result["message_id"]

        # ----------------------------------------------
        # CONSUME TOKEN
        # ----------------------------------------------

        consume_access_token(token)

        # ----------------------------------------------
        # SUCCESS ALERT
        # ----------------------------------------------

        alert_message = await message.reply_text(
            "✅ **File sent successfully!**\n\n"
            "⏱️ This file will be automatically deleted "
            "from this chat after **15 minutes**.\n\n"
            "So Kindly Share This File To Your Friends "
            "Or Saved Message..."
        )

        # ----------------------------------------------
        # CALCULATE DELETE TIME
        # ----------------------------------------------

        delete_at = (
            datetime.now(timezone.utc)
            + timedelta(minutes=15)
        ).isoformat()

        # ----------------------------------------------
        # SCHEDULE ALERT DELETION
        # ----------------------------------------------

        scheduled = schedule_file_deletion(
            chat_id=message.from_user.id,
            message_id=alert_message.id,
            delete_at=delete_at
        )

        if scheduled:

            print(
                f"⏱️ Success alert message "
                f"{alert_message.id} "
                f"scheduled for deletion at "
                f"{delete_at}"
            )

        else:

            print(
                "⚠️ WARNING: "
                "Could not schedule success alert deletion."
            )

        print(
            f"✅ Access token completed: "
            f"user={message.from_user.id}, "
            f"file={file_db_id}, "
            f"file_message={file_message_id}, "
            f"alert_message={alert_message.id}"
        )

        # ==================================================
        # VERY IMPORTANT
        # ==================================================
        # Do not continue to normal /start.
        # This prevents the deep-link from being treated
        # as a normal start/search request.

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

    # --------------------------------------------------
    # SEND NORMAL START MESSAGE
    # --------------------------------------------------

    start_message = await message.reply_text(
        "🤖 **Welcome to AutoFilterPro!**\n\n"
        "🔎 Search and find files quickly.\n\n"
        "Use the button below to start searching.",
        reply_markup=keyboard
    )

    # --------------------------------------------------
    # DELETE NORMAL START MESSAGE AFTER 1 MINUTE
    # --------------------------------------------------

    import asyncio

    asyncio.create_task(
        delete_after_one_minute(
            client=client,
            chat_id=message.chat.id,
            message_id=start_message.id
        )
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