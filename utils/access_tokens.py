import secrets
from datetime import datetime, timedelta, timezone

from database import (
    create_access_token,
    get_access_token,
    mark_access_token_used
)


# ==================================================
# TOKEN SETTINGS
# ==================================================

TOKEN_EXPIRY_MINUTES = 30


# ==================================================
# CREATE ACCESS TOKEN
# ==================================================

def generate_access_token(user_id, file_db_id):
    """
    Generate a secure one-time access token.

    The token is connected to:
        - Telegram user
        - Database file ID
        - Expiration time
    """

    token = secrets.token_urlsafe(32)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    )

    success = create_access_token(
        token=token,
        user_id=user_id,
        file_db_id=file_db_id,
        expires_at=expires_at.isoformat()
    )

    if not success:
        raise RuntimeError(
            "Could not create access token."
        )

    return token


# ==================================================
# VERIFY ACCESS TOKEN
# ==================================================

def verify_access_token(token, user_id):
    """
    Verify that a token:

        1. Exists
        2. Belongs to the current Telegram user
        3. Has not been used
        4. Has not expired
    """

    if not token:
        return None

    token_data = get_access_token(token)

    if not token_data:
        return None

    # Database structure:
    #
    # 0 id
    # 1 token
    # 2 user_id
    # 3 file_db_id
    # 4 created_at
    # 5 expires_at
    # 6 used

    token_user_id = token_data[2]
    file_db_id = token_data[3]
    expires_at = token_data[5]
    used = token_data[6]

    # --------------------------------------------------
    # CHECK USER
    # --------------------------------------------------

    if int(token_user_id) != int(user_id):
        print(
            "⚠️ Access token user mismatch:",
            user_id
        )

        return None

    # --------------------------------------------------
    # CHECK USED
    # --------------------------------------------------

    if int(used) == 1:
        print(
            "⚠️ Access token already used:",
            token
        )

        return None

    # --------------------------------------------------
    # CHECK EXPIRATION
    # --------------------------------------------------

    try:

        expiry_time = datetime.fromisoformat(
            expires_at
        )

        if expiry_time.tzinfo is None:
            expiry_time = expiry_time.replace(
                tzinfo=timezone.utc
            )

    except Exception:

        print(
            "❌ Invalid token expiration:",
            expires_at
        )

        return None

    if datetime.now(timezone.utc) > expiry_time:

        print(
            "⚠️ Access token expired:",
            token
        )

        return None

    # --------------------------------------------------
    # TOKEN VALID
    # --------------------------------------------------

    return {
        "token": token,
        "user_id": token_user_id,
        "file_db_id": file_db_id,
        "expires_at": expires_at
    }


# ==================================================
# CONSUME TOKEN
# ==================================================

def consume_access_token(token):
    """
    Mark a valid token as used.
    """

    return mark_access_token_used(token)