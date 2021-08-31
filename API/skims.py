import json
import traceback
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
        skimData["start_time"] = replaydata[0].split("\t")[0][:-4]
        rawMapName = json.loads(replaydata[0].split("\t")[1])["map_name"]
        if rawMapName == "mpl_combat_combustion" :  skimData["map"] = "combustion"
        if rawMapName == "mpl_combat_dyson" :  skimData["map"] = "dyson"
        if rawMapName == "mpl_combat_fission" :  skimData["map"] = "fission"
        if rawMapName == "mpl_combat_surge" :  skimData["map"] = "surge"
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
                                playerData["stats"]["total_upsidedown"] = 0
                                playerData["stats"]["total_stopped"] = 0
                                playerData["stats"]["total_deaths"] = 0
                                skimData["players"][player["name"]] = playerData

                            playerPosition = player["head"]["position"]
                            playerHeadRotationUp = player["head"]["up"]
                            velocity = player["velocity"]
                            skimData["players"][player["name"]]["stats"]["total_frames"] += 1
                            if playerHeadRotationUp[1] < 0:
                                skimData["players"][player["name"]]["stats"]["total_upsidedown"] += 1
                            
                            speed = ((velocity[0]**2) + (velocity[1]**2) + (velocity[2]**2))**.5
                            skimData["players"][player["name"]]["stats"]["total_speed"] += speed

                            if speed < 1:
                                skimData["players"][player["name"]]["stats"]["total_stopped"] += 1
                            
                            skimData["players"][player["name"]]["stats"]["total_ping"] += player["ping"]

                            currentPosition = player["head"]["position"]
                            oldPosition = PlayerPosCache[player["name"]]
                            if not InBoundingBox(currentPosition,MapSettings[skimData["map"]]["MapBounds"]) and InBoundingBox(oldPosition,MapSettings[skimData["map"]]["MapBounds"]):
                                skimData["players"][player["name"]]["stats"]["total_deaths"] += 1
                            PlayerPosCache[player["name"]] = currentPosition


            frameNumber += 1
        return skimData
    
    except:
        traceback.print_exc()
        return {"error":"there was an error"}
    
