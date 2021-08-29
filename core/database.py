import sqlite3
from datetime import datetime
from os import path
from typing import List
from discord import User
#from ..core import Bot
from core.constants import guild_id
from core.nickname import UpdatePlayerElo

PATH = path.join(path.split(path.split(__file__)[0])[0], "data")


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
    async def set_player_pubs(self,user_id,pubs):
        self.user_cur.execute(
            f'UPDATE "main"."users" SET "pubs"= (?) WHERE "userID" = (?)',
            (pubs, user_id),
        )
        self.user_db.commit()
        await UpdatePlayerElo(self.client,user_id)

    async def set_player_elo(self, user_id: int, elo: float, gamemode: int):
        """Set a players elo value for a given gamemode."""
        print(user_id)
        print(elo)
        print(gamemode)
        self.user_cur.execute(
            f'UPDATE "main"."users" SET "elo{gamemode}"= (?) WHERE "userID" = (?)',
            (elo, user_id),
        )
        self.user_db.commit()
    
    async def set_player_show_elo(self, user_id: int, gamemode: int):


        """Set a players elo value for a given gamemode."""
        print(user_id)
        print(gamemode)
        self.user_cur.execute(
            f'UPDATE "main"."users" SET "eloshow"= (?) WHERE "userID" = (?)',
            (gamemode, user_id),
        )
        self.user_db.commit()
        user = await self.client.fetch_user(user_id)
        #update the shown elo
        print(user)
        await UpdatePlayerElo(self.client,user.id)

    async def set_player_nick(self, user_id: int,name):
        self.user_cur.execute(
            f'UPDATE "main"."users" SET "name"= (?) WHERE "userID" = (?)',
            (name,user_id),
        )
        self.user_db.commit()
        user = await self.client.fetch_user(user_id)
        #update the shown elo
        #print(user)
        #await UpdatePlayerElo(self.client,user.id)
    
    async def set_oculus_name(self,user_id,name):
        self.user_cur.execute(
            f'UPDATE "main"."users" SET "oculus"= (?) WHERE "userID" = (?)',
            (name,user_id),
        )
        self.user_db.commit()
    
    async def get_player_info(self, user_id: int):
        """Get a players info."""
        for row in self.user_cur.execute(
            'SELECT "userID","name","oculus","pubs","eloshow","elo0","elo1","elo2","elo3" FROM'
            '"main"."users" WHERE "userID" = '
            + str(user_id)
        ):
            user = {
                key: row[i] for i, key in enumerate(
                    ("id", "name", "oculus","pubs","eloshow","elo0", "elo1", "elo2", "elo3")
                )
            }
            if user_id == 514251369738141733:
                user["pubs"] = 221
            #print(user)
            return user
       
        return await self.save_new_user(user_id)

    # Done
    async def save_new_user(self, user_id: int):
        """Save a new default user into the database."""
        guild = await self.client.fetch_guild(guild_id)
        nick = (await guild.fetch_member(user_id)).nick or (await self.client.fetch_user(user_id)).name

        # nick = ECRanked.GetPlayerName(userID)
        self.user_cur.execute(
            'INSERT INTO "main"."users"("userID","name") VALUES (?,?);',
            (user_id, nick),
        )
        self.user_db.commit()
        return {
            "id": user_id,
            "name": "",
            "elo0": 1000,
            "elo1": 1000,
            "elo2": 1000,
            "elo3": 1000,
        }
    
    def create_new_1v1_game(self, player1: User, player2: User, gamemode: int):
        """Create a new 1v1 Game in the database."""

        print("gameMode")
        print(gamemode)
        # dd/mm/YY H:M:S
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print("date and time =", dt_string)
        self.game_cur.execute(
            'INSERT INTO "main"."games"("time","team1","team2","gamemode")'
            'VALUES (?,?,?,?);',
            (now, player1.id, player2.id, gamemode),
        )
        print(self.game_cur.lastrowid)
        self.game_db.commit()
        return self.game_cur.lastrowid

    def create_new_2v2_game(self, userdata: List[List[dict]]):
        """Create a new 2v2 Game in the database."""
        # dd/mm/YY H:M:S
        now = datetime.now()
        print(userdata)
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print("date and time =", dt_string)
        print(userdata)

        u1_id = userdata[0][0]["id"]
        u2_id = userdata[0][1]["id"]
        u3_id = userdata[1][0]["id"]
        u4_id = userdata[1][1]["id"]

        self.game_cur.execute(
            'INSERT INTO "main"."games"("time","team1","team2","gamemode") '
            f'VALUES ("{dt_string}","{u1_id}|{u2_id}","{u3_id}|{u4_id}",3);'
        )
        print(self.game_cur.lastrowid)
        self.game_db.commit()
        return self.game_cur.lastrowid

    def set_winner(self, game_id: int, winner_id: int):
        """Set the winner for a given game_id."""
        # dd/mm/YY H:M:S
        for row in self.game_cur.execute(
            'SELECT "team1" ,"team2" FROM "main"."games" WHERE "id" = '
            + str(game_id)
        ):
            print(row)
            if winner_id == row[0]:
                self.game_db.execute(
                    'UPDATE "main"."games" SET ("winner_id","loser_id") = '
                    '(?,?) WHERE "id" = ' + str(game_id),
                    (row[0], row[1]),
                )
            elif winner_id == row[1]:
                self.game_db.execute(
                    'UPDATE "main"."games" SET ("winner_id","loser_id") = '
                    '(?,?) WHERE "id" = ' + str(game_id),
                    (row[1], row[0])
                )
            self.game_db.commit()
            return

    def get_game_data(self, game_id: int):
        """Get the game data."""
        for row in self.game_cur.execute(
            'SELECT "time","team1" ,"team2","winner_id" ,"loser_id","gamemode"'
            ' FROM "main"."games" WHERE "id" = ' + str(game_id)
        ):
            return {
                key: row[i] for i, key in enumerate(
                    ("time", "team1", "team2",
                     "winner_id", "loser_id", "gamemode")
                )
            }

    def get_games_list(self):
        totalList = []
        for row in self.game_cur.execute(
            'SELECT "ID" FROM "main"."games"'
        ):
            totalList.append(row[0])
        return totalList
    
    def get_users_list(self):
        totalList = []
        for row in self.user_cur.execute(
            'SELECT "userID" FROM "main"."users"'
        ):
            totalList.append(row[0])
        return totalList

    def get_all_games(self):
        totalList = []
        for row in self.game_cur.execute(
            'SELECT "id","time","team1" ,"team2","winner_id" ,"loser_id","gamemode"'
            ' FROM "main"."games"'
        ):
            totalList.append({
                key: row[i] for i, key in enumerate(
                    ("id","time", "team1", "team2",
                     "winner_id", "loser_id", "gamemode")
                )
            })

        return totalList

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
    
    def get_pub_games(self):
        totalList = []
        for row in self.game_cur.execute(
            'SELECT "id","time","names"'
            ' FROM "main"."pubs"'
        ):
            totalList.append({
                key: row[i] for i, key in enumerate(
                    ("id","time", "names")
                )
            })

        return totalList
       
        

# Gameid = create_new_1v1_game(123,345)
# set_winner(int(gameid),345)
