from pyrogram import Client

from config import API_ID, API_HASH, STORAGE_CHANNEL
from database import add_file, file_exists
from utils.metadata_parser import parse_metadata


# ============================================================
# USER ACCOUNT SCANNER
# ============================================================

app = Client(
    "AutoFilterUserScanner",
    api_id=API_ID,
    api_hash=API_HASH
)


# ============================================================
# FIND STORAGE CHANNEL
# ============================================================

async def find_storage_channel():

    print("🔎 Looking for storage channel...")
    print()

    target_id = int(STORAGE_CHANNEL)

    async for dialog in app.get_dialogs():

        chat = dialog.chat

        if int(chat.id) == target_id:

            print("✅ Storage channel found!")
            print("Channel Name:", chat.title)
            print("Channel ID  :", chat.id)
            print()

            return chat

    return None


# ============================================================
# SCAN STORAGE
# ============================================================

async def scan_storage():

    print("=" * 60)
    print("📦 AUTOFILTERPRO EXISTING FILE SCANNER")
    print("=" * 60)

    total_messages = 0
    media_messages = 0
    already_indexed = 0
    newly_indexed = 0
    failed = 0

    try:

        await app.start()

        print("✅ Telegram user account connected")
        print()

        chat = await find_storage_channel()

        if chat is None:

            print("=" * 60)
            print("❌ STORAGE CHANNEL NOT FOUND")
            print("=" * 60)

            return

        print("🔎 Scanning existing messages...")
        print("-" * 60)

        async for message in app.get_chat_history(chat.id):

            total_messages += 1

            # ------------------------------------------------
            # FIND MEDIA
            # ------------------------------------------------

            media = (
                message.document
                or message.video
                or message.audio
                or message.photo
            )

            if not media:
                continue

            media_messages += 1

            # ------------------------------------------------
            # FILE ID
            # ------------------------------------------------

            file_id = str(media.file_id)

            # ------------------------------------------------
            # DUPLICATE CHECK
            # ------------------------------------------------

            if file_exists(file_id):

                already_indexed += 1
                continue

            # ------------------------------------------------
            # FILE NAME
            # ------------------------------------------------

            file_name = getattr(
                media,
                "file_name",
                None
            )

            if not file_name:

                if message.photo:

                    file_name = "Photo"

                elif message.video:

                    file_name = "Video"

                elif message.audio:

                    file_name = "Audio"

                else:

                    file_name = "Unknown File"

            file_name = str(file_name)

            # ------------------------------------------------
            # CAPTION
            # ------------------------------------------------

            caption = str(
                message.caption or ""
            )

            # ------------------------------------------------
            # FILE SIZE
            # ------------------------------------------------

            file_size = getattr(
                media,
                "file_size",
                0
            ) or 0

            file_size = int(file_size)

            # ------------------------------------------------
            # FILE TYPE
            # ------------------------------------------------

            file_type = str(
                media.__class__.__name__
            )

            # ------------------------------------------------
            # MESSAGE ID
            # ------------------------------------------------

            message_id = int(
                message.id
            )

            # ------------------------------------------------
            # CHANNEL ID
            # ------------------------------------------------

            storage_channel = int(
                chat.id
            )

            # ------------------------------------------------
            # DEBUG
            # ------------------------------------------------

            print(
                f"🔄 Processing: {file_name}"
            )

            # ------------------------------------------------
            # PARSE METADATA
            # ------------------------------------------------
            
            metadata = parse_metadata(file_name)
            title = metadata.get("title", "")
            year = metadata.get("year")
            language = metadata.get("language", "")
            quality = metadata.get("quality", "")
            season = metadata.get("season")
            episode = metadata.get("episode")

            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            try:

                success = add_file(
                    file_id=file_id,
                    file_name=file_name,
                    caption=caption,
                    file_type=file_type,
                    file_size=file_size,
                    message_id=message_id,
                    storage_channel=storage_channel,
                    title=title,
                    year=year,
                    language=language,
                    quality=quality,
                    season=season,
                    episode=episode
                )

                if success:

                    newly_indexed += 1

                    print(
                        f"   ✅ INDEXED"
                    )

                else:

                    failed += 1

                    print(
                        f"   ⚠️ DATABASE INSERT FAILED"
                    )

            except Exception as error:

                failed += 1

                print(
                    f"   ❌ ERROR: {error}"
                )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        print()
        print("=" * 60)
        print("📊 SCAN COMPLETED")
        print("=" * 60)

        print(
            "Total messages scanned :",
            total_messages
        )

        print(
            "Media messages found   :",
            media_messages
        )

        print(
            "Already indexed        :",
            already_indexed
        )

        print(
            "Newly indexed          :",
            newly_indexed
        )

        print(
            "Failed                 :",
            failed
        )

        print("=" * 60)

    except Exception as error:

        print()
        print("=" * 60)
        print("❌ SCANNER ERROR")
        print("=" * 60)

        print(
            type(error).__name__,
            ":",
            error
        )

    finally:

        if app.is_connected:

            await app.stop()

        print()
        print("🔴 Scanner stopped.")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        scan_storage()
    )