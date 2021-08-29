from re import L
import sqlite3
from datetime import datetime
from os import path
from typing import List
import os


game_db = sqlite3.connect("data/games.sqlite")
game_cur = game_db.cursor()

    
def log_pub_game(self,id:str, time: datetime,names:List):
    try:
        self.game_cur.execute(
            'INSERT INTO "main"."pubs"("id","time","names")'
            'VALUES (?,?,?);',
            (id, time.strftime("%Y-%m-%d %H:%M:%S"), " ".join(names)),
        )
        self.game_db.commit()
    
    except:
        pass

def get_pub_games():
    totalList = []
    for row in game_cur.execute(
        'SELECT "id","time","names"'
        ' FROM "main"."pubs"'
    ):
        totalList.append({
            key: row[i] for i, key in enumerate(
                ("id","time", "names")
            )
        })

    return totalList

SavedPubGames = get_pub_games()
#print(SavedPubGames)
SavedIDs = [game["id"] for game in SavedPubGames]
maps = ["combustion","dyson","fission","surge"]
for map in maps:
    for match in os.listdir(f"E:/ECRanked/Skims/{map}"):
        MatchID = match[-41:-5]
        if MatchID not in SavedIDs:
            print(MatchID)
# Gameid = create_new_1v1_game(123,345)
# set_winner(int(gameid),345)
