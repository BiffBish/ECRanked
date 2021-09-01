
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
