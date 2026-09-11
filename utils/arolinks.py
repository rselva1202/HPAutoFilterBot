import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from config import AROLINKS_API_KEY


# ==================================================
# AROLINKS API
# ==================================================

AROLINKS_API_URL = "https://arolinks.com/api"


def shorten_url(destination_url: str) -> str:
    """
    Create an AroLinks shortened URL.

    Parameters:
        destination_url: The URL that AroLinks should redirect to.

    Returns:
        The generated AroLinks short URL.

    Raises:
        ValueError: If AroLinks returns an error or invalid response.
        RuntimeError: If the API request itself fails.
    """

    if not destination_url:
        raise ValueError("Destination URL cannot be empty.")

    if not AROLINKS_API_KEY:
        raise ValueError("AROLINKS_API_KEY is not configured.")

    # --------------------------------------------------
    # BUILD API REQUEST
    # --------------------------------------------------

    params = {
        "api": AROLINKS_API_KEY,
        "url": destination_url,
    }

    api_url = f"{AROLINKS_API_URL}?{urlencode(params)}"

    request = Request(
        api_url,
        method="GET",
        headers={
            "User-Agent": "AutoFilterPro/1.0"
        }
    )

    # --------------------------------------------------
    # SEND REQUEST
    # --------------------------------------------------

    try:

        with urlopen(request, timeout=15) as response:

            response_text = response.read().decode("utf-8").strip()

    except HTTPError as error:

        raise RuntimeError(
            f"AroLinks API HTTP error: {error.code}"
        ) from error

    except URLError as error:

        raise RuntimeError(
            f"Could not connect to AroLinks: {error.reason}"
        ) from error

    except Exception as error:

        raise RuntimeError(
            f"AroLinks request failed: {error}"
        ) from error

    # --------------------------------------------------
    # PARSE RESPONSE
    # --------------------------------------------------

    try:

        result = json.loads(response_text)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"AroLinks returned an invalid response: "
            f"{response_text[:300]}"
        ) from error

    # --------------------------------------------------
    # CHECK API STATUS
    # --------------------------------------------------

    if result.get("status") != "success":

        message = result.get(
            "message",
            "Unknown AroLinks API error."
        )

        raise ValueError(
            f"AroLinks API error: {message}"
        )

    # --------------------------------------------------
    # GET SHORT URL
    # --------------------------------------------------

    shortened_url = result.get("shortenedUrl")

    if not shortened_url:

        raise ValueError(
            "AroLinks did not return a shortened URL."
        )

    return shortened_url


# ==================================================
# CREATE AROLINKS ACCESS LINK
# ==================================================

def create_access_link(
    bot_username: str,
    token: str
) -> str:
    """
    Create an AroLinks short URL that redirects
    the user back to the Telegram bot with the
    AutoFilterPro access token.
    """

    from utils.access_link import build_telegram_access_link

    # ----------------------------------------------
    # BUILD TELEGRAM DESTINATION
    # ----------------------------------------------

    telegram_url = build_telegram_access_link(
        bot_username=bot_username,
        token=token
    )

    # ----------------------------------------------
    # SHORTEN WITH AROLINKS
    # ----------------------------------------------

    return shorten_url(telegram_url)