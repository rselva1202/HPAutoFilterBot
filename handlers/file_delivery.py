from pyrogram import filters
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import (
    get_file_by_db_id,
    schedule_file_deletion
)

from utils.access_tokens import generate_access_token
from utils.arolinks import create_access_link


# ==================================================
# ACTUAL FILE DELIVERY
# ==================================================

async def deliver_file(client, user_id, db_id):

    file_data = get_file_by_db_id(db_id)

    if not file_data:
        return False, "File not found."

    # Database structure:
    #
    # 0  id
    # 1  file_id
    # 2  file_name
    # 3  caption
    # 4  file_type
    # 5  file_size
    # 6  message_id
    # 7  storage_channel
    # 8  created_at
    # 9  title
    # 10 year
    # 11 language
    # 12 quality
    # 13 season
    # 14 episode

    file_name = file_data[2]
    message_id = file_data[6]
    storage_channel = file_data[7]

    try:

        print("\n" + "=" * 50)
        print("📤 FILE DELIVERY")
        print("User ID       :", user_id)
        print("Database ID   :", db_id)
        print("File Name     :", file_name)
        print("Storage       :", storage_channel)
        print("Message ID    :", message_id)
        print("=" * 50)

        # --------------------------------------------------
        # COPY FILE FROM STORAGE CHANNEL TO USER
        # --------------------------------------------------

        delivered_message = await client.copy_message(
            chat_id=user_id,
            from_chat_id=storage_channel,
            message_id=message_id
        )

        if not delivered_message:
            return False, "File could not be delivered."

        # --------------------------------------------------
        # CALCULATE DELETE TIME
        # --------------------------------------------------

        from datetime import datetime, timedelta, timezone

        delete_at = (
            datetime.now(timezone.utc)
            + timedelta(minutes=15)
        ).isoformat()

        # --------------------------------------------------
        # SAVE DELETE TASK TO SQLITE
        # --------------------------------------------------

        scheduled = schedule_file_deletion(
            chat_id=user_id,
            message_id=delivered_message.id,
            delete_at=delete_at
        )

        if scheduled:

            print(
                f"⏱️ File message "
                f"{delivered_message.id} "
                f"scheduled for deletion at "
                f"{delete_at}"
            )

        else:

            print(
                "⚠️ WARNING: "
                "Could not save deletion schedule."
            )

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        print(
            f"✅ File delivered successfully: "
            f"{file_name} → {user_id}"
        )

        return True, file_name

    except Exception as error:

        print("\n❌ FILE DELIVERY ERROR")
        print("File:", file_name)
        print("Error:", error)

        return False, str(error)


# ==================================================
# FILE DELIVERY CALLBACK
# ==================================================

async def get_file_handler(client, callback_query):

    data = callback_query.data

    if not data.startswith("getfile:"):
        return

    # --------------------------------------------------
    # GET DATABASE ID
    # --------------------------------------------------

    try:

        db_id = int(
            data.split(":", 1)[1]
        )

    except (ValueError, IndexError):

        await callback_query.answer(
            "❌ Invalid file request.",
            show_alert=True
        )

        return

    # --------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------

    file_data = get_file_by_db_id(db_id)

    if not file_data:

        await callback_query.answer(
            "❌ File not found.",
            show_alert=True
        )

        return

    # --------------------------------------------------
    # USER
    # --------------------------------------------------

    user_id = callback_query.from_user.id

    # --------------------------------------------------
    # CREATE NEW ACCESS TOKEN
    # --------------------------------------------------

    try:

        token = generate_access_token(
            user_id=user_id,
            file_db_id=db_id
        )

        print(
            f"🔑 New access token generated "
            f"for user {user_id}, file {db_id}"
        )

    except Exception as error:

        print(
            "❌ TOKEN GENERATION ERROR:",
            error
        )

        await callback_query.answer(
            "❌ Could not create access link.",
            show_alert=True
        )

        return

    # --------------------------------------------------
    # GET BOT USERNAME
    # --------------------------------------------------

    try:

        bot_info = await client.get_me()

        bot_username = bot_info.username

        if not bot_username:

            raise ValueError(
                "Bot username is not available."
            )

    except Exception as error:

        print(
            "❌ BOT USERNAME ERROR:",
            error
        )

        await callback_query.answer(
            "❌ Bot configuration error.",
            show_alert=True
        )

        return

    # --------------------------------------------------
    # CREATE NEW AROLINKS URL
    # --------------------------------------------------

    try:

        short_url = create_access_link(
            bot_username=bot_username,
            token=token
        )

        print(
            f"🔗 New AroLinks URL created "
            f"for user {user_id}, file {db_id}"
        )

    except Exception as error:

        print(
            "❌ AROLINKS ERROR:",
            error
        )

        await callback_query.answer(
            "❌ Could not create access link.",
            show_alert=True
        )

        return

    # --------------------------------------------------
    # SHOW AROLINKS BUTTON
    # --------------------------------------------------

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔐 Get File",
                    url=short_url
                )
            ]
        ]
    )

    file_name = file_data[2]

    await callback_query.message.reply_text(

        "🔐 **Complete the access step first.**\n\n"

        f"📁 **{file_name}**\n\n"

        "After completing the access step, "
        "Telegram will automatically open "
        "the file access.",

        reply_markup=keyboard
    )

    # --------------------------------------------------
    # ANSWER CALLBACK
    # --------------------------------------------------

    await callback_query.answer(
        "🔐 Access link created!"
    )

    print(
        f"🔗 AroLinks link created for "
        f"user {user_id}, file {db_id}"
    )


# ==================================================
# REGISTER HANDLER
# ==================================================

def register_file_delivery_handler(app):

    app.add_handler(
        CallbackQueryHandler(
            get_file_handler,
            filters.regex(r"^getfile:")
        )
    )

    print(
        "✅ File delivery handler registered"
    )