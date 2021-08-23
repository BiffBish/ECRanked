
import os
import pickle
import bz2

REPLAYDIRECTORY = "D:/ECRanked/Replays"
   

def ProcessSpeedOverTime(data,f):
    
    velocitys = dict()
    frames = data["data"]
    for frame in frames:
        for i in range(2):
            team = frame["teams"][i]
            for player in team:
                
                if str(player["id"]) not in velocitys:
                    velocitys[str(player["id"])] = list()
                velocity = player["v"]

                speed = ((velocity[0]**2) + (velocity[1]**2) + (velocity[2]**2))**.5
                if speed < 1:
                    speed = 1
                else:speed = 0
                velocitys[str(player["id"])].append(speed)

    nameRef = dict()
    for userid,player in data["players"].items():
        nameRef[str(player["playerID"])] = str(player["name"])
    
    for id,velocitylist in velocitys.items():
        f.write(f"ST\t{nameRef[id]}\t{sum(velocitylist)}\t{len(velocitylist)}\n")
    


def DecompressFile(FilePath,OutputFile):
    print(f"DECOMPRESSING FILE {FilePath}")
    ReplayData = dict()
    with bz2.open(FilePath) as f:
        ReplayData = pickle.load(f)
    # with open(OutputFile,"w") as f:
    #     JsonData = json.dumps(ReplayData)
    #     f.write(JsonData)
    return ReplayData


with open("stats.txt","a") as outputfile:

    for map in os.listdir(REPLAYDIRECTORY):
        mapPath = f"{REPLAYDIRECTORY}/{map}"
        outputfile.write(f"MAP {map}\n")
        for file in os.listdir(mapPath):
            try:
                filePath = f"{REPLAYDIRECTORY}/{map}/{file}"
                data = DecompressFile(filePath,"decompressed.json")
                #with open("Skims\dyson\[2021-08-14 22-35-00] BB0322DE-BD11-42BD-8510-E429DAB99247.ecrs") as f:
                #    data = json.load(f)
                #    print(data.keys())
                ProcessSpeedOverTime(data,outputfile)
            except:
                print("ERROR : {filePath}")
#data = asyncio.run(statistics.LoadMapsIntoMemory(None))
#asyncio.run(statistics.GameMapOverTime(data))

#async def AverageSpeedOverTime()
