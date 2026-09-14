from pyrogram import filters
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import (
    get_file_by_db_id,
    schedule_file_deletion,
    has_active_user_access
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
        # SAVE FILE DELETE TASK
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
                "Could not save file deletion schedule."
            )

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        print(
            f"✅ File delivered successfully: "
            f"{file_name} → {user_id}"
        )

        # Return BOTH file name and delivered message ID
        return True, {
            "file_name": file_name,
            "message_id": delivered_message.id
        }

    except Exception as error:

        print("\n❌ FILE DELIVERY ERROR")
        print("File:", file_name)
        print("Error:", error)

        return False, str(error)


# ==================================================
# FILE DELIVERY CALLBACK
# ==================================================

async def _delete_message_after_minute(chat_id, message_id):
    from datetime import datetime, timedelta, timezone

    delete_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=1)
    ).isoformat()

    schedule_file_deletion(
        chat_id=chat_id,
        message_id=message_id,
        delete_at=delete_at
    )


async def _send_file_deletion_alert(client, chat_id):
    """Send the 15-minute deletion notice and schedule it for deletion too."""
    from datetime import datetime, timedelta, timezone

    alert = await client.send_message(
        chat_id=chat_id,
        text=(
            "✅ **File sent successfully!**\n\n"
            "⏱️ This file will be automatically deleted from this chat "
            "after 15 minutes.\n\n"
            "So Kindly Share This File To Your Friends Or Saved Message..."
        )
    )

    delete_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=15)
    ).isoformat()

    schedule_file_deletion(
        chat_id=chat_id,
        message_id=alert.id,
        delete_at=delete_at
    )

    return alert


# ==================================================
# FILE DELIVERY CALLBACK
# ==================================================

async def get_file_handler(client, callback_query):

    data = callback_query.data

    if not data.startswith("getfile:"):
        return

    try:
        db_id = int(data.split(":", 1)[1])
    except (ValueError, IndexError):
        await callback_query.answer(
            "❌ Invalid file request.",
            show_alert=True
        )
        return

    file_data = get_file_by_db_id(db_id)

    if not file_data:
        await callback_query.answer(
            "❌ File not found.",
            show_alert=True
        )
        return

    user_id = callback_query.from_user.id

    # --------------------------------------------------
    # ALREADY VERIFIED -> SEND DIRECTLY
    # --------------------------------------------------

    if has_active_user_access(user_id):

        success, result = await deliver_file(
            client=client,
            user_id=user_id,
            db_id=db_id
        )

        if success:
            await _send_file_deletion_alert(
                client=client,
                chat_id=user_id
            )

            await callback_query.answer(
                "✅ File sent!",
                show_alert=False
            )
        else:
            await callback_query.answer(
                "❌ Could not send this file.",
                show_alert=True
            )

        return

    # --------------------------------------------------
    # NOT VERIFIED -> CREATE VERIFICATION LINK
    # --------------------------------------------------

    try:
        token = generate_access_token(
            user_id=user_id,
            file_db_id=db_id
        )
    except Exception as error:
        print("❌ TOKEN GENERATION ERROR:", error)
        await callback_query.answer(
            "❌ Could not create verification link.",
            show_alert=True
        )
        return

    try:
        bot_info = await client.get_me()
        bot_username = bot_info.username

        if not bot_username:
            raise ValueError("Bot username is not available.")

        short_url = create_access_link(
            bot_username=bot_username,
            token=token
        )

    except Exception as error:
        print("❌ AROLINKS ERROR:", error)
        await callback_query.answer(
            "❌ Could not create verification link.",
            show_alert=True
        )
        return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔐 VERIFY",
                    url=short_url
                )
            ]
        ]
    )

    file_name = file_data[2]

    verification_message = await callback_query.message.reply_text(
        "🔐 **Verify for 8 hours and get any files for free.**\n\n"
        f"📁 **{file_name}**\n\n"
        "Complete the verification once. After that, you can get any files "
        "without verifying again for the next **8 hours**.",
        reply_markup=keyboard
    )

    await _delete_message_after_minute(
        chat_id=callback_query.message.chat.id,
        message_id=verification_message.id
    )

    await callback_query.answer(
        "🔐 Verification required."
    )

    print(
        f"🔗 Verification link created for "
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