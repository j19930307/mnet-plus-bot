import asyncio
import os

from sns_core import FirestoreSubscriptionStore, decode_base64_json

from berriz_bot import BerrizBot
from bstage_bot import BstageBot
from dotenv import load_dotenv

load_dotenv()


async def main():
    firebase_admin_key = os.getenv("FIREBASE_ADMIN_KEY")
    if not firebase_admin_key:
        raise ValueError("環境變數中找不到 FIREBASE_ADMIN_KEY！")

    firebase = FirestoreSubscriptionStore(decode_base64_json(firebase_admin_key))
    bstage_bot = BstageBot(firebase)
    berriz_bot = BerrizBot(firebase)

    await asyncio.gather(
        bstage_bot.execute(),
        berriz_bot.execute()
    )


if __name__ == "__main__":
    asyncio.run(main())
