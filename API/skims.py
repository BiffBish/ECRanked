import json
import traceback
from datetime import datetime
MapSettings = dict()
MapSettings["dyson"] = {
    "MapBounds":[-100,100,-40,40],
    "quality":[200*6,90*6]
    }
MapSettings["combustion"] = {
    "MapBounds":[-100,100,-20,60],
    "quality":[200*6,90*6]
    }
MapSettings["surge"] = {
    "MapBounds":[-50,70,-60,150],
    "quality":[200*6,90*6]
    }
MapSettings["fission"] = {
    "MapBounds":[-30,40,-80,130],
    "quality":[200*6,90*6]
    }

loadoutTable = {
    "0xC8C33E4832761FBC" : 0, #-- Repair Matrix
    "0x41D2D4381430080C" : 1,#-- Threat Scanner
    "0x41D2D43513260B1A" : 2,#-- Enery Barrier
    "0x41D2D02F1B2A1316" : 3,#-- Phase Shift

    "0xC8E8D0B1A894E7FE" : 0, #-- Detonator
    "0xC8C33E4829670BBE" : 4,#-- Stun Field
    "0xC8E8D0B1A891F0E9" : 8,#-- Arc Mine
    "0xE32DC7D8CC9D57A4" : 12,#-- Instant Repair

    "0x2FD69C8C5F615B9E" : 0, #-- Pulsar
    "0x2FD5839E4D605298" : 16,#-- Nova
    "0xE32DC7C9DA8051A4" : 32,#-- Comet
    "0x41D2D5321928020A" : 48,#-- Meteor
}

def InBoundingBox(position,Box):
    if position[0] < Box[0]:
        return False
    if position[0] > Box[1]:
        return False 
    if position[2] < Box[2]:
        return False
    if position[2] > Box[3]:
        return False  
    return True 
def CaculateSkims(replaydata):
    try:
        skimData = dict()
        skimData["frames"] = len(replaydata)-1
        startTime =  replaydata[0].split("\t")[0]
        endTime =  replaydata[-2].split("\t")[0]
        skimData["start_time"] = startTime[:-4]
        skimData["end_time"] = endTime[:-4]
        print (replaydata[0].split("\t")[0][:-4])
        matchLength = datetime.strptime(endTime.replace("/","-"),"%Y-%m-%d %H:%M:%S.%f") - datetime.strptime(startTime.replace("/","-"),"%Y-%m-%d %H:%M:%S.%f")
        skimData["match_length"] = matchLength.seconds
        skimData["framerate"] = (skimData["frames"]/skimData["match_length"])
        rawMapName = json.loads(replaydata[0].split("\t")[1])["map_name"]
        if rawMapName == "mpl_combat_combustion" :  skimData["map"] = "combustion"
        if rawMapName == "mpl_combat_dyson" :  skimData["map"] = "dyson"
        if rawMapName == "mpl_combat_fission" :  skimData["map"] = "fission"
        if rawMapName == "mpl_combat_gauss" :  skimData["map"] = "surge"
        skimData["players"] = dict()
        PlayerPosCache = dict()

        frameNumber = 0
        for frame in replaydata:
            if frame != "":
                frameDataRaw  = frame.split("\t")[1]
                frameData = json.loads(frameDataRaw)
                for TeamID in range(3):
                    team = frameData["teams"][TeamID]
                    if "players" in team:
                        for player in team["players"]:
                            #Generate the new player data
                            if player["name"] not in PlayerPosCache:
                                PlayerPosCache[player["name"]] = player["head"]["position"]



                            if player["name"] not in skimData["players"]:
                                playerData = dict()
                                playerData["team"] = TeamID
                                playerData["playerid"] = player["playerid"]
                                playerData["name"] = player["name"]
                                playerData["userid"] = player["userid"]
                                playerData["number"] = player["number"]
                                playerData["level"] = player["level"]
                                playerData["startFrame"] = frameNumber
                                playerData["stats"] = dict()
                                playerData["stats"]["total_frames"] = 0
                                playerData["stats"]["total_ping"] = 0
                                
                                playerData["stats"]["total_speed"] = 0
                                playerData["stats"]["frames_speed"] = 0

                                playerData["stats"]["total_upsidedown"] = 0
                                playerData["stats"]["frames_upsidedown"] = 0

                                playerData["stats"]["total_stopped"] = 0
                                playerData["stats"]["frames_stopped"] = 0

                                playerData["stats"]["total_deaths"] = 0
                                loadoutDict = dict()
                                for i in range(64):
                                    loadoutDict[i] = 0
                                playerData["stats"]["loadout"] = loadoutDict
                                playerData["stats"]["frames_loadout"] = 0
                                skimData["players"][player["name"]] = playerData

                            playerPosition = player["head"]["position"]
                            playerHeadRotationUp = player["head"]["up"]
                            velocity = player["velocity"]
                            skimData["players"][player["name"]]["stats"]["total_frames"] += 1
                            skimData["players"][player["name"]]["stats"]["total_ping"] += player["ping"]

                            if "Weapon" in player:
                                Weapon = player["Weapon"]
                                TechMod = player["Ability"]
                                Grenade = player["Grenade"]


                                LoadoutNumber = 0

                                if Weapon in loadoutTable:
                                    LoadoutNumber+= loadoutTable[Weapon]
                                if Grenade in loadoutTable:
                                    LoadoutNumber+= loadoutTable[Grenade]
                                if TechMod in loadoutTable:
                                    LoadoutNumber+= loadoutTable[TechMod]

                                skimData["players"][player["name"]]["stats"]["loadout"][LoadoutNumber] += 1
                                skimData["players"][player["name"]]["stats"]["frames_loadout"] += 1




                            currentPosition = player["head"]["position"]
                            playerBodyRotation = player["body"]["up"]

                            oldPosition = PlayerPosCache[player["name"]]

                            if InBoundingBox(currentPosition,MapSettings[skimData["map"]]["MapBounds"]):
                                if playerBodyRotation[1] < 0:
                                    skimData["players"][player["name"]]["stats"]["total_upsidedown"] += 1
                                
                                speed = ((velocity[0]**2) + (velocity[1]**2) + (velocity[2]**2))**.5

                                if speed < 1:
                                    skimData["players"][player["name"]]["stats"]["total_stopped"] += 1
                                else:
                                    skimData["players"][player["name"]]["stats"]["total_speed"] += speed
                                    skimData["players"][player["name"]]["stats"]["frames_speed"] += 1


                                skimData["players"][player["name"]]["stats"]["frames_stopped"] += 1
                                skimData["players"][player["name"]]["stats"]["frames_upsidedown"] += 1

                            elif InBoundingBox(oldPosition,MapSettings[skimData["map"]]["MapBounds"]):
                                skimData["players"][player["name"]]["stats"]["total_deaths"] += 1

                            PlayerPosCache[player["name"]] = currentPosition


            frameNumber += 1
        #Convert Player Dict into list
        PlayerDict = skimData["players"]
        PlayerList = []
        for value in skimData["players"].values():
            PlayerList.append(value)
        skimData["players"] = PlayerList
        return skimData
    
    except Exception as e:
        return {"error":str(e)}
    
