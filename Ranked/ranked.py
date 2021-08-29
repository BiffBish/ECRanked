@bot.slash.slash(
        name="play",
        description="Play a game with other people",
        options=[
            create_option(
                name="gamemode",
                description="The game mode you want to play",
                option_type=4,
                required=True,
                choices=[
                    create_choice(
                        name="Comet 1v1",
                        value=0
                    ),
                    create_choice(
                        name="Random Linked 1v1",
                        value=1
                    ),
                    create_choice(
                        name="Standard 1v1",
                        value=2
                    ),
                    create_choice(
                        name="Standard 2v2",
                        value=3
                    ),
                ]
            ),
            create_option(
                name="user1",
                description="A user you want to challenge",
                option_type=6,
                required=False,
            ),
            create_option(
                name="user2",
                description="A user you want to challenge",
                option_type=6,
                required=False,
            ),
            create_option(
                name="user3",
                description="A user you want to challenge",
                option_type=6,
                required=False,
            )
        ],
        guild_ids=GUILD_IDS,
    )
    async def _challenge(ctx, gamemode: int, user1=None, user2=None, user3=None):
        challange(ctx, gamemode, user1=user1, user2=user2, user3=user3)

    async def challange(ctx, gamemode: int, user1=None, user2=None, user3=None):
        challenged = []
        await ctx.send("Running command", hidden=True)
        ping = ""
        for user in (user1, user2, user3):
            if user:
                ping += user.mention + "\n"
                challenged.append(user.id)
        if ping != "":
            await ctx.send(ping)
        if gamemode < 3:
            await challenge_user(
                bot,
                ctx.author,
                await bot.fetch_channel(ctx.channel_id),
                challenged,
                gamemode,
            )

        if gamemode == 3:
            await Challenge2v2(
                bot,
                ctx.author,
                await bot.fetch_channel(ctx.channel_id),
                challenged,
            )
    print("setup slash Challenge")


    @bot.slash.slash(
        name="display",
        description="Change your displayed elo ranking",
        guild_ids=GUILD_IDS,
    )
    async def display(ctx):
        sender = await bot.database.get_player_info(ctx.author.id)
        components = [
            Select(
                placeholder="click to select what you would like to display!", 
                options=[
                    SelectOption(label="None", value=-1), 
                    SelectOption(label=f'[{ round(sender["elo0"]) }] Comet 1v1', value=0),
                    SelectOption(label=f'[{ round(sender["elo1"]) }] Linked Random 1v1', value=1),
                    SelectOption(label=f'[{ round(sender["elo2"]) }] Standerd 1v1', value=2),
                    SelectOption(label=f'[{ round(sender["elo3"]) }] Standard 2v2', value=3)
                ]
            )
        ]
        await ctx.send("What do you want to display?",components=components)
        def confirmcheck(res):
            return True
        interaction = await bot.wait_for("select_option", check=confirmcheck)

        print(interaction)
        print(interaction.component.label)

        await interaction.respond(content = f"{interaction.component.label} selected!")
        await bot.database.set_player_show_elo(ctx.author.id,interaction.component.value)

    
    
    @bot.slash.slash(
        name="elo",
        description="See your or another users elo",
        options=[
            create_option(
                name="user",
                description="Whos stats you want to see",
                option_type=6,
                required=False
            )
            ,
            create_option(
                name="gamemode",
                description="The game mode you want to see stats about",
                option_type=4,
                required=False,
                choices=[
                    create_choice(
                        name="Comet 1v1",
                        value=0
                    ),
                    create_choice(
                        name="Random Linked 1v1",
                        value=1
                    ),
                    create_choice(
                        name="Standard 1v1",
                        value=2
                    ),
                    create_choice(
                        name="Standard 2v2",
                        value=3
                    ),
                ]
            ),
        ],
        guild_ids=GUILD_IDS,
    )
    async def _elo(ctx, user=None, gamemode = 0):
        if user is None:
            user = ctx.author
        print(user)
        
        stats = await UserStats(user.id)
        embed = await GetEloCheck(bot, user)
        #file = discord.File("stats.png")
        #embed.set_image(url="attachment://stats.png")
        plot.statPlot(stats,Gamemode = gamemode)
        f = discord.File("stats.png", filename="image.png")
        e = discord.Embed()
        embed.set_image(url="attachment://image.png")
        await ctx.send(file=f,embed=embed)
   class Challenge(ButtonCog):
        @button("GameConfirm(?P<outcome>.+)")
        async def confirm_outcome(self, user, message, outcome):
            
            print(user,message,outcome)

            user_id = str(user.id)
            guild = self.bot.guild
            member = await guild.fetch_member(user.id)

            manager_role = discord.utils.find(
                lambda r: r.name == 'ECR moderator',
                guild.roles
            )

            is_manager = manager_role in member.roles
            print(is_manager)
            game_id = int(message.embeds[0].footer.text)
            game_data = self.bot.database.get_game_data(game_id)

            other_ids = None
            user_ids = None
            if user_id in game_data["team1"].split("|"):
                other_ids = game_data["team2"].split("|")
                user_ids = game_data["team1"].split("|")
            if user_id in game_data["team2"].split("|"):
                other_ids = game_data["team1"].split("|")
                user_ids = game_data["team2"].split("|")
            if user_ids is None and not is_manager:
                return
            if outcome == "Tie" and is_manager:
                await message.delete()
                return
            components = [
                [
                    Button(
                        style=ButtonStyle.green,
                        label=f"Win confirmed by {user.name}" if outcome == "Win" else "Confirm win",
                        disabled=outcome != "Loss",
                        id=f"GameAcceptWin_{other_ids[0]}",
                    ),
                    Button(
                        style=ButtonStyle.grey,
                        label="Confirm cancel",
                        disabled=outcome != "Tie",
                        id=f"GameAcceptTie_{other_ids[0]}",
                    ),
                    Button(
                        style=ButtonStyle.red,
                        label=f"Loss confirmed by {user.name}" if outcome == "Loss" else "Confirm Loss",
                        disabled=outcome != "Win",
                        id=f"GameAcceptLoss_{other_ids[0]}",
                    ),
                ],
                [
                    Button(
                        style=ButtonStyle.blue,
                        label="Undo or issue dispute",
                        id=f"GameUndoOrIssueDispute_{user_id}",
                    ),
                ]
            ]
            
            await message.edit(components=components)
            print(f"[confirm_outcome]{user.name}: {outcome}")

        @button("GameAccept(?P<outcome>.+)_(?P<clicker_id>[0-9]+)")
        async def accept_outcome(self, user, message, outcome, clicker_id):
            guild = message.guild
            user_id = str(user.id)
            member = await guild.fetch_member(user.id)
            manager_role = discord.utils.find(
                lambda r: r.name == 'ECR moderator',
                message.guild.roles
            )
            is_manager = manager_role in member.roles
            game_id = int(message.embeds[0].footer.text)
            game_data = self.bot.database.get_game_data(game_id)

            other_ids = None
            user_ids = None

            if user_id in game_data["team1"].split("|"):
                other_ids = game_data["team2"].split("|")
                user_ids = game_data["team1"].split("|")
            if user_id in game_data["team2"].split("|"):
                other_ids = game_data["team1"].split("|")
                user_ids = game_data["team2"].split("|")
            if user_ids is None and not is_manager:
                return

            if clicker_id not in user_ids and not is_manager:
                return
            await message.delete()
            if outcome == "Win":
                embed = await GameWin(self.bot, game_id, user_id)
                winmessage = await (
                    await self.bot.fetch_channel(ACTIVE_GAMES_CHANNEL)
                ).send(embed=embed)
                await (
                    await self.bot.fetch_channel(GAME_CHANNEL_ID)
                ).send(embed=embed)
                await asyncio.sleep(30)
                await winmessage.delete()
            if outcome == "Loss":
                embed = await GameWin(self.bot, game_id, other_ids[0])
                winmessage = await (
                    await self.bot.fetch_channel(ACTIVE_GAMES_CHANNEL)
                ).send(embed=embed)
                await (
                    await self.bot.fetch_channel(GAME_CHANNEL_ID)
                ).send(embed=embed)
                await asyncio.sleep(30)
                await winmessage.delete()
            
                
            print(f"[accept_outcome]{user.name}: {outcome} , {clicker_id}")

        
        @button("GameUndoOrIssueDispute_(?P<clicked_id>[0-9]+)")
        async def UndoOrDispute(self, user, message, clicked_id):
            
            user_id = str(user.id)
            guild = self.bot.guild
            member = await guild.fetch_member(user.id)
            
            manager_role = discord.utils.find(
                lambda r: r.name == 'ECR moderator',
                guild.roles
            )
            is_manager = manager_role in member.roles
            print(is_manager)


            game_id = int(message.embeds[0].footer.text)
            game_data = self.bot.database.get_game_data(game_id)

            other_ids = None
            user_ids = None
            if user_id in game_data["team1"].split("|"):
                other_ids = game_data["team2"].split("|")
                user_ids = game_data["team1"].split("|")
            if user_id in game_data["team2"].split("|"):
                other_ids = game_data["team1"].split("|")
                user_ids = game_data["team2"].split("|")
            if user_ids is None:
                return

            if clicked_id in user_ids or is_manager:
                components = [
                    [
                        Button(
                            style=ButtonStyle.green,
                            label="Confirm win",
                            id="GameConfirmWin",
                        ),
                        Button(
                            style=ButtonStyle.blue,
                            label="Confirm cancel",
                            id="GameConfirmTie",
                        ),
                        Button(
                            style=ButtonStyle.red,
                            label="Confirm loss",
                            id="GameConfirmLoss",
                        ),
                    ]
                ]
                await message.edit(components=components)

            elif clicked_id in other_ids:
                channel = await self.bot.fetch_channel(GAME_CHANNEL_ID)
                await channel.send(f"<@&853058237157867541> Dispute issued for game {game_id}")

            
                
            print(f"[UndoDisupte]{user.name}:")

    class Helper(ButtonCog):
        @button("GamePlayGamemode_(?P<gamemode>[0-9]+)")
        async def GamePlayGamemode_(self, user, message,gamemode):
            ctx = await bot.get_context(message)
            await ctx.send("Playing Game!")
            if int(gamemode) < 3:
                await challenge_user(
                    bot,
                    user,
                    await bot.fetch_channel(message.channel.id),
                    [],
                    int(gamemode),
                )

    class Leaderboard(ButtonCog):
        @button("Leaderboard_(?P<Term>[^_]*)_(?P<Key>[^\n]*)")
        async def confirm_outcome(self, user, message, Term, Key):
            if Term == "C1v1SK":
                self.bot.C1v1SK = Key
            if Term == "LRL1v1SK":
                self.bot.LRL1v1SK = Key  
            await MainLeaderboard(self.bot)



    bot.add_buttons(Challenge(bot))
    bot.add_buttons(Leaderboard(bot))
    bot.add_buttons(Helper(bot))
    
        def add_buttons(self, buttons: ButtonCog) -> None:
            """Add a button cog to the bot."""
            if not isinstance(buttons, ButtonCog):
                raise ValueError("Only a ButtonCog instance can be loaded")

            for key, value in buttons.buttons.items():
                if key in self.buttons:
                    raise TypeError(f"Button {key} is already defined.")
                self.buttons[key] = value

        def remove_buttons(self, buttons: ButtonCog) -> None:
            """Remove a button cog from the bot."""
            if not isinstance(buttons, ButtonCog):
                raise ValueError("Only a ButtonCog instance can be unloaded")

            for key in buttons.buttons:
                if key in self.buttons:
                    self.buttons.pop(key)
                else:
                    raise TypeError(f"No button for match {key} is not defined.")

