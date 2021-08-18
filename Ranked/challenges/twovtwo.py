import asyncio

import discord
from discord_components import Button, ButtonStyle

from .. import colors, constants, elo, gameModes


async def Challenge2v2(client, sender, channel, challenged):
    if len(challenged) > 3:
        return

    players = []

    # initial Challenge
    embed = discord.Embed(
        color=colors.ChallengeEmbed,
        title=f"{sender.name} Wants to play a Standard 2v2",
    )
    enteredPlayers = [
        Button(
            style=ButtonStyle.gray,
            label=sender.name,
            id=sender.id,
            disabled=True,
        )
    ]  
    message = await channel.send(embed=embed)

    await message.edit(components=[
        enteredPlayers,
        [
            Button(
                style=ButtonStyle.green,
                label=f'Accept Challenge! (0/{len(challenged)})',
                id="ChallengeJoin",
            ),
            Button(
                style=ButtonStyle.red,
                label="Decline Challenge!",
                id="ChallengeNope",
            )
        ]
    ])

    if challenged:
        while len(players) < len(challenged):
            def confirm_check(res):
                print(res)
                return res.user.id in challenged and res.user.id not in players and res.channel.id == channel.id and str(res.message.id) == str(message.id)
            try:
                res = await client.wait_for(
                    "button_click", check=confirm_check, timeout=10800)
            except asyncio.TimeoutError:
                await message.edit(
                    embed=discord.Embed(
                        color=0xED564E,
                        title="Timeout!",
                        description="No-one reacted. ☹️",
                    ),
                    components=[
                        Button(
                            style=ButtonStyle.red,
                            label="Oh-no! Timeout reached!",
                            disabled=True,
                        )
                    ],
                )
                return
            await res.respond(type=6)

            if res.component.id == "ChallengeJoin":
                players.append(res.user.id)
                enteredPlayers.append(
                    Button(
                        style=ButtonStyle.gray,
                        label=res.user.name,
                        id=res.user.id,
                        disabled=True,
                    ),
                )
                await message.edit(
                    embed=embed,
                    components=[
                        enteredPlayers,
                        [
                            Button(
                                style=ButtonStyle.green,
                                label=f"Accept Challenge! ({len(players)}/{len(challenged)})",
                                id="ChallengeJoin",
                            ),
                            Button(
                                style=ButtonStyle.red,
                                label=f"Decline Challenge!",
                                id="ChallengeNope",
                            )
                        ]
                    ],
                )
            if res.component.id == "ChallengeNope":
                # embed = discord.Embed(color=discord.Colour.red(), title=f'{reciver.name} has declined.')
                players.append(res.user.id)
                enteredPlayers.append(
                    Button(
                        style=ButtonStyle.gray,
                        label=res.user.name,
                        id=res.user.id,
                        disabled=True,
                    ),
                )
                await message.edit(
                    embed=discord.Embed(
                        color=0xED564E,
                        title="Decline!",
                        description=f'{res.user.name} declined the challenge',
                    ),
                    components=[],
                )
                return

    players.append(sender.id)

    await message.edit(components=[
        enteredPlayers,
        [
            Button(
                style=ButtonStyle.green,
                label=f'Click to join! ({len(players)}/4)',
                id="ChallengeJoin",
            ),
            Button(
                style=ButtonStyle.red, label=f'Cancel', id="CancelChallange")
        ]
    ])

    for _ in range(4 - len(players)):

        def confirmcheck2(res):
            if res.user.id in players and res.component.id == "CancelChallange":
                return True
            return res.user.id not in players and res.channel.id == channel.id and str(res.message.id) == str(message.id)
        try:
            res = await client.wait_for(
                "button_click", check=confirmcheck2, timeout=10800)
        except asyncio.TimeoutError:
            await message.edit(
                embed=discord.Embed(
                    color=0xED564E,
                    title="Timeout!",
                    description="No-one reacted. ☹️",
                ),
                components=[
                    Button(
                        style=ButtonStyle.red,
                        label="Oh-no! Timeout reached!",
                        disabled=True,
                    )
                ],
            )
            return
        await res.respond(type=6)
        if res.component.id == "ChallengeJoin":
            players.append(res.user.id)
            enteredPlayers.append(
                Button(
                    style=ButtonStyle.gray,
                    label=res.user.name,
                    id=res.user.id,
                    disabled=True,
                ),
            )
            await message.edit(
                embed=embed,
                components=[
                    enteredPlayers,
                    [
                        Button(
                            style=ButtonStyle.green,
                            label=f"Click to join! ({len(players)}/4)",
                            id="ChallengeJoin",
                        )
                    ]
                ],
            )
        elif res.component.id == "CancelChallange":
            await message.delete()
            await message.edit(
                embed=embed,
                components=[
                    enteredPlayers,
                    [
                        Button(
                            style=ButtonStyle.green,
                            label=f"Click to join! ({len(players)}/4)",
                            id="ChallengeJoin",
                        )
                    ]
                ],
            )

    await channel.send(content="Found 4 people")

    data = [(await client.database.get_player_info(id)) for id in players]
    print(data)
    result = elo.Generate2v2Teams(data)
    print(result)

    embed, game_id = await gameModes.Standard2v2(result)
    await message.delete()


    p1 = (await client.fetch_user(result[0][0]["id"])).mention
    p2 = (await client.fetch_user(result[0][1]["id"])).mention
    p3 = (await client.fetch_user(result[1][0]["id"])).mention
    p4 = (await client.fetch_user(result[1][1]["id"])).mention

    mentionstr = f'{p1}\n{p2}\n{p3}\n{p4}\n'
    message = await channel.send(content=mentionstr)
    await channel.send(embed=embed, components=[])

    embed = discord.Embed(
        title="Echo Combat Ranked : 2v2 Standard",
        description="A game has begun. Come back here and sumbit the results",
        color=colors.TeamEmbed,
    )
    embed.add_field(name="Team 1", value=f'{p1}\n{p2}', inline=True)
    embed.add_field(name="Team 2", value=f'{p3}\n{p4}', inline=True)
    embed.set_footer(text=str(game_id))

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
    game_channel = await client.fetch_channel(constants.ACTIVE_GAMES_CHANNEL)

    message = await game_channel.send(embed=embed, components=components)

    await channel.send(embed=embed)
    components = [
        [
            Button(
                style=ButtonStyle.URL,
                label="Enter your results!",
                url=message.jump_url,
            ),
        ]
    ]
    await message.edit(embed=embed)
