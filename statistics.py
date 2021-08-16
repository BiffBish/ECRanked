#SKIMSPATH = "C:/Users/Admin/Desktop/Skims"
SKIMSPATH = "Skims"


import os
import json
from PIL import Image
data = dict()
data["dyson"] = []
data["combustion"] = []
data["surge"] = []
data["fission"] = []
mapLoadLimit = 99999

async def LoadMapsIntoMemory(logChannel):
    await logChannel.send("Loading maps into memory.....")
    #maps = ["dyson"]
    maps = ["dyson","combustion","surge","fission"]
    MaploadNum = 0
    for map in maps:

        print(f"Loading map: {map}")
        mapfiles = os.listdir(f"{SKIMSPATH}/{map}")
        i = 0
        await logChannel.send(f"Loading maps from {map}..... {len(mapfiles)} total files")

        for filename in mapfiles:
            i += 1
            if MaploadNum >= mapLoadLimit:
                break
            MaploadNum += 1
            filepath = f"{SKIMSPATH}/{map}/{filename}"
            print(f"({i}/{len(mapfiles)})")

            with open(filepath,"rb") as f:
                ReplayData = json.load(f)
            
            PlayerNameRef = dict()
            for userID, playerdata in ReplayData["players"].items():
                PlayerNameRef[str(playerdata["playerID"])] = playerdata["name"]
            
            mapData = dict()
            for id,playerData in ReplayData["Data"].items():
                mapData[PlayerNameRef[str(id)]] = playerData

            data[map].append(mapData)
    await logChannel.send("Finished loading maps")



async def GetPositionHeatMap(map):
    
    pass
