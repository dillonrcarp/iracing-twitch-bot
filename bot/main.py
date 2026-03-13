import asyncio
import os

from dotenv import load_dotenv

from bot.twitch import TwitchBot

load_dotenv()


def main():
    print("iRacing Twitch Bot starting...")

    required_vars = [
        "TWITCH_CLIENT_ID",
        "TWITCH_CLIENT_SECRET",
        "TWITCH_BOT_ACCESS_TOKEN",
        "TWITCH_BOT_USER_ID",
        "TWITCH_BROADCASTER_USER_ID",
        "TWITCH_CHANNEL_NAME",
        "IR_CLIENT_ID",
        "IR_CLIENT_SECRET",
        "IR_USERNAME",
        "IR_PASSWORD",
    ]

    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

    print("All required environment variables present.")
    bot = TwitchBot()
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
