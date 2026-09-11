from utils.access_link import build_telegram_access_link
from utils.arolinks import shorten_url


def main():

    # ----------------------------------------------
    # TEST VALUES
    # ----------------------------------------------

    bot_username = "HPAutoFilterBot"

    test_token = (
        "af_test123456789"
    )

    # ----------------------------------------------
    # BUILD TELEGRAM URL
    # ----------------------------------------------

    telegram_url = build_telegram_access_link(
        bot_username=bot_username,
        token=test_token
    )

    print("=" * 60)
    print("AUTOFILTERPRO ACCESS GATE TEST")
    print("=" * 60)

    print()
    print("Telegram destination:")
    print(telegram_url)

    # ----------------------------------------------
    # AROLINKS
    # ----------------------------------------------

    try:

        short_url = shorten_url(
            telegram_url
        )

        print()
        print("AroLinks short URL:")
        print(short_url)

        print()
        print("✅ COMPLETE CHAIN WORKING")

    except Exception as error:

        print()
        print("❌ AroLinks failed")
        print()
        print(error)


if __name__ == "__main__":
    main()