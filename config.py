import os
from dotenv import load_dotenv

load_dotenv()


def get_required_env(name):
    value = os.getenv(name)

    if not value:
        raise ValueError(f"Missing required environment variable: {name}")

    return value


# Telegram API
API_ID = int(get_required_env("API_ID"))
API_HASH = get_required_env("API_HASH")
BOT_TOKEN = get_required_env("BOT_TOKEN")


# Admin IDs
ADMIN_IDS = [
    int(admin_id.strip())
    for admin_id in get_required_env("ADMIN_IDS").split(",")
    if admin_id.strip()
]


# Telegram storage channel
STORAGE_CHANNEL = int(get_required_env("STORAGE_CHANNEL"))

# ==================================================
# AROLINKS CONFIGURATION
# ==================================================

AROLINKS_API_KEY = get_required_env("AROLINKS_API_KEY")