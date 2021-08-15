import discord

from .. import constants, elo


async def GameTie(client, game_id):
    client.database.set_winner(game_id, 0)
    game_data = client.database.get_game_data(game_id)

    p1Data = await client.database.get_player_info(game_data["team1"])
    p2Data = await client.database.get_player_info(game_data["team2"])

    eloType = f"elo{game_data['gamemode']}"
    p1 = await client.fetch_user(p1Data["id"])
    p2 = await client.fetch_user(p2Data["id"])

    p1AfterElo, p2AfterElo = elo.Tie(p1Data[eloType], p2Data[eloType])

    client.database.set_player_elo(
        p1Data["id"], p1AfterElo, game_data["gamemode"])
    client.database.set_player_elo(
        p2Data["id"], p2AfterElo, game_data["gamemode"])

    embed = discord.Embed(
        title="Game Finished",
        description="A game has been finished",
        color=0xff0000,
    )
    embed.add_field(name="Player 1", value=p1.mention, inline=True)
    embed.add_field(name="Player 2", value=p2.mention, inline=True)
    embed.add_field(name="\u200b", value="\u200b")
    p1_change = p1AfterElo - p1Data[eloType]
    p2_change = p2AfterElo - p2Data[eloType]
    if p1_change > 0:
        embed.add_field(
            name="ELO",
            value=f"{round(p1Data[eloType], 2)} + {round(p1_change)}",
            inline=True,
        )
    else:
        embed.add_field(
            name="ELO",
            value=f"{round(p1Data[eloType], 2)} - {round(0-p1_change)}",
            inline=True,
        )

    if p2_change > 0:
        embed.add_field(
            name="ELO",
            value=f"{round(p2Data[eloType], 2)} + {round(p2_change)}",
            inline=True,
        )
    else:
        embed.add_field(
            name="ELO",
            value=f"{round(p2Data[eloType], 2)} - {round(0-p2_change)}",
            inline=True,
        )

    game_channel = await client.fetch_channel(constants.GAME_CHANNEL_ID)
    await game_channel.send(embed=embed)
