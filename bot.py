if __name__ == '__main__':
    import asyncio
    import discord
    import traceback

    from datetime import datetime
    from discord.ext import commands , tasks

    from discord_components.component import Component
    from discord_components import InteractionType, Button, Select, SelectOption ,ButtonStyle

    from discord_slash import SlashCommand
    from discord_slash.utils.manage_commands import create_permission , create_option, create_choice
    from discord_slash.model import SlashCommandPermissionType


    from data.config import BOT_TOKEN
    from data.config import SKIMSFILEPATH


    #from core.buttoncogs import ButtonCog
    from core.database import Database
    from discord_slash_components import (
        DiscordComponents
    )

    from core import plot

    from core.nickname import UpdatePlayerElo

    #from core.challenges.user import challenge_user
    #from core.challenges.twovtwo import Challenge2v2

    # Importing the newly installed library.
    from core.constants import GUILD_IDS , ACTIVE_GAMES_CHANNEL , GAME_CHANNEL_ID , LEADERBOARD_CHANNEL_ID , GAMEMODENAMES , LOG_CHANNEL_ID
    #from core.button import button
    #from core.buttoncogs import ButtonCog
    from core.endings.win import GameWin
    from core.endings.tie import GameTie

    from core.elo import GetEloCheck ,WinLosses

    from core.leaderboard import MainLeaderboard

    from core.graphs.pubhist import TimeOfDayHist

    import subprocess

    import sys
    import statistics
    import os
    initial_extensions = ["button_cogs.results"]

    intents = discord.Intents.default()
    intents.members = True

    class Bot(commands.Bot):
        """Custom Bot subclass."""

        def __init__(self, *args, **kwargs):

            # """Initialize the bot."""
            self.database = Database(self)
            self.buttons = {}
            super().__init__(*args, **kwargs)
            self.slash = SlashCommand(self, sync_commands=True)
            DiscordComponents(self,self.slash)
            self.add_listener(self.button_listener,"on_button_click")
            self.add_listener(self.member_update,"on_member_update")
            self.add_listener(self.on_start,"on_ready")
            self.C1v1SK = "elo0+"
            self.LRL1v1SK = "elo1+"


        async def button_listener(self, res):
            print(res)
            print(res.message)
            print(res.channel)
            """Dispatch the button event."""
            component_id = res.component.id
            print(component_id)
            for pattern, button in self.buttons.items():
                result = pattern.fullmatch(component_id)
                if result is not None:
                    await button(res.user, res.message, **result.groupdict())
                    await res.respond(
                        type=InteractionType.UpdateMessage
                    )
                

        async def member_update(self, before: discord.Member, after: discord.Member):
            print(before, after)
            if before.nick != after.nick:
                await UpdatePlayerElo(self, after.id, OnChange=True)
        
            pass

        async def on_message(self, message):
            if message.channel.id == 872886014815924245:
                print(message.content)
                await NewPubGame(message.embeds[0].title[1:-1].split(" ")[0],message.embeds[0].title[1:-1].split(" ")[1:])         
        
        async def on_start(self):
            print("Started")
            self.guild = await self.fetch_guild(779349159852769310)
            testingChannel = await self.fetch_channel(873299154045136957)
            await testingChannel.send("Starting v2.1")
            #await EloRecaculation()
            await MainLeaderboard(self)
            self.mapData = await statistics.LoadMapsIntoMemory(testingChannel)
            await StartupTask(self)
        
        async def on_command_error(self, ctx, error):
            """The event triggered when an error is raised while invoking a command.
            Parameters
            ------------
            ctx: commands.Context
                The context used for command invocation.
            error: commands.CommandError
                The Exception raised.
            """

            # Allows us to check for original exceptions raised and sent to CommandInvokeError.
            # If nothing is found. We keep the exception passed to on_command_error.
            error = getattr(error, 'original', error)

            

            if isinstance(error, commands.DisabledCommand):
                await ctx.send(f'{ctx.command} has been disabled.')

            elif isinstance(error, commands.NoPrivateMessage):
                try:
                    await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
                except discord.HTTPException:
                    pass

            # For this error example we check to see where it came from...
            elif isinstance(error, commands.BadArgument):
                if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
                    await ctx.send('I could not find that member. Please try again.')

            else:
                # All other Errors not returned come here. And we can just print the default TraceBack.
                print('<@301343234108424192> Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    bot = Bot(command_prefix=["ecr"],intents=intents)

    print("setup slash Challenge")
    
    @bot.slash.slash(
        name="stats",
        description="See stats about a user",
        options=[
            create_option(
                name="user",
                description="The user you want to see stats about",
                option_type=3,
                required=True
            ),
        ],
        guild_ids=GUILD_IDS,
    )
    async def _stats(ctx, user):
        await statistics.GameMapOverTime(bot.mapData)
        #await statistics.GetPositionHeatMap(bot.mapData,"dyson",user)
        # if gamemode < 4:
        #     await GlobalStats(gamemode = gamemode )
        # else:
        #     await TimeOfDayHist(bot)

        f = discord.File("stats.png", filename="image.png")
        e = discord.Embed()
        e.set_image(url="attachment://image.png")
        await ctx.send(file=f,embed=e)

    @bot.slash.slash(
        name="convert",
        description="No",
        default_permission=False,
        permissions={
                779349159852769310: [
                create_permission(301343234108424192, SlashCommandPermissionType.USER, True)
                ]
            },
        guild_ids=GUILD_IDS,
    )
    async def _runConversion(ctx):
        await ctx.send(content="Running Conversions.... Good luck!")
        os.system('python Caculatons/GenerateAllSkims.py')
        #subprocess.Popen(['Caculations/ConvertToEchoReplay.py'])
        print("Runnign COnvrsion")
        quit()

    @bot.slash.slash(
        name="mapstats",
        description="See general map statistics",
        guild_ids=GUILD_IDS,
    )
    async def _mapstats(ctx):
        await ctx.defer()
        #await ctx.send(content = "updated")
        await statistics.GameMapOverTime(bot.mapData)
        f = discord.File("stats.png", filename="image.png")
        e = discord.Embed()
        e.set_image(url="attachment://image.png")
        await ctx.send(file=f,embed=e)


    @bot.slash.slash(
        name="shutdown",
        description="Shutdown the bot",
        default_permission=False,
        permissions={
                779349159852769310: [
                create_permission(301343234108424192, SlashCommandPermissionType.USER, True)
                ]
            },
        guild_ids = [779349159852769310]
        )
    async def _shutdown(ctx, user=None):
        await ctx.send("Shutting down")
        await bot.logout()

    @bot.slash.slash(
        name="recaculate",
        description="Recaculate ELO",
        default_permission=False,
        permissions={
                779349159852769310: [
                create_permission(301343234108424192, SlashCommandPermissionType.USER, True)
                ]
            },
        options=[
            create_option(
                name="hideprogress",
                description="Hide the progress (makes it faster)",
                option_type=4,
                required=False,
                choices=[
                    create_choice(
                        name="True",
                        value=1
                    )
                ]
            ) 
        ],
        guild_ids = [779349159852769310]
        )
    async def _recaculate(ctx, hideprogress=None):
        await ctx.send("Recaculating")
        await PubRecaculation()
        #await EloRecaculation()

    @bot.slash.slash(
        name="purge",
        default_permission=False,
        permissions={
                779349159852769310: [
                create_permission(301343234108424192, SlashCommandPermissionType.USER, True)
                ]
            },
        options=[
            create_option(
                name="amount",
                description="The amount of messages to purge",
                option_type=4,
                required=True
            ) 
        ],
        guild_ids = [779349159852769310]
        )
    async def _purge(ctx, amount = 5):
        await ctx.channel.purge(limit=amount)

    @bot.slash.slash(
        name="link",
        description="Link a discord and oculus name",
        default_permission=False,
        permissions={
                779349159852769310: [
                create_permission(853058237157867541, SlashCommandPermissionType.ROLE, True)
                ]
            },
        options=[
            create_option(
                name="user",
                description="Whos stats you want to see",
                option_type=6,
                required=True
            )
            ,
            create_option(
                name="name",
                description="The game mode you want to see stats about",
                option_type=3,
                required=True
            ),
        ],
        guild_ids=GUILD_IDS,
    )
    async def _link(ctx, user, name):
        await bot.database.get_player_info(user.id)
        await bot.database.set_oculus_name(user.id,name)
        await ctx.send("Oculus for \""+name+"\" Linked")
        pass

    @bot.slash.slash(
        name="reboot",
        description="Reboot and pull from discord",
        default_permission=False,
        permissions={
                779349159852769310: [
                create_permission(301343234108424192, SlashCommandPermissionType.USER, True)
                ]
            },
        options=[
            create_option(
                name="amount",
                description="The amount of messages to purge",
                option_type=4,
                required=False
            ) 
        ],
        guild_ids = [779349159852769310]
        )
    async def UpdateReboot_(ctx):
        await ctx.send(content="Rebooting and updating!")
        subprocess.Popen(['update.bat'])
        print("QUITING")
        quit()

    @tasks.loop(seconds=86400)
    async def ActiveGamesReminder():
        return
        channel = await bot.fetch_channel(ACTIVE_GAMES_CHANNEL)
        messages = await channel.history(limit=100).flatten()
        for msg in messages:
            print(msg)
            gameID = msg.embeds[0].footer.text
            gameData = bot.database.get_game_data(gameID)

            mentionchannel = await bot.fetch_channel(GAME_CHANNEL_ID)
            EveryoneInvolvedID = gameData["team1"].split("|") + gameData["team2"].split("|")
            team1ID = gameData["team1"].split("|")
            team2ID = gameData["team2"].split("|")
            team1Mention = [(await bot.fetch_user(id)).mention for id in team1ID]
            team2Mention = [(await bot.fetch_user(id)).mention for id in team2ID]

            embed=discord.Embed(title="Reminder", description="This is a reminder about an active game. you have not submited a result yet. to stop these reminders please cancel the game or sumbit the correct results", color=0xffffff)
            embed.add_field(name="team 1", value="\n".join(team1Mention), inline=True)
            embed.add_field(name="team 2", value="\n".join(team2Mention), inline=True)
            components = [
                Button(label="Link",url=msg.jump_url,style=5)
            ]
            await mentionchannel.send("\n".join(team1Mention+team2Mention))
            await mentionchannel.send(embed=embed,components=components)

    @tasks.loop(seconds=21600)
    async def HowToPlayReminder():
        
        channel = await bot.fetch_channel(GAME_CHANNEL_ID)
        messages = await channel.history(limit=1).flatten()
        if len(messages[0].embeds) == 0:
            embed=discord.Embed(title="How to play!", description="You can either use the buttons below or you can use /play!", color=0xffffff)
            components = [[
                Button(label="Play Comet 1v1!",id = "GamePlayGamemode_0"),
                Button(label="Play Linked 1v1!",id = "GamePlayGamemode_1")
            ]]
            await channel.send(embed=embed,components=components)

    @tasks.loop(seconds=360)
    async def LeaderBoardUpdate():
        await MainLeaderboard(bot)

 


    async def EloRecaculation(DisplayProgress = False):
        channel = await bot.fetch_channel(LOG_CHANNEL_ID)

        
        

        users = bot.database.get_users_list()
        games = bot.database.get_games_list()
        
        
        mentionList = []
        for user in users:
            userData = bot.database.get_player_info(user)
            mentionList.append(f"`[1000] [1000] [1000] [1000]` - <@!{user}>")
        embed = embed=discord.Embed(title="Elo Recaculation", description="An ELO Recaculation is taking place. Please hold on until it is finished. This may take a few minutes", color=0xffffff)
        embed.add_field(name = "Players", value = "\n".join(mentionList))
        PlayerList = await channel.send(embed=embed)


        players = dict()
        
        for user in users:
            players[str(user)] = [1000,1000,1000,1000]
        

        Elapsed = 0
        games = bot.database.get_all_games()
        for gameData in games:

            print(f"Elapsed {Elapsed}")
            Elapsed = Elapsed + 1
            winner = gameData["winner_id"]
            if winner is not None:

                winner_ids = gameData["winner_id"].split("|")
                loser_ids = gameData["loser_id"].split("|")
                eloType = int(gameData["gamemode"])


                winner_elos = [players[ID][eloType] for ID in winner_ids]
                loser_elos =[players[ID][eloType] for ID in loser_ids]

                winner_elos_after, loser_elos_after = WinLosses(winner_elos, loser_elos)

                for player, elo in zip(winner_ids + loser_ids, winner_elos_after + loser_elos_after):
                    players[player][eloType] = elo


                    
                
        mentionList = []
        for user in users:
            Database = bot.database
            userData = await Database.get_player_info(user)
            mentionList.append(f"`[{ str(round(players[str(user)][0])).zfill(4) }] [{ str(round(players[str(user)][1])).zfill(4) }] [{ str(round(players[str(user)][2])).zfill(4) }] [{ str(round(players[str(user)][3])).zfill(4) }]` - <@!{user}>")
        embed = embed=discord.Embed(title="Elo Recaculation", description="An ELO Recaculation is taking place. Please hold on until it is finished. This may take a few minutes", color=0xffffff)
        embed.add_field(name = "Players", value = "\n".join(mentionList),inline=False)
        await PlayerList.edit(embed = embed)     
        #if DisplayProgress:
            
        print(players)            
        for user in users:
            await bot.database.set_player_elo(user,players[str(user)][0],0)
            await bot.database.set_player_elo(user,players[str(user)][1],1)
            await bot.database.set_player_elo(user,players[str(user)][2],2)
            await bot.database.set_player_elo(user,players[str(user)][3],3)

        #for user in users:
        # await UpdatePlayerElo(bot,user)
        mbed = embed=discord.Embed(title="Elo Recaculation", description="Elo recaculation finished!", color=0xffffff)
        await channel.send(embed=embed)

    async def NewPubGame(id,names):
        bot.database.log_pub_game(id,datetime.now(),names)
        userIDs = bot.database.get_users_list()
        userDatas = [await bot.database.get_player_info(userID) for userID in userIDs]
        lookupTable = dict()

        for user in userDatas:
            if user["oculus"] is not None:
                lookupTable[user["oculus"]] = str(user["id"])


        for name in names:
            if name in lookupTable:
                userID = int(lookupTable[name])
                userData = await bot.database.get_player_info(userID)
                await bot.database.set_player_pubs(userID,userData["pubs"]+1)

    async def PubRecaculation():
        userIDs = bot.database.get_users_list()
        userDatas = [await bot.database.get_player_info(userID) for userID in userIDs]
        lookupTable = dict()
        for user in userDatas:
            if user["oculus"] is not None:
                lookupTable[user["oculus"]] = str(user["id"])

        pubGames = bot.database.get_pub_games()

        

        totalListOculusNames = dict()
        #print(lookupTable)
        for game in pubGames:
            for i in range(8):
                if len(game["names"].split(" ")) > i:
                    name = game["names"].split(" ")[i]
                    if name in totalListOculusNames:
                        totalListOculusNames[name] += 1
                    else:
                        totalListOculusNames[name] = 1
        sortedDict = dict(sorted(totalListOculusNames.items(),reverse = True, key=lambda item: item[1]))
        #print(sortedDict)
        

        knownDictNames = dict()
        knownDictIds = dict()
        unknownDict = dict()
        for key,value in sortedDict.items():
            if key in lookupTable:
                knownDictNames[f"<@{lookupTable[key]}>"] = value
                knownDictIds[str(lookupTable[key])] = value
            else:
                unknownDict[key] = value
            
        for key,value in knownDictIds.items():
            await bot.database.set_player_pubs(int(key),value)
            
        channel = await bot.fetch_channel(LOG_CHANNEL_ID)

        knownformated = [f"{key} - {value}" for key,value in knownDictNames.items()] 
        
        knowntotal = "\n".join(knownformated)
        

        embed=discord.Embed(title="knownPubStatistics", description=knowntotal, color=0xffff00)
        await channel.send(embed=embed)


        unknownformated = [f"{key} - {value}" for key,value in unknownDict.items()] 
        unknowntotal = "```"
        unknowntotal += "\n".join(unknownformated)
        unknowntotal += "```"
        channel = await bot.fetch_channel(LOG_CHANNEL_ID)

        embed=discord.Embed(title="UnknownPubStatistics", description=unknowntotal, color=0xff0000)
        await channel.send(embed=embed)

    


    async def GlobalStats(gamemode = 0):
        users = bot.database.get_users_list()

        TotalStats = dict()
        for user in users:
            TotalStats[str(user)] = await UserStats(user)
        plot.globalStatPlot(TotalStats,Gamemode= gamemode)        

    async def UserStats(userID):


        stats = dict()
        stats["maxElo"] = [1000,1000,1000,1000]
        stats["minElo"] = [1000,1000,1000,1000]
        stats["eloWinStreakStart"] = [0,0,0,0]
        stats["eloWinStreakLength"] = [0,0,0,0]
        stats["eloLossStreakStart"] = [0,0,0,0]
        stats["eloLossStreakLength"] = [0,0,0,0]
        stats["currentStreakStatus"] = [0,0,0,0]
        stats["winGames"] = [[],[],[],[]]
        stats["lossGames"] = [[],[],[],[]]
        stats["totalGames"] = [0,0,0,0]


        games = bot.database.get_all_games()
        users = bot.database.get_users_list()
        players = dict()

        #Caculates The ELO History
        for user in users:
            players[str(user)] = [1000,1000,1000,1000]
        eloHistory = [[("2021-06-16 00:00:00.000",True,1000)],[("2021-06-16 00:00:00.000",True,1000)],[("2021-06-16 00:00:00.000",True,1000)],[("2021-06-16 00:00:00.000",True,1000)]]
        gameI = 0
        for gameData in games:
            winner = gameData["winner_id"]
            if winner is not None:
                # Simulate ELOs
                winner_ids = gameData["winner_id"].split("|")
                loser_ids = gameData["loser_id"].split("|")
                eloType = int(gameData["gamemode"])
                winner_elos = [players[ID][eloType] for ID in winner_ids]
                loser_elos =[players[ID][eloType] for ID in loser_ids]
                winner_elos_after, loser_elos_after = WinLosses(winner_elos, loser_elos)


                for player, elo in zip(winner_ids + loser_ids, winner_elos_after + loser_elos_after):
                    players[player][eloType] = elo
                    if(str(player) == str(userID)):
                        eloHistory[eloType].append((gameData["time"],player in winner_ids,players[player][eloType]))

            gameI += 1
        stats["eloHistory"] = eloHistory

        player = players[str(user)]
        #Caculates the Win Streaks and Max and Min Elos




    

        for gamemode in range(0,2):
            LastGameWin = None
            MaxElo = 1000
            MinElo = 1000
            WinGames = []
            LossGames = []

            WinStreakStart = 0
            WinStreakLength = 0
            LossStreakStart = 0
            LossStreakLength = 0
            StreakPos = 0
            CurStreak = 0
            GameI = 0
            for result in eloHistory[gamemode]:
                time, win, elo = result 
                if win:
                    WinGames.append(GameI)
                    #if you on a win streak
                    if LastGameWin:
                        CurStreak += 1
                        if CurStreak >= WinStreakLength:
                            WinStreakLength = CurStreak
                            WinStreakStart = StreakPos
                else:
                    LossGames.append(GameI)

                    #if you on a loss streak
                    if not LastGameWin:
                        CurStreak += 1
                        if CurStreak >= LossStreakLength:
                            LossStreakLength = CurStreak
                            LossStreakStart = StreakPos         
                if win != LastGameWin:
                    CurStreak = 1
                    StreakPos = GameI                
                LastGameWin = win
                GameI += 1

                if elo > MaxElo: MaxElo = elo
                if elo < MinElo: MinElo = elo

            
            print("Outcome:")
            print(WinStreakStart,WinStreakLength,LossStreakStart,LossStreakLength)
            stats["eloWinStreakStart"][gamemode] = WinStreakStart
            stats["eloWinStreakLength"][gamemode] = WinStreakLength
            stats["eloLossStreakStart"][gamemode] = LossStreakStart
            stats["eloLossStreakLength"][gamemode] = LossStreakLength 
            stats["winGames"][gamemode] = WinGames 
            stats["lossGames"][gamemode] = LossGames 
            stats["maxElo"][gamemode] = MaxElo
            stats["minElo"][gamemode] = MinElo
            stats["totalGames"][gamemode] = len(eloHistory[gamemode])

        return stats

    async def StartupTask(bot):
        totalList = []
        channel = await bot.fetch_channel(872886014815924245)
        messages = await channel.history().flatten()
        for msg in messages:
            names = msg.embeds[0].title[1:-1].split(" ")
            
            bot.database.log_pub_game(names[0],msg.created_at,names[1:])
            
        
        
        pass

    def make_ordinal(n):
        '''
        Convert an integer into its ordinal representation::

            make_ordinal(0)   => '0th'
            make_ordinal(3)   => '3rd'
            make_ordinal(122) => '122nd'
            make_ordinal(213) => '213th'
        '''
        n = int(n)
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        return str(n) + suffix


    ActiveGamesReminder.start()
    HowToPlayReminder.start()
    LeaderBoardUpdate.start()
    bot.run(BOT_TOKEN)