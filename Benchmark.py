import time
import os
import json
from datetime import datetime
from multiprocessing import Process , Queue,Pool


if __name__ == '__main__':
    print("Running File processing Benchmark")

    tnow = time.perf_counter()
    data = dict()
    data["dyson"] = []
    data["combustion"] = []
    data["surge"] = []
    data["fission"] = []
    mapLoadLimit = 99999
    #maps = ["dyson"]
    maps = ["dyson","combustion","surge","fission"]
    MaploadNum = 0


    TotalMapsToLoad = []
    for map in maps:
        mapfiles = os.listdir(f"Skims/{map}")
        for filename in mapfiles:
            TotalMapsToLoad.append({"name":filename,"map":map})

    print(TotalMapsToLoad)

    exitFlag = 0

    print("List Created")



        # start 4 worker processes
    with Pool(processes=4) as pool:
        ReturnObj = pool.map(LoadMapIntoMemory, TotalMapsToLoad)
        print(f"Workers Done : {round(time.perf_counter()-tnow,3)}s total ({round((time.perf_counter()-tnow)/len(TotalMapsToLoad),3)}s/m)")

        for Obj in ReturnObj:
            data[Obj["map"]].append(Obj["data"])
        print(f"Data loaded : {time.perf_counter()-tnow}")


    time.sleep(20)

    quit()

    # Get lock to synchronize threads


# #threadList = ["Thread-1"]
# processList = ["Process-1", "Process-2", "Process-3", "Process-4"]

# quit()










# for map in maps:



#     t = time.perf_counter()
#     mapfiles = os.listdir(f"Skims/{map}")
#     i = 0
#     NumOfMaps = len(mapfiles)

#     for filename in mapfiles:
#         i += 1
#         if MaploadNum >= mapLoadLimit:
#             break
#         MaploadNum += 1
#         filepath = f"Skims/{map}/{filename}"
#         #print(f"({i}/{len(mapfiles)})")

#         with open(filepath,"rb") as f:
#             ReplayData = json.load(f)
        
#         PlayerNameRef = dict()
#         for userID, playerdata in ReplayData["players"].items():
#             PlayerNameRef[str(playerdata["playerID"])] = playerdata["name"]
        
#         mapData = dict()
#         for id,playerData in ReplayData["Data"].items():
#             mapData[PlayerNameRef[str(id)]] = playerData

#         data[map].append(mapData)
#     print(f"Processing maps [{map}] ({NumOfMaps}) ({round((time.perf_counter() - t)/NumOfMaps,4)}s)")



# for i in range(2):
#     xPos = []
#     yPos = []
#     for mapname in maps:
#         t = time.perf_counter()
#         for map in data[mapname]:
#             for playername,playerdata in map.items():
#                 for frame in playerdata:
#                     xPos.append(frame[0])
#                     yPos.append(frame[2])
#         print(f"Processing maps [{mapname}] ({len(data[mapname])}) ({round((time.perf_counter() - t)/(len(data[mapname])),4)}s)")

        

# print("finished")

                    










    

