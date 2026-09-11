import sqlite3
from pathlib import Path

from utils.metadata_parser import parse_metadata


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "autofilter.db"


# --------------------------------------------------
# REPAIR METADATA
# --------------------------------------------------

def repair_metadata():

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    # Get all existing files
    cursor.execute("""
        SELECT id, file_name
        FROM files
        ORDER BY id
    """)

    files = cursor.fetchall()

    if not files:

        print("No files found in database.")

        connection.close()

        return

    print("=" * 60)
    print("🔧 METADATA REPAIR")
    print("=" * 60)

    updated = 0

    for db_id, file_name in files:

        if not file_name:

            print(f"⚠️ ID {db_id}: No filename")

            continue

        # Parse filename
        metadata = parse_metadata(file_name)

        # Update database
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
            metadata["title"],
            metadata["year"],
            metadata["language"],
            metadata["quality"],
            metadata["season"],
            metadata["episode"],
            db_id
        ))

        updated += 1

        print()
        print(f"ID:       {db_id}")
        print(f"File:     {file_name}")
        print(f"Title:    {metadata['title']}")
        print(f"Year:     {metadata['year']}")
        print(f"Language: {metadata['language']}")
        print(f"Quality:  {metadata['quality']}")
        print(f"Season:   {metadata['season']}")
        print(f"Episode:  {metadata['episode']}")

    connection.commit()

    connection.close()

    print()
    print("=" * 60)
    print(f"✅ REPAIR COMPLETED")
    print(f"Files processed: {updated}")
    print("=" * 60)


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":

    repair_metadata()