from core.constants import LEADERBOARD_CHANNEL_ID
import discord
from discord_components import Button ,ButtonStyle

async def MainLeaderboard(bot):
    channel = await bot.fetch_channel(LEADERBOARD_CHANNEL_ID)
    History =  await channel.history(limit=3).flatten()
    PubsMessage = History[0]

    PubList = bot.database.get_pubs_list()

    Players = list()
    for item in PubList:
        if(item["total_games"] is not None):
            Players.append(item)
    
    
    ### PUBS LEADERBOARD  
    ### ===================================================================
    
    Players.sort(reverse=True,key=lambda a: a["total_games"])
    PubsLeaderboard = []
    for userStat in Players:
        if userStat["total_games"] > 0:
            PubsLeaderboard.append(userStat)
    #▼
    Placement = 0
    for userStat in PubsLeaderboard:
        Placement += 1
        userStat["placement"] = Placement
    #PubsLeaderboard.sort(reverse=LRL1v1SK[-1]=="+",key=lambda a: a[LRL1v1SK[:-1]])


    StatStr = "```  | "

    StatStr +=  "#    "

    #              
    StatStr += "Oculus Name          Discord Name\n"
    StatStr += "--+-------------------------------------------\n"
    counter = 0
    for i in range(10):
        if i >= len(PubsLeaderboard):
            StatStr += f"\n"
            continue
        userStat = PubsLeaderboard[i]
        counter = str(userStat['placement'])
        Plays = str(userStat['total_games'])
        Name = userStat['oculus_name']
        DiscordName = userStat['discord_name']
        if DiscordName:
            StatStr += f"{counter.ljust(2)}| {Plays.ljust(3)}  {Name.ljust(20)} [{DiscordName}]\n"
        else:
            StatStr += f"{counter.ljust(2)}| {Plays.ljust(3)}  {Name.ljust(20)} \n"
    StatStr += "..."

    StatStr += "```"
    PubEmbed=discord.Embed(title="Pubs Leaderboard!", description =StatStr,  color=0xff0000)

    await PubsMessage.edit(content = "",embed=PubEmbed,components = [])

    # #print(userStats)
    # games = bot.database.get_games_list()

    # for game in games:
    #     gameData = bot.database.get_game_data(game)
    #     if(gameData["winner_id"] is None):
    #         continue
    #     for userID in gameData["winner_id"].split("|"):
    #         userStats[userID][f"win{gameData['gamemode']}"] += 1
    #         userStats[userID][f"plays{gameData['gamemode']}"] +=  1

    #     for userID in gameData["loser_id"].split("|"):
    #         userStats[userID][f"loss{gameData['gamemode']}"] += 1
    #         userStats[userID][f"plays{gameData['gamemode']}"] +=  1
        

    #     # for userStat in userStats:
    #     #     #print(userStat)
    #     #     #print(gameData["team1"].split("|") + gameData["team2"].split("|"))
    #     #     if(gameData["winner_id"] is None):
    #     #         continue
    #     #     if str(userStat["id"]) in gameData["winner_id"].split("|"):
    #     #         #print("Match")
    #     #         userStat[f"win{gameData['gamemode']}"] += 1
    #     #         userStat[f"plays{gameData['gamemode']}"] +=  1
            
    #     #     if str(userStat["id"]) in gameData["loser_id"].split("|"):
    #     #         #print("Match")
    #     #         userStat[f"loss{gameData['gamemode']}"] += 1
    #     #         userStat[f"plays{gameData['gamemode']}"] = userStat[f"plays{gameData['gamemode']}"] + 1


    # for id,userStat in userStats.items():
    #     if(userStats[id]['plays0'] == 0):
    #         userStats[id]['wlr0'] = 0
    #     else:
    #         userStats[id]['wlr0'] = userStats[id]['win0'] / userStats[id]['plays0']
        
    #     if(userStats[id]['plays1'] == 0):
    #         userStats[id]['wlr1'] = 0
    #     else:
    #         userStats[id]['wlr1'] = userStats[id]['win1'] / userStats[id]['plays1']


    # #print(userStats)
    
    # pubGames = bot.database.get_pub_games()
    # lookupTable = dict()

    # for user in userDatas:
    #     if user["oculus"] is not None:
    #         lookupTable[user["oculus"]] = str(user["id"])


    # #print(lookupTable)
    # for game in pubGames:
    #     for name in game["names"].split(" "):
    #         #print(name)
    #         if name in lookupTable:
    #             userStats[lookupTable[name]]["pubs"] += 1
    #             #print("added")





    # ### COMET 1v1
    # ### ===================================================================
    # ListStats = []
    # for key,item in userStats.items():
    #     ListStats.append(item)
    # C1v1SK = "elo0+"#bot.C1v1SK

    # ListStats.sort(reverse=True,key=lambda a: a["elo0"])
    # Comet1v1Leaderboard = []
    # for userStat in ListStats:
    #     if userStat["plays0"] > 0:
    #         Comet1v1Leaderboard.append(userStat)

    # Placement = 0
    # for userStat in Comet1v1Leaderboard:
    #     Placement += 1
    #     userStat["placement"] = Placement

    # Comet1v1Leaderboard.sort(reverse=C1v1SK[-1]=="+",key=lambda a: a[C1v1SK[:-1]])

    #▼
    components = []

    # StatStr = "```  | "
    # if C1v1SK == "elo0+":
    #     EloStr = "▲Elo" 
    #     components.append(Button(style=ButtonStyle.green,label=EloStr,id="Leaderboard_C1v1SK_elo0-"))
    # elif C1v1SK == "elo0-":
    #     EloStr = "▼Elo"
    #     components.append(Button(style=ButtonStyle.red,label=EloStr,id="Leaderboard_C1v1SK_elo0+"))
    # else:
    #     EloStr = "Elo"
    #     components.append(Button(style=ButtonStyle.gray,label=EloStr,id="Leaderboard_C1v1SK_elo0+"))

    # if C1v1SK == "plays0+":
    #     PlaysStr = "▲#"
    #     components.append(Button(style=ButtonStyle.green,label=PlaysStr,id="Leaderboard_C1v1SK_plays0-"))
    # elif C1v1SK == "plays0-":
    #     PlaysStr = "▼#"
    #     components.append(Button(style=ButtonStyle.red,label=PlaysStr,id="Leaderboard_C1v1SK_plays0+"))
    # else:
    #     PlaysStr = "#"
    #     components.append(Button(style=ButtonStyle.grey,label=PlaysStr,id="Leaderboard_C1v1SK_plays0+"))

    # if C1v1SK == "wlr0+":
    #     WlrStr = "▲W/L"
    #     components.append(Button(style=ButtonStyle.green,label=WlrStr,id="Leaderboard_C1v1SK_wlr0-"))
    # elif C1v1SK == "wlr0-":
    #     WlrStr = "▼W/L"
    #     components.append(Button(style=ButtonStyle.red,label=WlrStr,id="Leaderboard_C1v1SK_wlr0+"))
    # else:
    #     WlrStr = "W/L"
    #     components.append(Button(style=ButtonStyle.grey,label=WlrStr,id="Leaderboard_C1v1SK_wlr0+"))


    # #      
    # StatStr +=  EloStr.ljust(7) + PlaysStr.ljust(5) + WlrStr.ljust(8)     
    # StatStr += "Name \n"
    # StatStr += "--+-------------------------------------------\n"
    # counter = 0
    # for userStat in Comet1v1Leaderboard:
    #     counter = str(userStat['placement'])
    #     Wlr =  "{:.1%}".format(userStat['wlr0'])
    #     Elo = str(round(userStat['elo0']))
    #     Plays = str(userStat['plays0'])
    #     Name = userStat['name']
    #     StatStr += f"{counter.ljust(2)}| {Elo.ljust(5)}  {Plays.ljust(3)}  {Wlr.ljust(6)}  {Name} \n"
    # StatStr += "```"
    # CometEmbed=discord.Embed(title="Comet 1v1 Leaderboard!", description =StatStr,  color=0xff0000)


    # await C1v1Message.edit(content = "",embed=CometEmbed,components = [])
    












    # ### LINKED RANDOM LOADOUT 1v1   
    # ### ===================================================================
    # ListStats = []
    # for key,item in userStats.items():
    #     ListStats.append(item)


    # LRL1v1SK = "elo1+"#bot.LRL1v1SK



    # ListStats.sort(reverse=True,key=lambda a: a["elo1"])
    # Comet1v1Leaderboard = []
    # for userStat in ListStats:
    #     if userStat["plays1"] > 0:
    #         Comet1v1Leaderboard.append(userStat)
    # #▼
    # Placement = 0
    # for userStat in Comet1v1Leaderboard:
    #     Placement += 1
    #     userStat["placement"] = Placement
    # Comet1v1Leaderboard.sort(reverse=LRL1v1SK[-1]=="+",key=lambda a: a[LRL1v1SK[:-1]])

    # components = []
    # if LRL1v1SK == "elo1+":
    #     EloStr = "▲Elo"
    #     components.append(Button(style=ButtonStyle.green,label=EloStr,id="Leaderboard_LRL1v1SK_elo1-"))
                
    # elif LRL1v1SK == "elo1-":
    #     EloStr = "▼Elo"
    #     components.append(Button(style=ButtonStyle.red,label=EloStr,id="Leaderboard_LRL1v1SK_elo1+"))
    # else:
    #     EloStr = "Elo"
    #     components.append(Button(style=ButtonStyle.gray,label=EloStr,id="Leaderboard_LRL1v1SK_elo1+"))

    # if LRL1v1SK == "plays1+":
    #     PlaysStr = "▲#"
    #     components.append(Button(style=ButtonStyle.green,label=PlaysStr,id="Leaderboard_LRL1v1SK_plays1-"))
    # elif LRL1v1SK == "plays1-":
    #     PlaysStr = "▼#"
    #     components.append(Button(style=ButtonStyle.red,label=PlaysStr,id="Leaderboard_LRL1v1SK_plays1+"))
    # else:
    #     PlaysStr = "#"
    #     components.append(Button(style=ButtonStyle.grey,label=PlaysStr,id="Leaderboard_LRL1v1SK_plays1+"))

    # if LRL1v1SK == "wlr1+":
    #     WlrStr = "▲W/L"
    #     components.append(Button(style=ButtonStyle.green,label=WlrStr,id="Leaderboard_LRL1v1SK_wlr1-"))
    # elif LRL1v1SK == "wlr1-":
    #     WlrStr = "▼W/L"
    #     components.append(Button(style=ButtonStyle.red,label=WlrStr,id="Leaderboard_LRL1v1SK_wlr1+"))
    # else:
    #     WlrStr = "W/L"
    #     components.append(Button(style=ButtonStyle.grey,label=WlrStr,id="Leaderboard_LRL1v1SK_wlr1+"))
    # StatStr = "```  | "

    # StatStr +=  EloStr.ljust(7) + PlaysStr.ljust(5) + WlrStr.ljust(8)     

    # #              
    # StatStr += "Name \n"
    # StatStr += "--+-------------------------------------------\n"
    # counter = 0
    # for userStat in Comet1v1Leaderboard:
    #     counter = str(userStat['placement'])
    #     Wlr =  "{:.1%}".format(userStat['wlr1'])
    #     Elo = str(round(userStat['elo1']))
    #     Plays = str(userStat['plays1'])
    #     Name = userStat['name']
    #     StatStr += f"{counter.ljust(2)}| {Elo.ljust(5)}  {Plays.ljust(3)}  {Wlr.ljust(6)}  {Name} \n"
    # StatStr += "```"
    # LrLEmbed=discord.Embed(title="Linked Random 1v1 Leaderboard!", description =StatStr,  color=0xff0000)

    # await LrL1v1Message.edit(content = "",embed=LrLEmbed,components = [])


    
    
