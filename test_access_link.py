from utils.access_link import build_telegram_access_link


def main():

    bot_username = "YourBotUsername"

    token = (
        "test123456789"
    )

    link = build_telegram_access_link(
        bot_username=bot_username,
        token=token
    )

    print("=" * 50)
    print("TELEGRAM ACCESS LINK TEST")
    print("=" * 50)

    print()
    print("Generated link:")
    print(link)

    print()
    print("Expected format:")
    print(
        "https://t.me/"
        "YourBotUsername"
        "?start=af_test123456789"
    )


if __name__ == "__main__":
    main()