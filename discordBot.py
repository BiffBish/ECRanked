from asyncio.windows_events import NULL

from discord.flags import PublicUserFlags


if __name__ == '__main__':
    BotVersion = "2.6"
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


    #from core.buttoncogs import ButtonCog
    from core.database import Database
    from discord_slash_components import (
        DiscordComponents
    )

    from core import plot

    from core.nickname import UpdatePlayerPubs

    #from core.challenges.user import challenge_user
    #from core.challenges.twovtwo import Challenge2v2

    # Importing the newly installed library.
    from core.constants import GUILD_IDS , ACTIVE_GAMES_CHANNEL , GAME_CHANNEL_ID , LEADERBOARD_CHANNEL_ID , GAMEMODENAMES , LOG_CHANNEL_ID
    
    from core.leaderboard import MainLeaderboard

    import subprocess

    import sys
    import statistics
    import os
    import json
    import re
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
            # print(before, after)
            # if before.nick != after.nick:
            #     CleanName = re.match("^(?:.(?![\\[\\(\\{]))*",after.nick).group()
            #     await self.database.UpdatePlayerPubs(self, after.id,CleanName, OnChange=True)
        
            pass

        async def on_message(self, message):
            if message.channel.id == 882379875242106940:
                print(message.content)
                await NewPubGame(message.content.split(","))         
        
        async def on_start(self):
            print("Started")
            self.guild = await self.fetch_guild(779349159852769310)
            testingChannel = await self.fetch_channel(873299154045136957)
            await testingChannel.send(f"Starting v{BotVersion}")
            #await EloRecaculation()
            await MainLeaderboard(self)
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
    print("setup slash _stats")


   
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
                create_permission(853058237157867541, SlashCommandPermissionType.ROLE, True)
                ]
            },
        guild_ids = [779349159852769310]
        )
    async def _shutdown(ctx):
        await ctx.send("Shutting down")
        await bot.logout()

    @bot.slash.slash(
        name="recaculate",
        description="Recaculate ELO",
        default_permission=False,
        permissions={
                779349159852769310: [
                create_permission(853058237157867541, SlashCommandPermissionType.ROLE, True)
                ]
            },
        guild_ids = [779349159852769310]
        )
    async def _recaculate(ctx):
        await ctx.send("Recaculating 2.0")
        await PubRecaculation(ctx)
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
                description="The Discord user",
                option_type=6,
                required=True
            )
            ,
            create_option(
                name="name",
                description="The Oculus username",
                option_type=3,
                required=True
            ),
        ],
        guild_ids=GUILD_IDS,
    )
    async def _link(ctx, user:discord.User, name):
        await bot.database.link_discord_oculus(name,user.id,user.name)
        await ctx.send("Oculus for \""+name+"\" Linked")
        pass

    @bot.slash.slash(
        name="setabout",
        description="Set an about string for a user",
        default_permission=False,
        permissions={
                779349159852769310: [
                create_permission(853058237157867541, SlashCommandPermissionType.ROLE, True)
                ]
            },
        options=[
            create_option(
                name="name",
                description="The Oculus username",
                option_type=3,
                required=True
            ),
            create_option(
                name="about",
                description="The about string",
                option_type=3,
                required=True
            )
            
        ],
        guild_ids=GUILD_IDS,
    )
    async def _setabout(ctx, name, about):
        bot.database.set_about(name,about)
        await ctx.send("About for \""+name+"\" set to `"+about+"`")
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
    
    
    @bot.slash.slash(
        name="ecstats",
        description="Get Recorded stats from Echo Combat games",
        options=[
            create_option(
                name="name",
                description="The oculus username",
                option_type=3,
                required=False
            ),
        ],
        guild_ids=[779349159852769310,326412222119149578]
    )
    async def _stats(ctx, name = None):
        try:
            weaponName = ["Pulsar","Nova","Comet","Meteor"]
            abilityName = ["Repair Matrix","Threat Scanner","Energy Barrier","Phase Shift"]

            grenadeName = ["Detonator","Stun Field","Arc Mine","Instant Repair"]


            if ctx.guild.id == 326412222119149578:
                if ctx.channel.id not in [375408783091826698,328962843800109067,537419656181448716]:
                    embed=discord.Embed(title="Stats", description=f"Please don't use <@852660826710999051> in this channel.\nUse <#328962843800109067> or <#375408783091826698>. Thanks!", color=0xff0000)
                    await ctx.send(embed=embed)
                    return

            inputedNothing = False
            if name is None:
                inputedNothing = True
                name = re.match("^(?:.(?![\\[\\(\\{]))*",ctx.author.display_name).group()
            playerData = bot.database.get_player_info(name)
            if playerData is None:
                if inputedNothing:
                    embed=discord.Embed(title="Stats", description=f"There are no combat stats for `{name}`!\nTry setting your discord nickname to your oculus name.", color=0xff0000)
                else:
                    embed=discord.Embed(title="Stats", description=f"There are no combat stats for `{name}`", color=0xff0000)
                embed.set_footer(text="Note: Information has only been collected since September 1st 2021")
                await ctx.send(embed=embed)
                return
            
            average_speed = playerData["average_speed"]
            average_ping = playerData["average_ping"]
            percent_stopped = playerData["percent_stopped"]*100
            percent_upsidedown = playerData["percent_upsidedown"]*100
            total_games = playerData["total_games"]
            total_deaths = playerData["total_deaths"]
            average_deaths = playerData["average_deaths"]
            mainLoadoutStr = "No Loadout Data Available"
            if playerData["top_loadout"] is not None:
                mainLoadout = int(playerData["top_loadout"][0][0])
                abilityNumber = int(mainLoadout % 4)
                grenadeNumber = int(((mainLoadout - abilityNumber)% 16) / 4)
                weaponNumber = int(((mainLoadout - (abilityNumber+grenadeNumber))% 64) / 16)

                mainLoadoutStr = f"{weaponName[weaponNumber]}\n {grenadeName[grenadeNumber]}\n {abilityName[abilityNumber]}" 
            if "discord_name" not in playerData:
                discord_name = None
                discord_pfp = None
            else:
                discord_name = playerData["discord_name"]
                discord_pfp = playerData["discord_pfp"]


            embed=discord.Embed(title=f"Combat Stats for `{name}`", description=f"For more stats visit [ECRanked.com](http://ecranked.com/user/{name}/stats)", color=0x00ffff)
            if discord_name != None:
                embed.set_thumbnail(url=discord_pfp)
            embed.add_field(name="Games", value=f"{total_games}", inline=True)
            embed.add_field(name="Deaths", value=f"{total_deaths}", inline=True)
            embed.add_field(name="Avg Speed", value=f"{round(average_speed,2)}m/s", inline=True)
            embed.add_field(name="Avg Ping", value=f"{round(average_ping)}ms", inline=True)
            embed.add_field(name="Idle", value=f"{round(percent_stopped,1)}%", inline=True)
            embed.add_field(name="Flipped", value=f"{round(percent_upsidedown,1)}%", inline=True)
            embed.add_field(name="Avg Deaths", value=f"{round(average_deaths,1)}", inline=True)
            embed.add_field(name="Main Loadout", value=mainLoadoutStr, inline=True)
            if playerData["about_string"] is None:
                if ctx.guild.id == 326412222119149578:
                    embed.add_field(name="About Me",value="No profile set, join echo combat longue and contact an ECR moderator to submit", inline=True)
                else:
                    embed.add_field(name="About Me", value="No profile set, contact an <@&853058237157867541> to submit", inline=True)

            else:
                embed.add_field(name="About Me", value=playerData["about_string"], inline=True)


            embed.set_footer(text="Note: Information has only been collected since September 1st 2021")

            if discord_name != None:
                embed.add_field(name="Discord Name", value = discord_name, inline=False)
            #if name.lower() == "parcellforce":
            #    embed.add_field(name="Developer Note!", value="Will throw the game to get you killed. He will announce your location to the oponents, get in your face, and be a general nuisance if your at the receving end of his bullshit. If you see him in game please say \"Bad Parcel\"", inline=False)

            await ctx.send(embed= embed)
        except Exception as e:
            traceback.print_exc()
            print(e)
            embed=discord.Embed(title=f"Oops!", description = f"`{e}`", color=0x00ffff)
            await ctx.send(embed= embed)


    @tasks.loop(seconds=360)
    async def LeaderBoardUpdate():
        await MainLeaderboard(bot)

 
    async def NewPubGame(ids):
        pubList = bot.database.get_pubs_list()
        for id in ids:
            if id in pubList:
                totalGames = pubList[id]["total_games"]
                discord_id = pubList[id]["discord_id"]
                saved_name = pubList[id]["discord_name"]
                if discord_id:
                    await UpdatePlayerPubs(bot,discord_id,saved_name,totalGames)

    async def PubRecaculation(ctx):
        pubList = bot.database.get_pubs_list()
        for userId, userData in pubList.items():
            totalGames = userData["total_games"]
            discord_id = userData["discord_id"]
            saved_name = userData["discord_name"]
            if discord_id:
                await UpdatePlayerPubs(bot,discord_id,saved_name,totalGames)
                await ctx.send(userData["discord_name"])

   

    
    async def StartupTask(bot):
        
        # totalList = []
        # for row in self.user_cur.execute(
        #     'SELECT "userID" FROM "main"."users"'
        # ):
        #     totalList.append(row[0])
        # return totalList
        return
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


    LeaderBoardUpdate.start()
    bot.run(BOT_TOKEN)