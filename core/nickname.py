import discord
import core.database
import re
async def UpdatePlayerElo(bot,userID: int,OnChange = False):


    try:
        member = await bot.guild.fetch_member(userID)
    except:
        return
    userData = await bot.database.get_player_info(member.id)
    print("UpdatePlayerElo------------------:")
    #Exactly what they have set
    currentRawName = member.nick
    if member.nick is None:
        currentRawName = member.name
    
    #What their name is set in the database
    savedName = userData["name"]
    
    currentCleanName = re.match("^(?:.(?![\\[\\(\\{]))*",currentRawName).group()


    showGamemode = userData["eloshow"]


    if OnChange:


        SetOff = False

        
        
        #if they are removing the formating
        if(currentRawName == savedName):
            SetOff = True


        if currentCleanName != savedName:
            await bot.database.set_player_nick(member.id,currentCleanName)

        #if member.id == 579767387600060423: return

        if showGamemode != -1:
            if SetOff:        
                await bot.database.set_player_show_elo(member.id,-1)
                await member.send("You have set or reset your username. It appeares you wanted to remove the elo ranking so I have turned it off for you. You can reenable it with /display")
            else:
                elo = userData[f"elo{showGamemode}"]
                pubs = userData["pubs"]
                
                if elo != 1000:
                    newName = f'{currentCleanName} ({pubs}) [{round(elo)}]'
                else:
                    newName = f'{currentCleanName} ({pubs})'
                print(newName)
                if newName != currentRawName and len(newName)<=32:
                    try:
                        print("Set")
                        await member.edit(nick=newName)
                    except :
                        print("Error setting nickname for "+newName)
                        pass
        else:
            if currentCleanName != currentRawName:
                await member.send("You are not allowed to put stats in your name. i have removed it automaticly")
                await member.edit(nick=currentCleanName)














    else:

        #if userID == 579767387600060423: return
        
        if showGamemode == -1: return


        elo = userData[f"elo{showGamemode}"]
        pubs = userData["pubs"]

        if elo != 1000:
            newName = f'{savedName} ({pubs}) [{round(elo)}]'
        else:
            newName = f'{savedName} ({pubs})'
        print(newName)
        if newName != currentRawName and len(newName)<=32:
            try:
                print("Set")

                await member.edit(nick=newName)
            except :
                print("Error setting nickname for "+newName)
                pass

    

        
     
   