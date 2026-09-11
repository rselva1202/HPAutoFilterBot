from utils.arolinks import shorten_url


def main():

    destination = "https://example.com"

    print("=" * 50)
    print("Testing AroLinks API")
    print("=" * 50)

    try:

        short_url = shorten_url(destination)

        print()
        print("✅ AroLinks API working!")
        print()
        print("Destination:")
        print(destination)

        print()
        print("Short URL:")
        print(short_url)

    except Exception as error:

        print()
        print("❌ AroLinks API test failed")
        print()
        print("Error:")
        print(error)


if __name__ == "__main__":
    main()