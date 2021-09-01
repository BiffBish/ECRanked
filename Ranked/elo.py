import discord


def expected(playera, playerb):
    """Calculate expected score of A in a match against B.

    :param playera: Elo rating for player A
    :param playerb: Elo rating for player B
    """
    return 1 / (1 + 10 ** ((playerb - playera) / 400))


def elo(old, exp, score, k=32):
    """Calculate the new Elo rating for a player.

    :param old: The previous Elo rating
    :param exp: The expected score for this match
    :param score: The actual score for this match
    :param k: The k-factor for Elo (default: 32)
    """
    return old + k * (score - exp)

def Tie(p1, p2, k=32):

    p1exp = expected(p1, p2)
    p2exp = expected(p2, p1)

    print("Before Elo:")
    print((p1exp, p2exp))
    print((p1, p2))
    p1after = elo(p1, p1exp, .5, k=k)
    p2after = elo(p2, p2exp, .5, k=k)
    print("After Elo:")
    print((p1after, p2after))
    return p1after, p2after


def Generate2v2Teams(users: list):
    eloKey = "elo3"

    Total = 0
    for user in users:
        Total += user[eloKey]
    print(Total)

    d0 = abs(users[0][eloKey]+users[1][eloKey] - (Total/2))
    d1 = abs(users[0][eloKey]+users[2][eloKey] - (Total/2))
    d2 = abs(users[0][eloKey]+users[3][eloKey] - (Total/2))

    print("2v2 elo:")

    print(d0, d1, d2)
    if d0 <= d1 and d0 <= d2:
        return [[users[0], users[1]], [users[2], users[3]]]
    if d1 <= d0 and d1 <= d2:
        return [[users[0], users[2]], [users[1], users[3]]]
    if d2 <= d1 and d2 <= d0:
        return [[users[0], users[3]], [users[1], users[2]]]


def WinLosses(winnerelos, loserelos, k = 32):
    winnerExps = [expected(old_elo, sum(loserelos) / len(loserelos)) for old_elo in winnerelos]
    loserExps = [expected(old_elo, sum(winnerelos) / len(winnerelos)) for old_elo in loserelos]
    winner_elos_after = [elo(old_elo, exp, 1, k) for old_elo, exp in zip(winnerelos, winnerExps)]
    loser_elos_after = [elo(old_elo,exp,0,k) for old_elo,exp in zip(loserelos,loserExps)]
    return winner_elos_after,loser_elos_after


# test = (1016.0, 984.0)
# print(WinLose(1016.0, 984.0))


async def GetEloCheck(client, user):
    userData = await client.database.get_player_info(user.id)

    string1v1 = ""
    string2v2 = ""
    string1v1 += f'[{str(round(userData["elo0"]))}] Comet 1v1 \n'
    string1v1 += f'[{str(round(userData["elo1"]))}] Linked Random 1v1 \n'
    string1v1 += f'[{str(round(userData["elo2"]))}] Standard 1v1 \n'
    string2v2 += f'[{str(round(userData["elo3"]))}] Standard 2v2 \n'

    embed = discord.Embed(
        title="Elo Stats",
        description=f"Here are the stats for {user.mention}",
        color=0x80ff8c,
    )
    embed.add_field(name="1v1", value=string1v1, inline=False)
    embed.add_field(name="2v2", value=string2v2, inline=False)
    return embed
