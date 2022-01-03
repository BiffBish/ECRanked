import discord
import core.database
import re
async def UpdatePlayerPubs(bot,userID: int,saved_name,total_games,OnChange = False):

    try:
        member = await bot.guild.fetch_member(userID)
    except Exception as E:
        print(E)
        return
    print(f"UpdatePlayerElo------------------:{total_games}")
    #Exactly what they have set
    currentRawName = member.nick
    if member.nick is None:
        currentRawName = member.name
    
    #What their name is set in the database
    
    currentCleanName = re.match("^(?:.(?![\\[\\(\\{]))*",currentRawName).group()
    print(f"currentCleanName : {currentCleanName}")
    print(f"saved_name : {saved_name}")
    if OnChange:
        if currentCleanName != saved_name:
            bot.database.set_player_nick(member.id,currentCleanName)


        newName = f'{currentCleanName} ({total_games})'
        
        if newName != currentRawName and len(newName)<=32:
            try:
                print("Set")
                await member.edit(nick=newName)
            except :
                print("Error setting nickname for "+newName)
                pass

    else:
        if currentCleanName != saved_name:
            bot.database.set_player_nick(member.id,currentCleanName)
        newName = f'{currentCleanName} ({total_games})'
        if newName != currentRawName and len(newName)<=32:
            try:
                print("Set")

                await member.edit(nick=newName)
            except :
                print("Error setting nickname for "+newName)
                pass

    

        
     
   