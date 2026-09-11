from urllib.parse import quote


# ==================================================
# TELEGRAM ACCESS LINK
# ==================================================

def build_telegram_access_link(
    bot_username: str,
    token: str
) -> str:
    """
    Build a Telegram deep link for an AutoFilterPro
    access token.

    Example:

    https://t.me/MyBot?start=af_xxxxxxxxx
    """

    if not bot_username:
        raise ValueError(
            "Bot username is required."
        )

    if not token:
        raise ValueError(
            "Access token is required."
        )

    bot_username = bot_username.lstrip("@").strip()

    start_parameter = f"af_{token}"

    return (
        f"https://t.me/"
        f"{quote(bot_username)}"
        f"?start={quote(start_parameter)}"
    )