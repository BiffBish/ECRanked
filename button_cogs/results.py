from asyncio import sleep

from .. import core
from ..core import constants
from discord_components import Button, ButtonStyle
import discord




def setup(bot):
    print("setup Challenge")
    bot.add_buttons(Challenge(bot))


def teardown(bot):
    bot.remove_buttons(Challenge(bot))
