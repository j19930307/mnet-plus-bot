import os

import discord

from bstage_bot import BstageBot
from el7zup_bot import EL7ZUPBot
from dotenv import load_dotenv

from firebase import Firebase

load_dotenv()
firebase = Firebase()
el7zup_bot = EL7ZUPBot(firebase)
el7zup_bot.execute()
bot = discord.Bot()


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('Bot is ready to receive commands')
    bstage_bot = BstageBot(bot, firebase)
    await bstage_bot.execute()
    await bot.close()
    await exit()


bot.run(os.environ["BOT_TOKEN"])
