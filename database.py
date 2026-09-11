import sqlite3
from pathlib import Path


# ==================================================
# DATABASE CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "autofilter.db"


# ==================================================
# DATABASE CONNECTION
# ==================================================

connection = sqlite3.connect(
    DATABASE_PATH,
    check_same_thread=False
)

cursor = connection.cursor()


# ==================================================
# FILES TABLE
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    file_id TEXT NOT NULL UNIQUE,

    file_name TEXT,

    caption TEXT,

    file_type TEXT,

    file_size INTEGER DEFAULT 0,

    message_id INTEGER,

    storage_channel INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    title TEXT DEFAULT '',

    year INTEGER,

    language TEXT DEFAULT '',

    quality TEXT DEFAULT '',

    season INTEGER,

    episode INTEGER
)
""")

connection.commit()


# ==================================================
# ACCESS TOKENS TABLE
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS access_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    token TEXT NOT NULL UNIQUE,

    user_id INTEGER NOT NULL,

    file_db_id INTEGER NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    expires_at TIMESTAMP NOT NULL,

    used INTEGER DEFAULT 0
)
""")

connection.commit()


# ==================================================
# SCHEDULED FILE DELETIONS TABLE
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS scheduled_deletions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    chat_id INTEGER NOT NULL,

    message_id INTEGER NOT NULL,

    delete_at TIMESTAMP NOT NULL,

    UNIQUE(chat_id, message_id)
)
""")

connection.commit()


# ==================================================
# USER ACCESS TABLE
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_access (
    user_id INTEGER PRIMARY KEY,

    unlocked_until TIMESTAMP NOT NULL
)
""")

connection.commit()


# ==================================================
# ADD FILE
# ==================================================

def add_file(
    file_id,
    file_name,
    caption,
    file_type,
    file_size,
    message_id,
    storage_channel,
    title="",
    year=None,
    language="",
    quality="",
    season=None,
    episode=None
):
    try:

        cursor.execute("""
        INSERT INTO files (
            file_id,
            file_name,
            caption,
            file_type,
            file_size,
            message_id,
            storage_channel,
            title,
            year,
            language,
            quality,
            season,
            episode
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(file_id),
            str(file_name),
            str(caption),
            str(file_type),
            int(file_size),
            int(message_id),
            int(storage_channel),
            str(title),
            year,
            str(language),
            str(quality),
            season,
            episode
        ))

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        print("⚠️ File already exists.")

        return False

    except Exception as error:

        print("❌ Database error:", error)

        return False


# ==================================================
# CHECK FILE EXISTS
# ==================================================

def file_exists(file_id):

    cursor.execute("""
    SELECT id
    FROM files
    WHERE file_id = ?
    """, (
        str(file_id),
    ))

    result = cursor.fetchone()

    return result is not None


# ==================================================
# SEARCH FILES
# ==================================================

def search_files(keyword):

    keyword = keyword.strip()

    if not keyword:
        return []

    # --------------------------------------------------
    # CHECK IF SEARCH CONTAINS A YEAR
    # --------------------------------------------------

    import re

    year_match = re.search(
        r"\b(19\d{2}|20\d{2})\b",
        keyword
    )

    year = None

    if year_match:

        year = int(year_match.group(1))

        title_keyword = re.sub(
            r"\b(19\d{2}|20\d{2})\b",
            "",
            keyword
        ).strip()

    else:

        title_keyword = keyword


    # --------------------------------------------------
    # SEARCH WITH YEAR
    # --------------------------------------------------

    if year:

        search_pattern = f"%{title_keyword}%"

        cursor.execute("""
        SELECT
            id,
            file_id,
            file_name,
            caption,
            file_type,
            file_size,
            message_id,
            storage_channel,
            created_at,
            title,
            year,
            language,
            quality,
            season,
            episode
        FROM files
        WHERE
            (
                title LIKE ?
                OR file_name LIKE ?
                OR caption LIKE ?
            )
            AND year = ?
        ORDER BY id DESC
        """, (
            search_pattern,
            search_pattern,
            search_pattern,
            year
        ))

    # --------------------------------------------------
    # SEARCH WITHOUT YEAR
    # --------------------------------------------------

    else:

        search_pattern = f"%{keyword}%"

        cursor.execute("""
        SELECT
            id,
            file_id,
            file_name,
            caption,
            file_type,
            file_size,
            message_id,
            storage_channel,
            created_at,
            title,
            year,
            language,
            quality,
            season,
            episode
        FROM files
        WHERE
            title LIKE ?
            OR file_name LIKE ?
            OR caption LIKE ?
        ORDER BY id DESC
        """, (
            search_pattern,
            search_pattern,
            search_pattern
        ))

    return cursor.fetchall()


# ==================================================
# GET FILE BY FILE ID
# ==================================================

def get_file(file_id):

    cursor.execute("""
    SELECT *
    FROM files
    WHERE file_id = ?
    """, (
        str(file_id),
    ))

    return cursor.fetchone()


# ==================================================
# GET FILE BY DATABASE ID
# ==================================================

def get_file_by_db_id(db_id):

    cursor.execute("""
    SELECT *
    FROM files
    WHERE id = ?
    """, (
        int(db_id),
    ))

    return cursor.fetchone()


# ==================================================
# COUNT FILES
# ==================================================

def get_file_count():

    cursor.execute("""
    SELECT COUNT(*)
    FROM files
    """)

    result = cursor.fetchone()

    return result[0]


# ==================================================
# ACCESS TOKEN FUNCTIONS
# ==================================================

def create_access_token(
    token,
    user_id,
    file_db_id,
    expires_at
):
    """
    Store a new access token.
    """

    try:

        cursor.execute("""
        INSERT INTO access_tokens (
            token,
            user_id,
            file_db_id,
            expires_at,
            used
        )
        VALUES (?, ?, ?, ?, 0)
        """, (
            str(token),
            int(user_id),
            int(file_db_id),
            expires_at
        ))

        connection.commit()

        return True

    except Exception as error:

        print(
            "❌ Error creating access token:",
            error
        )

        return False


def get_access_token(token):
    """
    Retrieve an access token.
    """

    cursor.execute("""
    SELECT
        id,
        token,
        user_id,
        file_db_id,
        created_at,
        expires_at,
        used
    FROM access_tokens
    WHERE token = ?
    """, (
        str(token),
    ))

    return cursor.fetchone()


def mark_access_token_used(token):
    """
    Mark an access token as used.
    """

    try:

        cursor.execute("""
        UPDATE access_tokens
        SET used = 1
        WHERE token = ?
        """, (
            str(token),
        ))

        connection.commit()

        return True

    except Exception as error:

        print(
            "❌ Error marking access token:",
            error
        )

        return False


# ==================================================
# SCHEDULE FILE DELETION
# ==================================================

def schedule_file_deletion(
    chat_id,
    message_id,
    delete_at
):
    """
    Store a file message that must be deleted later.
    """

    try:

        cursor.execute("""
        INSERT OR REPLACE INTO scheduled_deletions (
            chat_id,
            message_id,
            delete_at
        )
        VALUES (?, ?, ?)
        """, (
            int(chat_id),
            int(message_id),
            delete_at
        ))

        connection.commit()

        print(
            f"⏱️ Deletion scheduled: "
            f"chat={chat_id}, "
            f"message={message_id}, "
            f"delete_at={delete_at}"
        )

        return True

    except Exception as error:

        print(
            "❌ Error scheduling file deletion:",
            error
        )

        return False


# ==================================================
# GET DUE FILE DELETIONS
# ==================================================

def get_due_file_deletions(current_time):
    """
    Get all file messages whose deletion time has arrived.
    """

    try:

        cursor.execute("""
        SELECT
            id,
            chat_id,
            message_id,
            delete_at
        FROM scheduled_deletions
        WHERE delete_at <= ?
        ORDER BY delete_at ASC
        """, (
            current_time,
        ))

        return cursor.fetchall()

    except Exception as error:

        print(
            "❌ Error getting scheduled deletions:",
            error
        )

        return []


# ==================================================
# REMOVE DELETION RECORD
# ==================================================

def remove_scheduled_deletion(deletion_id):
    """
    Remove a completed deletion task from the database.
    """

    try:

        cursor.execute("""
        DELETE FROM scheduled_deletions
        WHERE id = ?
        """, (
            int(deletion_id),
        ))

        connection.commit()

        return True

    except Exception as error:

        print(
            "❌ Error removing deletion record:",
            error
        )

        return False


# ==================================================
# USER ACCESS FUNCTIONS
# ==================================================

def set_user_access(
    user_id,
    unlocked_until
):

    cursor.execute("""
    INSERT OR REPLACE INTO user_access (
        user_id,
        unlocked_until
    )
    VALUES (?, ?)
    """, (
        int(user_id),
        unlocked_until
    ))

    connection.commit()


def get_user_access(user_id):

    cursor.execute("""
    SELECT unlocked_until
    FROM user_access
    WHERE user_id = ?
    """, (
        int(user_id),
    ))

    row = cursor.fetchone()

    if not row:
        return None

    return row[0]


def remove_user_access(user_id):

    cursor.execute("""
    DELETE FROM user_access
    WHERE user_id = ?
    """, (
        int(user_id),
    ))

    connection.commit()


# ==================================================
# CLOSE DATABASE
# ==================================================

def close_database():

    connection.close()