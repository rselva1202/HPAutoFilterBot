import sqlite3

from pathlib import Path

from utils.metadata_parser import parse_metadata


# ==================================================
# DATABASE
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "autofilter.db"


# ==================================================
# CONNECT
# ==================================================

connection = sqlite3.connect(DATABASE_PATH)

cursor = connection.cursor()


# ==================================================
# GET ALL FILES
# ==================================================

cursor.execute("""
SELECT
    id,
    file_name
FROM files
WHERE file_name IS NOT NULL
""")

files = cursor.fetchall()


print("=" * 60)
print("🔄 METADATA UPDATE")
print("=" * 60)

print(f"Files found: {len(files)}")

print()


# ==================================================
# UPDATE EACH FILE
# ==================================================

updated = 0


for db_id, file_name in files:

    metadata = parse_metadata(file_name)

    title = metadata["title"]
    year = metadata["year"]
    language = metadata["language"]
    quality = metadata["quality"]
    season = metadata["season"]
    episode = metadata["episode"]

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
        db_id
    ))

    updated += 1

    print(f"✅ {file_name}")
    print(f"   Title    : {title}")
    print(f"   Year     : {year}")
    print(f"   Language : {language}")
    print(f"   Quality  : {quality}")
    print(f"   Season   : {season}")
    print(f"   Episode  : {episode}")
    print()


# ==================================================
# SAVE
# ==================================================

connection.commit()


# ==================================================
# CLOSE
# ==================================================

connection.close()


print("=" * 60)
print("✅ METADATA UPDATE COMPLETED")
print("=" * 60)

print(f"Updated files: {updated}")