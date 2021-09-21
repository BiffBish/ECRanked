


import sqlite3
from datetime import datetime
from os import path
from typing import List
from discord import User
#from ..core import Bot
from core.constants import guild_id
import requests
import json
from data.config import APIKEY


ECRANKEDURL = "http://localhost/"

LINKURL = f"{ECRANKEDURL}api/link.py"
TOTALPUBSURL = f"{ECRANKEDURL}pubs"

UPDATENICK = f"{ECRANKEDURL}api/update_discord_nick.py"
UPDATEABOUT = f"{ECRANKEDURL}api/update_about_string.php"


PATH = path.join(path.split(path.split(__file__)[0])[0], "data")
#SELECT COUNT(player_ids) as "total" FROM `ecranked`.`skims` WHERE player_ids LIKE '%3188659097895059%'

class Database:
    """Custom Database subclass."""
    def __init__(self, client):
        self.client = client
        self.user_db = sqlite3.connect(path.join(PATH, "users.sqlite"))
        self.user_cur = self.user_db.cursor()
        self.game_db = sqlite3.connect(path.join(PATH, "games.sqlite"))
        self.game_cur = self.game_db.cursor()

    # GameModes
    # 0 - Comet 1v1
    # 1 - Linked Random Loadout 1v1
    # 2 - Standerd 1v1
    # 3 - Standard 2v2

    def set_player_nick(self, discord_id: int,discord_name):
        Formdata = {
            "key": APIKEY,
            "discord_id" : discord_id,
            "discord_name" : discord_name,
            }
        print(requests.post(UPDATENICK,data=Formdata))
    
    def set_about(self, user, about):
        Formdata = {
            "key": APIKEY,
            "oculus_name" : user,
            "about_string" : about,
            }
        print(requests.post(UPDATEABOUT,data=Formdata))
    
    async def link_discord_oculus(self,oculus_name,discord_id,discord_name):
        
        Formdata = {
            "key": APIKEY,
            "oculus_name" : oculus_name,
            "discord_id" : discord_id,
            "discord_name" : discord_name,
            }
        print(requests.post(LINKURL,data=Formdata))
    
    def get_player_info(self, oculus_name: int):
        request = requests.get(f"{ECRANKEDURL}user/{oculus_name}/stats.json")
        #await ctx.send(request.status_code)
        #await ctx.send(request.text)
        if request.status_code == 404:
            return None
        FormatedText = request.text.replace("'",'"')
        FormatedText = FormatedText.replace(": None",": null")
        print(FormatedText+"|")
        return json.loads(FormatedText)
       
    def get_pubs_list(self):
        request = requests.get(f"{ECRANKEDURL}pubs")
        if request.status_code == 404:
            return None
        FormatedText = request.text
        #print(FormatedText)
        return json.loads(FormatedText)
        pass
