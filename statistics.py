#SKIMSPATH = "C:/Users/Admin/Desktop/Skims"
#SKIMSPATH = "Skims"

colors = [(222,146,89),(58,203,214),(233,108,168),(140,251,136)]
colorsNormalized = [(222/255,146/255,89/255),(58/255,203/255,214/255),(233/255,108/255,168/255),(140/255,251/255,136/255)]
if __name__ == '__main__':
    import asyncio
    import statistics
    print("Started")
    data = asyncio.run(statistics.LoadMapsIntoMemory(None))
    asyncio.run(statistics.GameMapOverTime(data))

import os
import json
from re import M
from PIL import Image
from multiprocessing import Process , Queue, Pool
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import date2num


import matplotlib
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

from datetime import datetime , date ,timedelta
from data.config import SKIMSFILEPATH
from PIL import Image
import sys


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
    if logChannel:
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
    
    for key,value in data.items():
        print(f"{key} : {len(value)}")



    if logChannel:
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
    startDatetime = datetime(2021,8,7)
    startDatetime = date.today()

    startDate = date(2021,8,14) 
    endDate = date.today() + timedelta(days=1)
    #endDate = date.today()
    
    fig = plt.figure(constrained_layout=True)
    gs = GridSpec(5, 5, figure=fig)

        #fig, ax = plt.subplots(facecolor=(.1,.1,.1,0))

    
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
    ax1 = fig.add_subplot(gs[0:-1, 0:-1])
    #ax1.tick_params(axis='y', colors='#ff00ff')
    #ax1.tick_params(axis='x', colors='#ff00ff')

    #ax1.spines['left'].set_color('#ff00ff')        # setting up Y-axis tick color to red
    #ax1.spines['top'].set_color('#ff00ff')
    #ax1.spines['right'].set_color('#ff00ff')        # setting up Y-axis tick color to red
    #ax1.spines['bottom'].set_color('#ff00ff')
    #ax.xaxis.set_major_locator(MultipleLocator(5))
    #ax.xaxis.set_major_formatter('{x:.0f}')
    #ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax1.tick_params(which='minor', length=4)
    ax1.tick_params(which='major', length=7)     
        
    ax1.plot(times["combustion"], cumulative["combustion"],color= "#F00",label = "combustion")
    ax1.plot(times["dyson"], cumulative["dyson"],color= "#0F0",label = "dyson")
    ax1.plot(times["fission"], cumulative["fission"],color= "#FF0",label = "fission")
    ax1.plot(times["surge"], cumulative["surge"],color= "#00F",label = "surge")
    ax1.legend(facecolor = "w")
    ax1.xaxis.set_major_locator(mdates.DayLocator(bymonthday=None, interval=2))
    ax1.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=None, interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax1.set_xlim(startDate,endDate)
    ax1.grid(which='both', axis='x',color='gray', linestyle='-', linewidth=.5)
    #ax1.figure.set_size_inches(8, 6)

    ax2 = fig.add_subplot(gs[-1, 0:-1])

    #ax2.tick_params(axis='y', colors='#ff00ff')
    #ax2.tick_params(axis='x', colors='#ff00ff')

    #ax2.spines['left'].set_color('#ff00ff')        # setting up Y-axis tick color to red
    #ax2.spines['top'].set_color('#ff00ff')
    #ax2.spines['right'].set_color('#ff00ff')        # setting up Y-axis tick color to red
    #ax2.spines['bottom'].set_color('#ff00ff')


    
    one_day = timedelta(days = 1)  

    week = [] 
    for i in range((endDate-startDate).days+1):  
        week.append(startDate + (i)*one_day)

    numweek = date2num(week)

    combinedTimes = [times["combustion"],times["dyson"],times["fission"],times["surge"]]
    ax2.hist([times["combustion"],times["dyson"],times["fission"],times["surge"]], numweek, stacked=True,ec="w",color = ['#f00','#0f0','#ff0','#00f'])
    # ax2.hist([times["combustion"],times["dyson"],times["fission"],times["surge"]], numweek, stacked=True, density=True,ec="k")
    ax2.set_xlim(startDate,endDate)
    ax2.xaxis.set_major_locator(mdates.DayLocator(bymonthday=None, interval=2))
    ax2.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=None, interval=1))
    ax2.yaxis.set_minor_locator(MultipleLocator(10))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    #plt.show()


    #plt.setp(ax1.get_xticklabels(), rotation=30, ha="right")
    ##ax.plot(x, y, 'o--', color='grey', alpha=0.3)
    #plt.legend(title='Maps:')

    #ax1.grid(axis='x', color='0.05')
    ##ax.legend(title='Elo History')
    #plt.setp(ax1.get_xticklabels(), rotation=0, ha="center",color = "#00ff00")
    
    ax3 = fig.add_subplot(gs[0:-1, -1])

    # ax3.tick_params(axis='y', colors='#ff00ff')
    # ax3.tick_params(axis='x', colors='#ff00ff')

    # ax3.spines['left'].set_color('#ff00ff')        # setting up Y-axis tick color to red
    # ax3.spines['top'].set_color('#ff00ff')
    # ax3.spines['right'].set_color('#ff00ff')        # setting up Y-axis tick color to red
    # ax3.spines['bottom'].set_color('#ff00ff')



    totalTimes = [len(x) for x in combinedTimes]
    labels = ['Co', 'Dy', 'Fi', 'Su']
    print(totalTimes)
    ax3.bar(labels,totalTimes, .95,color = ['#f00','#0f0','#ff0','#00f'])

    #plt.rc('label', fontsize=5) 
    ax4 = fig.add_subplot(gs[-1, -1])

    #labels = ['Co', 'Dy', 'Fi', 'Su']

    patches, texts, autotexts = ax4.pie(totalTimes, 
        colors = ['#f00','#0f0','#ff0','#00f'],
        autopct='%1.1f%%',startangle=90,
        wedgeprops={"edgecolor":"w",'linewidth': 1}
                        )
    for _ in autotexts:
        _.set_fontsize(6)
        _.set_color("#fff")
    
    ax4.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    # ax4.spines['left'].set_color('#ff00ff')        # setting up Y-axis tick color to red
    # ax4.spines['top'].set_color('#ff00ff')
    # ax4.spines['right'].set_color('#ff00ff')        # setting up Y-axis tick color to red
    # ax4.spines['bottom'].set_color('#ff00ff')
    #plt.show()



    fig.suptitle("Maps over time")

    plt.savefig('stats.png',dpi=300)

    
    print("converting image")
    img = Image.open('stats.png')
    img = img.convert("RGBA")

    pixdata = img.load()

    # Clean the background noise, if color != white, then set to black.

    #quit()
    #colors = [(214,39,39),(44,160,44),(255,127,14),(31,119,180)]
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            pix = pixdata[x,y]
            #If its at Grey White or black Convert to black
            if pix[0] == pix[1] == pix[2]:
                brightness = 255 - pix[0]
                pixdata[x, y] = (brightness, brightness, brightness, 255)

            #If the color is Yellow
            if pix[0] == pix[1] and pix[0] > pix[2]:
               brigtness = ((255-pix[2]) / 255)
               newcolor = tuple([round(c*brigtness) for c in colors[2]])
               pixdata[x,y] = newcolor
                #pixdata[x,y] = (0,255,255)

            #If the color is Red
            elif pix[1] == pix[2] and pix[0] > pix[2]:
               brigtness = ((255-pix[1]) / 255)
               newcolor = tuple([round(c*brigtness) for c in colors[0]])
               pixdata[x,y] = newcolor
                #pixdata[x,y] = (0,255,255)
            
             #If the color is Green
            elif pix[0] == pix[2] and pix[1] > pix[2]:
               brigtness = ((255-pix[0]) / 255)
               newcolor = tuple([round(c*brigtness) for c in colors[1]])
               pixdata[x,y] = newcolor
                #pixdata[x,y] = (0,255,255)

            #If the color is Blue
            elif pix[0] == pix[1] and pix[0] < pix[2]:
               brigtness = ((255-pix[0]) / 255)
               newcolor = tuple([round(c*brigtness) for c in colors[3]])
               pixdata[x,y] = newcolor
                #pixdata[x,y] = (0,255,255)

            elif pix[0] == pix[2] and pix[1] < pix[2]:
              brigtness = ((255-pix[1]) / 255)
              newcolor = tuple([round(255*brigtness) for i in range(3)])
              pixdata[x,y] = newcolor
              #pixdata[x,y] = (0,255,255)


            
            # elif pixdata[x,y][0] == pixdata[x,y][2] and pixdata[x,y][1] < pixdata[x,y][0] : 
            #     pixdata[x, y] = (255, 255, 255, 255)
    
    img.save('stats.png')
    print("finihsed")
    


#async def AverageSpeedOverTime()
