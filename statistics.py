#SKIMSPATH = "C:/Users/Admin/Desktop/Skims"
#SKIMSPATH = "Skims"

import os
import json
from re import M
from PIL import Image
from multiprocessing import Process , Queue, Pool
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import matplotlib
from datetime import datetime
from data.config import SKIMSFILEPATH
MapSettings = dict()
MapSettings["dyson"] = {
    "MapBounds":[-100,100,-40,40],
    "quality":[200*6,90*6]
    
    }

mapLoadLimit = 99999
NUMOFCORES = 4
def LoadMapIntoMemory(MapRequest):
    try:
        filepath = f"{SKIMSFILEPATH}/{MapRequest['map']}/{MapRequest['name']}"
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
        
        mapData["start_time"] = ReplayData["start_time"]

        return {"map":MapRequest['map'],"data":mapData}
    except:
        print(f"ERROR: {SKIMSFILEPATH}/{MapRequest['map']}/{MapRequest['name']}")


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
        mapfiles = os.listdir(f"{SKIMSFILEPATH}/{map}")
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

async def GameMapOverTime(data):
    fig, ax = plt.subplots(facecolor=(.1,.1,.1,0))
    ax.set_facecolor('#000')
    fig.patch.set_facecolor('black')
    #ax.set_ylim(800, 1200)
    ax.set_title("Maps over time",color= "white")
    ax.tick_params(axis='y', colors='white')
    ax.spines['left'].set_color('white')        # setting up Y-axis tick color to red
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')        # setting up Y-axis tick color to red
    ax.spines['bottom'].set_color('white')
    #ax.xaxis.set_major_locator(MultipleLocator(5))
    #ax.xaxis.set_major_formatter('{x:.0f}')
    #ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.tick_params(which='minor', length=4, color='w')
    ax.tick_params(which='major', length=7, color='w')
    
    maps = ["combustion","dyson","fission","surge"]
    times = dict()
    cumulative = dict()
    for map in maps:
        times[map] = list()
        cumulative[map] = list()
        maptimes = list()
        for game in data[map]:
            mapTime = game["start_time"].replace(":","-")
            maptimes.append(mapTime)
        maptimes.sort()
        times[map] = maptimes
        for i in range(len(data[map])):
            cumulative[map].append(i+1)
        
    
    for key,value in times.items():
        times[key] = [datetime.strptime(time, '%Y-%m-%d %H-%M-%S') for time in value]
            
        
        
    ax.plot(times["combustion"], cumulative["combustion"],color= "red",label = "combustion")
    ax.plot(times["dyson"], cumulative["dyson"],color= "green",label = "dyson")
    ax.plot(times["fission"], cumulative["fission"],color= "blue",label = "fission")
    ax.plot(times["surge"], cumulative["surge"],color= "yellow",label = "surge")

    ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=None, interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    #ax.plot(x, y, 'o--', color='grey', alpha=0.3)
    plt.legend(title='Maps:')

    ax.grid(axis='x', color='0.05')
    #ax.legend(title='Elo History')
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center",color = "white")
    plt.savefig('stats.png')