from config import STORAGE_CHANNEL

from database import add_file, file_exists

from utils.metadata_parser import parse_metadata


async def storage_handler(client, message):

    print("\n" + "=" * 50)
    print("📩 CHANNEL MESSAGE RECEIVED")
    print("Channel Name :", message.chat.title)
    print("Channel ID   :", message.chat.id)
    print("Configured ID:", STORAGE_CHANNEL)
    print("Message ID   :", message.id)
    print("=" * 50)

    # --------------------------------------------------
    # CHECK STORAGE CHANNEL
    # --------------------------------------------------

    if message.chat.id != STORAGE_CHANNEL:

        print("⚠️ Not our storage channel.")

        return

    # --------------------------------------------------
    # GET MEDIA
    # --------------------------------------------------

    media = (
        message.document
        or message.video
        or message.audio
        or message.photo
    )

    if not media:

        print("⚠️ Message contains no supported file.")

        return

    # --------------------------------------------------
    # FILE ID
    # --------------------------------------------------

    file_id = media.file_id

    # --------------------------------------------------
    # DUPLICATE CHECK
    # --------------------------------------------------

    if file_exists(file_id):

        print("⚠️ File already indexed.")

        return

    # --------------------------------------------------
    # FILE NAME
    # --------------------------------------------------

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

    # --------------------------------------------------
    # CAPTION
    # --------------------------------------------------

    caption = message.caption or ""

    # --------------------------------------------------
    # FILE SIZE
    # --------------------------------------------------

    file_size = getattr(
        media,
        "file_size",
        0
    ) or 0

    # --------------------------------------------------
    # FILE TYPE
    # --------------------------------------------------

    file_type = media.__class__.__name__

    # --------------------------------------------------
    # PARSE METADATA
    # --------------------------------------------------

    metadata = parse_metadata(file_name)

    title = metadata["title"]

    year = metadata["year"]

    language = metadata["language"]

    quality = metadata["quality"]

    season = metadata["season"]

    episode = metadata["episode"]

    print()
    print("📊 PARSED METADATA")
    print("Title    :", title)
    print("Year     :", year)
    print("Language :", language)
    print("Quality  :", quality)
    print("Season   :", season)
    print("Episode  :", episode)

    # --------------------------------------------------
    # SAVE TO DATABASE
    # --------------------------------------------------

    success = add_file(

        file_id=file_id,

        file_name=file_name,

        caption=caption,

        file_type=file_type,

        file_size=file_size,

        message_id=message.id,

        storage_channel=message.chat.id,

        title=title,

        year=year,

        language=language,

        quality=quality,

        season=season,

        episode=episode
    )

    # --------------------------------------------------
    # RESULT
    # --------------------------------------------------

    if success:

        print()
        print("✅ INDEXED SUCCESSFULLY")
        print("File:", file_name)

    else:

        print()
        print("❌ FAILED TO INDEX FILE")