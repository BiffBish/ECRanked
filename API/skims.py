#version 2021-01-04
import json
from logging import error
import traceback
from datetime import datetime
from datetime import timedelta
import pytz
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
    "0x41D2D4381430080C" : 1, #-- Threat Scanner
    "0x41D2D43513260B1A" : 2, #-- Energy Barrier
    "0x41D2D02F1B2A1316" : 3, #-- Phase Shift
    "heal": 0,
    "sensor": 1,
    "shield": 2,
    "wraith": 3,
    "0xC8E8D0B1A894E7FE" : 0, #-- Detonator
    "0xC8C33E4829670BBE" : 4, #-- Stun Field
    "0xC8E8D0B1A891F0E9" : 8, #-- Arc Mine
    "0xE32DC7D8CC9D57A4" : 12,#-- Instant Repair
    "det":0,
    "stun":4,
    "arc":8,
    "burst":12,
    "0x2FD69C8C5F615B9E" : 0, #-- Pulsar
    "0x2FD5839E4D605298" : 16,#-- Nova
    "0xE32DC7C9DA8051A4" : 32,#-- Comet
    "0x41D2D5321928020A" : 48,#-- Meteor
    "assault":0,
    "blaster":16,
    "scout":32,
    "rocket":48,
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

def GetSquaredDistance(position,position2):
    return ((position[0] - position2[0])**2) +  ((position[1] - position2[1])**2)+  ((position[2] - position2[2])**2)
def CaculateSkims(replaydata):
    try:
        TimeFormat = "%Y-%m-%d %H:%M:%S.%f"
        TimeFormatS = "%Y-%m-%d %H:%M:%S"
        skimData = dict()
        skimData["session_id"] = json.loads(replaydata[0].split("\t")[1])["sessionid"]
        skimData["frames"] = len(replaydata)-1
        startTime =  replaydata[0].split("\t")[0]
        endTime =  replaydata[-2].split("\t")[0]

        dt = datetime.strptime(startTime[:19].replace("/","-"), '%Y-%m-%d %H:%M:%S')
        tz = pytz.timezone('Europe/London')
        loc_dt = tz.localize(dt)        
        skimData["start_time"] = int(loc_dt.timestamp())
        dt = datetime.strptime(endTime[:19].replace("/","-"), '%Y-%m-%d %H:%M:%S')
        tz = pytz.timezone('Europe/London')
        loc_dt = tz.localize(dt)        
        skimData["end_time"] = int(loc_dt.timestamp())
        
        matchLength = datetime.strptime(endTime.replace("/","-"),TimeFormat) - datetime.strptime(startTime.replace("/","-"),TimeFormat)
        skimData["match_length"] = matchLength.seconds
        skimData["framerate"] = (skimData["frames"]/skimData["match_length"])
        rawMapName = json.loads(replaydata[0].split("\t")[1])["map_name"]
        if rawMapName == "mpl_combat_combustion" :  skimData["map"] = "combustion"
        if rawMapName == "mpl_combat_dyson" :  skimData["map"] = "dyson"
        if rawMapName == "mpl_combat_fission" :  skimData["map"] = "fission"
        if rawMapName == "mpl_combat_gauss" :  skimData["map"] = "surge"
        skimData["players"] = dict()
        PlayerPosCache = dict()

        PlayerLoadoutCache = dict()

        frameNumber = 0


        frameSpeedBuffer = dict()
        frameSpeedBufferSize = skimData["framerate"]
        for frame in replaydata:
            try:
                if frame != "":
                    frameDataRaw  = frame.split("\t")[1]
                    frameData = json.loads(frameDataRaw)
                    for TeamID in range(2):
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

                                    playerData["crashed"] = False
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


                                    playerData["stats"]["top_speed"] = 0

                                    playerData["stats"]["frames_left"] = 0
                                    playerData["stats"]["frames_right"] = 0

                                    playerData["stats"]["total_close_mate"] = 0
                                    playerData["stats"]["total_close_enemy"] = 0
                                    playerData["stats"]["frames_close_mate"] = 0
                                    playerData["stats"]["frames_close_enemy"] = 0

                                    playerData["stats"]["total_deaths"] = 0
                                    loadoutDict = dict()
                                    for i in range(64):
                                        loadoutDict[i] = 0
                                    playerData["stats"]["loadout"] = loadoutDict
                                    playerData["stats"]["frames_loadout"] = 0



                                    playerData["framestamps"] = dict()
                                    playerData["framestamps"]["loadout"] = list()
                                    playerData["framestamps"]["deaths"] = list()
                                    playerData["framestamps"]["respawns"] = list()
                                    playerData["framestamps"]["in_bounds"] = list()

                                    skimData["players"][player["name"]] = playerData


                                
                                playerPosition = player["head"]["position"]
                                playerHeadRotationUp = player["head"]["up"]
                                velocity = player["velocity"]

                                skimData["players"][player["name"]]["stats"]["total_frames"] += 1

                                skimData["players"][player["name"]]["stats"]["total_ping"] += player["ping"]




                                currentPosition = player["head"]["position"]
                                playerBodyRotation = player["body"]["up"]

                                oldPosition = PlayerPosCache[player["name"]]

                                ##IF YOUR IN THE MAP BOUNDS
                                if InBoundingBox(currentPosition,MapSettings[skimData["map"]]["MapBounds"]):

                                    ## GOING INTO THE MAP
                                    if not InBoundingBox(oldPosition,MapSettings[skimData["map"]]["MapBounds"]):
                                        skimData["players"][player["name"]]["framestamps"]["in_bounds"].append([frameNumber,True])

                                        
                                    if playerBodyRotation[1] < 0:
                                        skimData["players"][player["name"]]["stats"]["total_upsidedown"] += 1
                                    
                                    speed = ((velocity[0]**2) + (velocity[1]**2) + (velocity[2]**2))**.5
                                    if (player["name"] not in frameSpeedBuffer):
                                        frameSpeedBuffer[player["name"]] = []
                                    if len(frameSpeedBuffer[player["name"]]) > frameSpeedBufferSize:
                                        frameSpeedBuffer[player["name"]].pop(0)
                                    frameSpeedBuffer[player["name"]].append(speed)



                                    if (skimData["players"][player["name"]]["stats"]["top_speed"] < min(frameSpeedBuffer[player["name"]])):
                                        skimData["players"][player["name"]]["stats"]["top_speed"] = min(frameSpeedBuffer[player["name"]])
                                    if speed < 1:
                                        skimData["players"][player["name"]]["stats"]["total_stopped"] += 1
                                    else:
                                        skimData["players"][player["name"]]["stats"]["total_speed"] += speed
                                        skimData["players"][player["name"]]["stats"]["frames_speed"] += 1


                                    skimData["players"][player["name"]]["stats"]["frames_stopped"] += 1
                                    skimData["players"][player["name"]]["stats"]["frames_upsidedown"] += 1

                                    if "Arm" in player:
                                        if player["Arm"] == "Right":
                                            skimData["players"][player["name"]]["stats"]["frames_right"] += 1
                                        else:
                                            skimData["players"][player["name"]]["stats"]["frames_left"] += 1
                                    if "Weapon" in player:
                                        if "Ability" in player:
                                            Weapon = player["Weapon"]
                                            TechMod = player["Ability"]
                                            Grenade = player["Grenade"]
                                        else:
                                            Weapon = player["Weapon"]
                                            TechMod = player["TacMod"]
                                            Grenade = player["Ordnance"]

                                        LoadoutNumber = 0

                                        if Weapon in loadoutTable:
                                            LoadoutNumber+= loadoutTable[Weapon]
                                        if Grenade in loadoutTable:
                                            LoadoutNumber+= loadoutTable[Grenade]
                                        if TechMod in loadoutTable:
                                            LoadoutNumber+= loadoutTable[TechMod]
                                        if player["name"] not in PlayerLoadoutCache:
                                            PlayerLoadoutCache[player["name"]] = LoadoutNumber
                                            skimData["players"][player["name"]]["framestamps"]["loadout"].append([frameNumber,LoadoutNumber])

                                        if LoadoutNumber != PlayerLoadoutCache[player["name"]]:

                                            PlayerLoadoutCache[player["name"]] = LoadoutNumber
                                            skimData["players"][player["name"]]["framestamps"]["loadout"].append([frameNumber,LoadoutNumber])
                                        skimData["players"][player["name"]]["stats"]["loadout"][LoadoutNumber] += 1
                                        skimData["players"][player["name"]]["stats"]["frames_loadout"] += 1


                                    currentPosition
                                    closeToTm8 = False
                                    closeToEnemy = False

                                    for otherplayer in team["players"]:
                                        if player["name"] != otherplayer["name"]:
                                            otherplayerPosition = otherplayer["head"]["position"]
                                            distance = GetSquaredDistance(currentPosition,otherplayerPosition)
                                            if distance < 1:
                                                closeToTm8 = True
                                                break


                                    otherTeamID = 1 if TeamID == 0 else 0
                                    if "players" in frameData["teams"][otherTeamID]:
                                        for otherplayer in frameData["teams"][otherTeamID]["players"]:
                                            otherplayerPosition = otherplayer["head"]["position"]
                                            distance = GetSquaredDistance(currentPosition,otherplayerPosition)
                                            if distance < 1:
                                                closeToEnemy = True
                                                break

                                    if (closeToTm8):
                                        skimData["players"][player["name"]]["stats"]["frames_close_mate"] += 1
                                    if (closeToEnemy):
                                        skimData["players"][player["name"]]["stats"]["frames_close_enemy"] += 1
                                    skimData["players"][player["name"]]["stats"]["total_close_mate"] += 1
                                    skimData["players"][player["name"]]["stats"]["total_close_enemy"] += 1

                                elif InBoundingBox(oldPosition,MapSettings[skimData["map"]]["MapBounds"]):
                                    skimData["players"][player["name"]]["stats"]["total_deaths"] += 1   
                                    skimData["players"][player["name"]]["framestamps"]["deaths"].append(frameNumber)
                                    skimData["players"][player["name"]]["framestamps"]["in_bounds"].append([frameNumber,False])



                                PlayerPosCache[player["name"]] = currentPosition
            except:
                pass

            frameNumber += 1
        #Convert Player Dict into list
        PlayerDict = skimData["players"]
        PlayerList = []
        for value in skimData["players"].values():
            ## CACULATE CRASHES

            endingFrames = skimData["frames"] - (45 * skimData["framerate"])
            if value["startFrame"] + value["stats"]["total_frames"] < endingFrames:
                value["crashed"] = True

            PlayerList.append(value)
        skimData["players"] = PlayerList




        
        return skimData
    
    except Exception as e:
        return {"error":traceback.format_exc()}
    
