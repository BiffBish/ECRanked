from re import L
import sqlite3
from datetime import datetime
from os import path
from typing import List
import os
import time
import json
game_db = sqlite3.connect("data/games.sqlite")
game_cur = game_db.cursor()
user_db = sqlite3.connect("data/users.sqlite")
user_cur = user_db.cursor()
    
def log_pub_game(id:str, time: datetime,names:List):
    try:
        game_cur.execute(
            'INSERT INTO "main"."pubs"("id","time","names")'
            'VALUES (?,?,?);',
            (id, time.strftime("%Y-%m-%d %H:%M:%S"), " ".join(names)),
        )
        game_db.commit()
    
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

def get_users_list():
        totalList = []
        for row in user_cur.execute(
            'SELECT "userID" FROM "main"."users"'
        ):
            totalList.append(row[0])
        return totalList

def get_player_info( user_id: int):
        """Get a players info."""
        for row in user_cur.execute(
            'SELECT "userID","name","oculus","pubs","eloshow","elo0","elo1","elo2","elo3" FROM'
            '"main"."users" WHERE "userID" = '
            + str(user_id)
        ):
            user = {
                key: row[i] for i, key in enumerate(
                    ("id", "name", "oculus","pubs","eloshow","elo0", "elo1", "elo2", "elo3")
                )
            }
            # if user_id == 514251369738141733:
            #     user["pubs"] = 1
            # if user_id == 806596988988555335:
            #     user["pubs"] = 999999

            #print(user)
            return user
       
        return None
    
def set_player_pubs(user_id,pubs):
        user_cur.execute(
            f'UPDATE "main"."users" SET "pubs"= (?) WHERE "userID" = (?)',
            (pubs, user_id),
        )
        user_db.commit()

SavedPubGames = get_pub_games()
#print(SavedPubGames)
SavedIDs = [game["id"] for game in SavedPubGames]
maps = ["combustion","dyson","fission","surge"]
NumExtraMaps = 0

userIDs = get_users_list()
userDatas = [get_player_info(userID) for userID in userIDs]
lookupTable = dict()

for user in userDatas:
    if user["oculus"] is not None:
        lookupTable[user["oculus"]] = str(user["id"])
for map in maps:
    for match in os.listdir(f"E:/ECRanked/Skims/{map}"):
        MatchID = match[-41:-5]
        MatchData = json.load(open(f"E:/ECRanked/Skims/{map}/{match}"))
        MatchTime = datetime.strptime(MatchData["start_time"],"%Y/%m/%d %H:%M:%S")
        NamesToAdd = list()
        for name, player in MatchData["players"].items():
            NamesToAdd.append(name)
            if name in lookupTable:
                userID = int(lookupTable[name])
                userData = get_player_info(userID)
                set_player_pubs(userID,userData["pubs"]+1)    

        log_pub_game(MatchID,MatchTime,NamesToAdd)
        if MatchID not in SavedIDs:
            print(MatchID)
            NumExtraMaps+=1





print(NumExtraMaps)
time.sleep(100)
# Gameid = create_new_1v1_game(123,345)
# set_winner(int(gameid),345)
