import sqlite3

from database import DATABASE_PATH
from utils.metadata_parser import parse_metadata


print("=" * 60)
print("🔄 AUTOFILTERPRO METADATA REFRESH")
print("=" * 60)


connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()


# --------------------------------------------------
# GET ALL FILES
# --------------------------------------------------

rows = cursor.execute("""
    SELECT id, file_name
    FROM files
""").fetchall()


print(f"📦 Files found: {len(rows)}")
print()


updated = 0
failed = 0


# --------------------------------------------------
# REFRESH METADATA
# --------------------------------------------------

for file_id, file_name in rows:

    try:

        metadata = parse_metadata(file_name)

        title = metadata.get("title", "")
        year = metadata.get("year")
        language = metadata.get("language", "")
        quality = metadata.get("quality", "")
        season = metadata.get("season")
        episode = metadata.get("episode")

        cursor.execute("""
            UPDATE files
            SET
                title = ?,
                year = ?,
                language = ?,
                quality = ?,
                season = ?,
                episode = ?
            WHERE id = ?
        """, (
            title,
            year,
            language,
            quality,
            season,
            episode,
            file_id
        ))

        updated += 1

        print(
            f"✅ {file_id}: {title}"
            f" | {year or '-'}"
            f" | {quality or '-'}"
            f" | {language or '-'}"
        )

    except Exception as error:

        failed += 1

        print(
            f"❌ {file_id}: {file_name}"
        )

        print(
            f"   Error: {error}"
        )


# --------------------------------------------------
# SAVE
# --------------------------------------------------

connection.commit()


# --------------------------------------------------
# CLOSE
# --------------------------------------------------

connection.close()


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print()
print("=" * 60)
print("📊 METADATA REFRESH COMPLETED")
print("=" * 60)

print("Total files :", len(rows))
print("Updated     :", updated)
print("Failed      :", failed)

print("=" * 60)