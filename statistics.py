#SKIMSPATH = "C:/Users/Admin/Desktop/Skims"
SKIMSPATH = "Skims"
import os
import json
from re import M
from PIL import Image
from multiprocessing import Process , Queue,Pool



MapSettings = dict()
MapSettings["dyson"] = {
    "MapBounds":[-100,100,-40,40],
    "quality":[200*6,90*6]
    
    }

mapLoadLimit = 99999
NUMOFCORES = 4
def LoadMapIntoMemory(MapRequest):
    try:
        filepath = f"Skims/{MapRequest['map']}/{MapRequest['name']}"
        print(filepath)
        #print(f"({i}/{len(mapfiles)})")

        with open(filepath,"rb") as f:
            ReplayData = json.load(f)
        
        PlayerNameRef = dict()
        for userID, playerdata in ReplayData["players"].items():
            PlayerNameRef[str(playerdata["playerID"])] = playerdata["name"]
        
        mapData = dict()
        for id,playerData in ReplayData["Data"].items():
            mapData[PlayerNameRef[str(id)]] = playerData

        return {"map":MapRequest['map'],"data":mapData}
    except:
        print(f"ERROR: Skims/{MapRequest['map']}/{MapRequest['name']}")


async def LoadMapsIntoMemory(logChannel):
  
    await logChannel.send("Loading maps into memory.....")


    print("Running File processing Benchmark")

    data = dict()
    data["dyson"] = []
    data["combustion"] = []
    data["surge"] = []
    data["fission"] = []
    maps = ["dyson","combustion","surge","fission"]
    MaploadNum = 0

    TotalMapsToLoad = []
    for map in maps:
        mapfiles = os.listdir(f"Skims/{map}")
        for filename in mapfiles:
            TotalMapsToLoad.append({"name":filename,"map":map})


        # start 4 worker processes
    with Pool(processes=NUMOFCORES) as pool:
        ReturnObj = pool.map(LoadMapIntoMemory, TotalMapsToLoad)
        for Obj in ReturnObj:
            if Obj is not None:
                data[Obj["map"]].append(Obj["data"])

    await logChannel.send("Finished loading maps")
    return data




def ProcessPositionHeatMap(PositionList):
    xlist = []
    ylist = []
    for position in PositionList:
        xlist.append(position[0])
        ylist.append(position[2])
    
    return xlist,ylist

async def GetPositionHeatMap(data,map,user = None):
    MapsToGet = []
    for game in data[map]:
            if user in game:
                MapsToGet.append(game[user])

    xPositionList = []
    yPositionList = []
    print("ProcessingPositionList")
    with Pool(processes=NUMOFCORES) as pool:
        ReturnObj = pool.map(ProcessPositionHeatMap, MapsToGet)
        for Obj in ReturnObj:
            if Obj is not None:
                #print(Obj[0])
                xPositionList.extend(Obj[0])
                yPositionList.extend(Obj[1])
    print("PositionListProcessed")


    WindowWidth = MapSettings[map]["MapBounds"][1] - MapSettings[map]["MapBounds"][0]
    WindowHeight = MapSettings[map]["MapBounds"][3] - MapSettings[map]["MapBounds"][2]



    #Make the empty dataset
    HeatMap = []
    for x in range((WindowWidth)*MapSettings[map]["Resolution"][0]):
        HeatMap.append([])
        for y in range((WindowHeight)*MapSettings[map]["Resolution"][1]):
            HeatMap[x].append(0)
    
    for xval,yval in zip(xPositionList,yPositionList):
        xmid = MapSettings[map]["MapBounds"][1]-MapSettings[map]["MapBounds"][0]
        ymid = MapSettings[map]["MapBounds"][1]-MapSettings[map]["MapBounds"][0]
        x = round((xval- MapSettings[map]["MapBounds"][0])*MapSettings[map]["Resolution"][0])-1
        y = round((yval- MapSettings[map]["MapBounds"][2])*MapSettings[map]["Resolution"][1])-1
    #print(x,y)
        HeatMap[x][y] += 1



    print("HeatMapMade")

    pass
