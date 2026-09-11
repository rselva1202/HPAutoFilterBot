import sqlite3


DB_NAME = "autofilter.db"


def migrate_database():

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(files)")
    existing_columns = {
        column[1]
        for column in cursor.fetchall()
    }

    new_columns = {
        "title": "TEXT DEFAULT ''",
        "year": "INTEGER",
        "language": "TEXT DEFAULT ''",
        "quality": "TEXT DEFAULT ''",
        "season": "INTEGER",
        "episode": "INTEGER",
    }

    added = []

    for column_name, column_type in new_columns.items():

        if column_name not in existing_columns:

            cursor.execute(
                f"ALTER TABLE files ADD COLUMN {column_name} {column_type}"
            )

            added.append(column_name)

    connection.commit()

    # Show final structure
    cursor.execute("PRAGMA table_info(files)")
    columns = cursor.fetchall()

    print("=" * 50)
    print("DATABASE MIGRATION")
    print("=" * 50)

    if added:

        print("Added columns:")

        for column in added:
            print(f"  ✅ {column}")

    else:

        print("✅ Database was already up to date.")

    print()
    print("Current files table:")

    for column in columns:
        print(f"  {column[1]} → {column[2]}")

    connection.close()

    print()
    print("✅ Database migration completed successfully.")


if __name__ == "__main__":
    migrate_database()