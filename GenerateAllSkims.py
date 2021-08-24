EXPORTPATH = "D:/ECRanked/Skims"
IMPORTPATH = "D:/ECRanked/Replays"

# EXPORTPATH = "Skims"
# IMPORTPATH = "Replays"
import time
import os
import json
from datetime import datetime
from multiprocessing import Process , Queue,Pool
import zipfile
def MakeSkim(inputdata):
    mapname = inputdata["map"]
    filename = inputdata["name"]

    replaydata = []
    skimData = dict()

    with zipfile.ZipFile(f"{IMPORTPATH}/{mapname}/{filename}","r") as zipObj:
        zipPath = zipObj.namelist()[0]
        ReplayFile = zipObj.extract(zipPath)
        with open(ReplayFile) as replayFile:
            replaydata = (replayFile.read()).split("\n")
    skimData["frames"] = len(replaydata)-1
    skimData["start_time"] = replaydata[0].split("\t")[0][:-4]
    skimData["map"] = mapname
    skimData["players"] = dict()
    
    for frame in replaydata:
        if frame != "":
            frameDataRaw  = frame.split("\t")[1]
            frameData = json.loads(frameDataRaw)
            for TeamID in range(3):
                team = frameData["teams"][TeamID]
                if "players" in team:
                    for player in team["players"]:
                        #Generate the new player data
                        if player["name"] not in skimData["players"]:
                            playerData = dict()
                            playerData["team"] = TeamID
                            playerData["playerid"] = player["playerid"]
                            playerData["name"] = player["name"]
                            playerData["userid"] = player["userid"]
                            playerData["number"] = player["number"]
                            playerData["level"] = player["level"]
                            playerData["stats"] = dict()
                            playerData["stats"]["totalFrames"] = 0
                            playerData["stats"]["totalSpeedPerFrame"] = 0
                            playerData["stats"]["upsideDownFrames"] = 0
                            playerData["stats"]["stoppedFrames"] = 0
                            skimData["players"][player["name"]] = playerData

                        playerPosition = player["head"]["position"]
                        playerHeadRotationUp = player["head"]["up"]
                        velocity = player["velocity"]
                        skimData["players"][player["name"]]["stats"]["totalFrames"] += 1
                        if playerHeadRotationUp[1] < 0:
                            skimData["players"][player["name"]]["stats"]["upsideDownFrames"] += 1
                        
                        speed = ((velocity[0]**2) + (velocity[1]**2) + (velocity[2]**2))**.5
                        skimData["players"][player["name"]]["stats"]["totalSpeedPerFrame"] += speed

                        if speed < 1:
                            skimData["players"][player["name"]]["stats"]["stoppedFrames"] += 1

                        

                        
                









    with open(f"{EXPORTPATH}/{mapname}/{'.'.join(filename.split('.')[:-1])}.ecrs","w") as skimFile:
        skimFile.write(json.dumps(skimData))
    return None



if __name__ == '__main__':
    maps = ["dyson","combustion","surge","fission"]
    TotalMapsToLoad = []
    for map in maps:
        mapfiles = os.listdir(f"{IMPORTPATH}/{map}")
        for filename in mapfiles:
            print(f"Processing : [{map}] {filename}")
            data = {"name":filename,"map":map}
            TotalMapsToLoad.append(data)
            MakeSkim(data)
    #with Pool(processes=4) as pool:
    #    print("Starting Worker")
    #    ReturnObj = pool.map(MakeSkim, TotalMapsToLoad)
    #    #print(f"Workers Done : {round(time.perf_counter()-tnow,3)}s total ({round((time.perf_counter()-tnow)/len(TotalMapsToLoad),3)}s/m)")

