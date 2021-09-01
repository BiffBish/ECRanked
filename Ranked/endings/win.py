import discord

from ..elo import WinLosses
from .. import nickname
from core.leaderboard import MainLeaderboard
async def GameWin(bot, game_id, winner_id, justEloCalc = False):
    game_data = bot.database.get_game_data(game_id)
    if winner_id in game_data["team1"].split("|"):
        winner_ids = game_data["team1"].split("|")
        loser_ids = game_data["team2"].split("|")
    elif winner_id in game_data["team2"].split("|"):
        winner_ids = game_data["team2"].split("|")
        loser_ids = game_data["team1"].split("|")
    else:
        return discord.Embed(
            title="Error",
            description="There was an error. please contact the owner",
            color=0xff80c2,
        )

    print("GameWin : ")
    print(winner_id)
    eloType = f"elo{game_data['gamemode']}"

    winners = [await bot.fetch_user(id) for id in winner_ids]
    losers = [await bot.fetch_user(id) for id in loser_ids]

    winner_datas = [await bot.database.get_player_info(id) for id in winner_ids]
    loser_datas = [await bot.database.get_player_info(id) for id in loser_ids]

    winner_elos = [data[eloType] for data in winner_datas]
    loser_elos = [data[eloType] for data in loser_datas]

    winner_elos_after, loser_elos_after = WinLosses(winner_elos, loser_elos)

    for player, elo in zip(winners + losers, winner_elos_after + loser_elos_after):
        await bot.database.set_player_elo(player.id, elo, game_data["gamemode"])

    winner_changes = [eloafter - elo for eloafter, elo in zip(winner_elos_after, winner_elos)]
    loser_changes = [eloafter - elo for eloafter, elo in zip(loser_elos_after, loser_elos)]

    winnerstrs = [f'{user.mention} [+{round(change)}] ({round(eloafter)})' for user, change, eloafter in
                  zip(winners, winner_changes, winner_elos_after)]
    loserstrs = [f'{user.mention} [{round(change)}] ({round(eloafter)})' for user, change, eloafter in
                 zip(losers, loser_changes, loser_elos_after)]

    embed = discord.Embed(
        title="Game Finished",
        description="A game has been finished",
        color=0xff80c2,
    )
    embed.add_field(name="Winner", value="\n".join(winnerstrs), inline=True)
    embed.add_field(name="Loser", value="\n".join(loserstrs), inline=True)
    embed.set_footer(text=game_id)
    if not justEloCalc:
        print("UpdatingExtras")
        bot.database.set_winner(game_id, "|".join(winner_ids))
        for user in winners + losers:
            await nickname.UpdatePlayerElo(bot,user.id)

        await MainLeaderboard(bot)
    return embed
