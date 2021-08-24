import bz2
import pickle
import os
import json
import sys
from types import MappingProxyType
from datetime import datetime, timedelta
import zipfile

from multiprocessing import Process , Queue,Pool




def createPlayerInfo(PlayerData,FramePlayerData):
    player = dict()

    player["rhand"] = {
        "pos":FramePlayerData["r"][0],
        "forward":FramePlayerData["r"][1],
        "left":FramePlayerData["r"][2],
        "up":FramePlayerData["r"][3],
    }

    player["playerid"] = PlayerData["playerid"]
    player["name"] = PlayerData["name"]
    player["userid"] = PlayerData["userid"]
    player["number"] = PlayerData["number"]
    player["level"] = PlayerData["level"]
    player["ping"] = FramePlayerData["p"]
    player["packetlossratio"] = PlayerData["packetlossratio"]
    

    player["head"] = {
        "position":FramePlayerData["h"][0],
        "forward":FramePlayerData["h"][1],
        "left":FramePlayerData["h"][2],
        "up":FramePlayerData["h"][3],
    }
    player["body"] = {
        "position":FramePlayerData["b"][0],
        "forward":FramePlayerData["b"][1],
        "left":FramePlayerData["b"][2],
        "up":FramePlayerData["b"][3],
    }
    player["lhand"] = {
        "pos":FramePlayerData["l"][0],
        "forward":FramePlayerData["l"][1],
        "left":FramePlayerData["l"][2],
        "up":FramePlayerData["l"][3],
    }
    player["velocity"] = FramePlayerData["v"]

        
    return player

REPLAYDIRECTORY = "D:/ECRanked/Replays"
EXPORTDIRECTORY = "D:/ECRanked/ConvertedReplays"
# REPLAYDIRECTORY = "Replays"
# EXPORTDIRECTORY = "ConvertedReplays"

def HandleMap(inputData):
    try:
        map = inputData["map"]
        match = inputData["match"]
        #print(f"Saving replay to path : {ExportPath}")

        matchPath = f"{REPLAYDIRECTORY}/{map}/{match}"
        ExportPath = f"{EXPORTDIRECTORY}/{map}/{'.'.join(match.split('.')[:-1]) }.echoreplay"
        TempExport = f"{match}.echoreplay"
        print(matchPath)
        with bz2.open(matchPath) as f:
            data = pickle.load(f)
        
        Data = ""
        with open(TempExport,"a") as export:
            start_time = datetime.strptime(data["start_time"],"%Y-%m-%d %H-%M-%S")

            timeBetweenFrame = (1/int(data["framerate"])*1000)

            
            playerDatas = data["players"]
            PlayerIDToData = dict()
            for key,player in playerDatas.items():
                temp = dict()
                temp["name"] = player["name"]
                temp["userid"] = int(key)
                temp["playerid"] = player["playerID"]
                temp["level"] = player["level"]
                temp["number"] = player["number"]
                
                if "ping" in player:
                    temp["ping"] = player["ping"]
                else:
                    temp["ping"] = 0
                temp["packetlossratio"] = 0.0
                PlayerIDToData[str(player["playerID"])] = temp


            framecount = 0 
            for frame in data["data"]:
                FixedAPIRequest = dict()
                FixedAPIRequest["sessionid"] = data["sessionid"]
                FixedAPIRequest["sessionip"] = "0.0.0.0"
                FixedAPIRequest["match_type"] = "Echo_Combat"
                if map == "combustion": MapName = "mpl_combat_combustion"
                if map == "dyson": MapName = "mpl_combat_dyson"
                if map == "fission": MapName = "mpl_combat_fission"
                if map == "surge": MapName = "mpl_combat_gauss"

                FixedAPIRequest["map_name"] = MapName
                
                FixedAPIRequest["teams"] = []
                blueTeam = dict()
                blueTeam["team"] = "BLUE TEAM"
                blueTeam["players"] = list()    
                if len(frame["teams"][0])>0 : blueTeam["players"].append(createPlayerInfo(PlayerIDToData["0"],frame["teams"][0][0]))    
                if len(frame["teams"][0])>1 : blueTeam["players"].append(createPlayerInfo(PlayerIDToData["1"],frame["teams"][0][1]))    
                if len(frame["teams"][0])>2 : blueTeam["players"].append(createPlayerInfo(PlayerIDToData["2"],frame["teams"][0][2]))    
                if len(frame["teams"][0])>3 : blueTeam["players"].append(createPlayerInfo(PlayerIDToData["3"],frame["teams"][0][3]))  
                FixedAPIRequest["teams"].append(blueTeam)

                orangeTeam = dict()
                orangeTeam["team"] = "ORANGE TEAM"
                orangeTeam["players"] = list()
                if len(frame["teams"][1])>0 : orangeTeam["players"].append(createPlayerInfo(PlayerIDToData["4"],frame["teams"][1][0]))    
                if len(frame["teams"][1])>1 : orangeTeam["players"].append(createPlayerInfo(PlayerIDToData["5"],frame["teams"][1][1]))    
                if len(frame["teams"][1])>2 : orangeTeam["players"].append(createPlayerInfo(PlayerIDToData["7"],frame["teams"][1][2]))  
                if len(frame["teams"][1])>3 : orangeTeam["players"].append(createPlayerInfo(PlayerIDToData["6"],frame["teams"][1][3]))    
                FixedAPIRequest["teams"].append(orangeTeam)

                FixedAPIRequest["teams"].append({"team":"SPECTATOR TEAM"})
                
                
                
                FixedAPIRequest["player"] = {
                    "vr_left":[0,0,0],
                    "vr_position":[0,0,0],
                    "vr_forward":[0,0,0],
                    "vr_up":[0,0,0],
                    }
                
                FixedAPIRequest["private_match"] =  False
                FixedAPIRequest["tournament_match"] =  False
                
                FixedAPIRequest["pause"] = dict()
                FixedAPIRequest["pause"]["paused_state"] =  "none"
                FixedAPIRequest["pause"]["unpaused_team"] =  "none"
                FixedAPIRequest["pause"]["paused_requested_team"] =  "none"
                FixedAPIRequest["pause"]["unpaused_timer"] =  0.0
                FixedAPIRequest["pause"]["paused_timer"] =  0.0
                
                FixedAPIRequest["client_name"] = "ECRanked"

                
            

                #print(FixedAPIRequest)

                timeStr = datetime.strftime(start_time + timedelta(milliseconds=(framecount*timeBetweenFrame)),"%Y/%m/%d %H:%M:%S.%f")[:-3]
                APIStr = timeStr + "\t" + json.dumps(FixedAPIRequest) + "\n"
                
                framecount += 1
                export.write(APIStr)
    
        print(f"Saving replay to path : {ExportPath}")
        zipObj = zipfile.ZipFile(ExportPath, 'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)

        # Add multiple files to the zip
        zipObj.write(TempExport)
        zipObj.close()
        os.remove(TempExport)
    except:
        print(f"ERROR: {REPLAYDIRECTORY}/{map}/{match}")

if __name__ == "__main__":
    Tasks = []
    for map in os.listdir(REPLAYDIRECTORY):
        mapPath = f"{REPLAYDIRECTORY}/{map}"
        for match in os.listdir(mapPath):
            Tasks.append({"map":map,"match":match})

    print(Tasks)
    with Pool(processes=4) as pool:
        ReturnObj = pool.map(HandleMap, Tasks)
            

