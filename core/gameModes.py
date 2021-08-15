import random

import discord

from . import colors


def basic_gen(
    title,
    description,
    start,
    weapon: str = None,
    showweapon=True,
    weaponinline=True,
    ordinance_mod=False,
    loadout=None,
    team=False,
    showmap=True,
    whitespace=False,
) -> discord.Embed:
    """Generate standard embed."""
    weapons = ("Nova", "Comet", "Meteor", "Pulsar")
    ordinances = ("Arc Mine", "Stun Field", "Detonator", "Instant Repair")
    tech_mods = (
        "Phase Shift",
        "Repair Matrix",
        "Threat Scanner",
        "Force Field",
    )
    maps = ("Dyson", "Combustion")
    map_choice = random.choice(maps)

    embed = discord.Embed(
        title=title,
        description=description,
        color=colors.GameModeEmbed
    )

    embed.add_field(
        name="Start",
        value=(
            "Both of "
            + ("the teams will go to their" if team else "you will go to the")
            + " starting positions of the chosen map "
            f"and one person chooses who will start the round. {start}"
        ),
        inline=True,
    )
    embed.add_field(
        name="Goal",
        value=(
            "Your goal is to kill the other team. "
            "Whatever team is left standing gets a point"
            if team else
            "Your goal is to kill the other person. "
            "Whoever kills the other first gets a point"
        ),
        inline=True,
    )

    embed.add_field(
        name="Reset",
        value=(
            (
                "When both people on a team dies everyone goes" if team else
                "When the other person dies you both go"
            )
            + " back to the starting "
            "position and wait for y'alls abilities to recharge"
        ),
        inline=True,
    )

    embed.add_field(
        name="Win Condition",
        value="First to 3 points win",
        inline=True,
    )

    if whitespace:
        embed.add_field(name="\u200b", value="\u200b")
    if showmap:
        embed.add_field(name="Map", value=map_choice, inline=weaponinline)
    if whitespace:
        embed.add_field(name="\u200b", value="\u200b")

    if showweapon:
        embed.add_field(
            name="Weapon",
            value=weapon or random.choice(weapons),
            inline=weaponinline,
        )
    if ordinance_mod:
        embed.add_field(
            name="Ordinance",
            value=random.choice(ordinances),
            inline=True,
        )
        embed.add_field(
            name="Attack Mod",
            value=random.choice(tech_mods),
            inline=True,
        )

    if loadout:
        embed.add_field(name="Loadout", value=loadout, inline=False)

    if not map:
        return embed
    if map_choice == "Dyson":
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/852667904146538578/854480257019805696/Dyson.png"
        )
    elif map_choice == "Combustion":
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/852667904146538578/854480284900261898/combustion.png"
        )
    return embed


async def LinkedRandomLoadout1v1(client, p1, p2):
    embed = basic_gen(
        title="Linked Random Loadout 1v1",
        description="Both of y'all have to use this loadout for the 1v1",
        start="When the person fires their weapon both of you aim to kill the other.",
        ordinance_mod=True,
        whitespace=True,
    )

    return embed, client.database.create_new_1v1_game(p1, p2, 1)


async def Comet1v1(client, p1, p2):
    embed = basic_gen(
        title="Comet 1v1",
        description="A 1v1 with only a Comet",
        start="When the person fires their comet both of you aim to kill the other.",
        weapon="Comet",
        weaponinline=False,
    )

    return embed, client.database.create_new_1v1_game(p1, p2, 0)


async def Standard1v1(client, p1, p2):
    embed = basic_gen(
        title="Standard 1v1",
        description="A Standard 1v1",
        start="When the person fires their weapon both of you aim to kill the other.",
        loadout="Anything",
        weaponinline=False,
    )
    return embed, client.database.create_new_1v1_game(p1, p2, 0)


async def Standard2v2(client, pdata):
    embed = basic_gen(
        title="Standard 2v2",
        description="A Standard 2v2",
        start="When the person fires their weapon both teams aim to kill the other.",
        team=True,
        weapon="No duplicate anything on the same team",
        weaponinline=False,
    )

    return embed, client.database.create_new_2v2_game(pdata)


def HelpLinkedRandomLoadout1v1():
    return basic_gen(
        title="Linked Random Loadout 1v1",
        description="Everyone uses the same Random Loadout",
        start="When the person fires their weapon both of you aim to kill the other.",
        showweapon=False,
        showmap=False,
    )


def HelpComet1v1():
    embed = basic_gen(
        title="Comet 1v1",
        description="A 1v1 with only a Comet",
        start="When the person fires their comet both of you aim to kill the other.",
        weapon="Comet",
    )
    return embed


def HelpStandard1v1():
    embed = basic_gen(
        title="Standard 1v1",
        description="A Standard 1v1",
        start="When the person fires their weapon both of you aim to kill the other.",
        loadout="Anything",
        showweapon=False,
    )
    return embed


def HelpStandard2v2():
    embed = basic_gen(
        title="Standard 2v2",
        description="A Standard 2v2",
        start="When the person fires their weapon both teams aim to kill the other.",
        team=True,
        weapon="No duplicate anything on the same team",
    )
    return embed
