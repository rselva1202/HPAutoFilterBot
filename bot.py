import os
from pathlib import Path

PYROGRAM_WORKDIR = Path(
    os.getenv(
        "PYROGRAM_WORKDIR",
        str(Path(__file__).resolve().parent)
    )
)

PYROGRAM_WORKDIR.mkdir(
    parents=True,
    exist_ok=True
)

import asyncio
from datetime import datetime, timezone

from database import (
    get_due_file_deletions,
    remove_scheduled_deletion
)

from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler

from config import API_ID, API_HASH, BOT_TOKEN, STORAGE_CHANNEL

from handlers.storage import storage_handler
from handlers.search import register_search_handler
from handlers.file_delivery import register_file_delivery_handler
from handlers.start import register_start_handler
from handlers.ui import register_ui_handler


# ==================================================
# STORAGE CHANNELS
# ==================================================

STORAGE_CHANNELS = [
    -1003955875189,
    -1003552500659
]


# --------------------------------------------------
# CREATE CLIENT
# --------------------------------------------------

app = Client(
    "AutoFilterPro",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# --------------------------------------------------
# STORAGE HANDLER
# --------------------------------------------------

app.add_handler(
    MessageHandler(
        storage_handler,
        filters.channel & filters.chat(STORAGE_CHANNELS)
    )
)


# --------------------------------------------------
# START HANDLER
# --------------------------------------------------

register_start_handler(app)


# --------------------------------------------------
# SEARCH HANDLER
# --------------------------------------------------

register_search_handler(app)


# --------------------------------------------------
# FILE DELIVERY HANDLER
# --------------------------------------------------

register_file_delivery_handler(app)


# --------------------------------------------------
# UI HANDLER
# --------------------------------------------------

register_ui_handler(app)


# ==================================================
# PERSISTENT FILE DELETION WORKER
# ==================================================

async def scheduled_file_deletion_worker(app):

    print("🧹 Scheduled file deletion worker started")

    while True:

        try:

            current_time = datetime.now(
                timezone.utc
            ).isoformat()

            due_files = get_due_file_deletions(
                current_time
            )

            for deletion in due_files:

                deletion_id = deletion[0]
                chat_id = deletion[1]
                message_id = deletion[2]

                try:

                    await app.delete_messages(
                        chat_id=chat_id,
                        message_ids=message_id
                    )

                    print(
                        f"🗑️ Persistent deletion completed: "
                        f"chat={chat_id}, "
                        f"message={message_id}"
                    )

                except Exception as error:

                    print(
                        f"⚠️ Could not delete message "
                        f"{message_id} "
                        f"from {chat_id}: {error}"
                    )

                finally:

                    remove_scheduled_deletion(
                        deletion_id
                    )

        except Exception as error:

            print(
                "❌ Scheduled deletion worker error:",
                error
            )

        # Check every 30 seconds
        await asyncio.sleep(30)


# ==================================================
# START BOT
# ==================================================

async def main():

    print("=" * 50)
    print("🚀 AutoFilterPro")
    print("Starting bot...")
    print("=" * 50)

    await app.start()

    asyncio.create_task(
        scheduled_file_deletion_worker(app)
    )

    # --------------------------------------------------
    # CHECK BOTH STORAGE CHANNELS
    # --------------------------------------------------

    storage_connected = 0

    for channel_id in STORAGE_CHANNELS:

        try:

            chat = await app.get_chat(channel_id)

            print()
            print("✅ STORAGE CHANNEL CONNECTED")
            print("Channel Name :", chat.title)
            print("Channel ID   :", chat.id)

            storage_connected += 1

        except Exception as error:

            print()
            print("❌ STORAGE CHANNEL ERROR")
            print("Channel ID   :", channel_id)
            print(error)

    # --------------------------------------------------
    # STORAGE CONNECTION RESULT
    # --------------------------------------------------

    print()
    print(
        f"📦 Storage channels connected: "
        f"{storage_connected}/{len(STORAGE_CHANNELS)}"
    )

    if storage_connected == 0:

        print("❌ No storage channels connected.")

        await app.stop()

        return

    print()
    print("🤖 Bot is running...")
    print("📡 Waiting for files and searches...")

    await idle()

    await app.stop()


app.run(main())