import os

import discord

from berriz_bot import BerrizBot
from bstage_bot import BstageBot
from el7zup_bot import EL7ZUPBot
from dotenv import load_dotenv

from firebase import Firebase

load_dotenv()
firebase = Firebase()
# el7zup_bot = EL7ZUPBot(firebase)
# el7zup_bot.execute()
bstage_bot = BstageBot(firebase)
bstage_bot.execute()
berriz_bot = BerrizBot(firebase)
berriz_bot.execute()
