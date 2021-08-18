import asyncio

import discord
from discord_components import Button, ButtonStyle

from .. import constants, colors, gameModes


async def challenge_user(client, sender, channel, challenged, gamemode):
    gamemodes = ["Comet 1v1", "Linked Random Loadout 1v1", "Standard 1v1"]
    receiver = None

    if challenged:
        # initial Challenge
        embed = discord.Embed(
            color=colors.ChallengeEmbed,
            title=f"Hey, {sender.name} Wants to play a {gamemodes[gamemode]}",
        )
        acceptdenycomps = [
            [
                Button(style=ButtonStyle.green, label="Accept"),
                Button(style=ButtonStyle.red, label="Decline")
            ]
        ]
        message = await channel.send(embed=embed, components=acceptdenycomps)

        def confirmcheck(res):
            return res.user.id == challenged[0] and str(res.message.id) == str(message.id)
        try:
            res = await client.wait_for(
                "button_click", check=confirmcheck, timeout=10800)
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

        if res.component.label == "Decline":
            embed = discord.Embed(
                color=discord.Colour.red(),
                title=f'{res.user.name} has declined.',
            )
            await message.edit(embed=embed, components=[])
            return
        receiver = res.user

    else:
        embed = discord.Embed(
            color=colors.ChallengeEmbed,
            title=f"Hey, {sender.name} Wants to play a {gamemodes[gamemode]}",
        )
        message = await channel.send(embed=embed)
        await message.edit(components=[
            [
                Button(
                    style=ButtonStyle.green,
                    label='Click to join! (0/1)',
                    id="ChallengeJoin",
                ),
                Button(
                    style=ButtonStyle.red,
                    label='Cancel',
                    id="DeleteMessage",
                )
            ]
        ])

        def confirmcheck(res):
            if res.user.id == sender.id and res.component.id == "DeleteMessage":
                return True
            return  res.user.id != sender.id and str(res.message.id) == str(message.id)
        try:
            res = await client.wait_for(
                "button_click", check=confirmcheck, timeout=10800)
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
            receiver = res.user
        if res.component.id == "DeleteMessage":
            await message.delete()

    if gamemode == 0:
        embed, game_id = await gameModes.Comet1v1(
            client,
            sender,
            receiver,
        )
    if gamemode == 1:
        embed, game_id = await gameModes.LinkedRandomLoadout1v1(
            client,
            sender,
            receiver,
        )
    if gamemode == 2:
        embed, game_id = await gameModes.Standard1v1(
            client,
            sender,
            receiver,
        )

    await message.delete()
    
    await channel.send(content=sender.mention+"\n"+receiver.mention)
    
    message = await channel.send(embed=embed)

    embed = discord.Embed(
        title=f"Echo Combat Ranked : {gamemodes[gamemode]}",
        description="A game has begun. Come back here and sumbit the results",
        color=colors.ResultsEmbed,
    )
    embed.add_field(name="Team 1", value=f'{sender.mention}', inline=True)
    embed.add_field(name="Team 2", value=f'{receiver.mention}', inline=True)
    
    embed.add_field(name="link",    value=message.jump_url)
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

    components = [
        [
            Button(
                style=ButtonStyle.URL,
                label="Enter your results!",
                url=message.jump_url,
            ),
        ]
    ]
    await channel.send(embed=embed, components=components)
