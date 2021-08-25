import matplotlib.pyplot as plt
import zipfile
import json
import os
IMPORTPATH = "ConvertedReplays"



fig, ax = plt.subplots()

Filelimit = 5
GameNumber = 0
folderPath = "C:/Users/kaleb/DiscordBots/ECRanked/ConvertedReplays/dyson"
for file in os.listdir(folderPath):
    
    if Filelimit == GameNumber:
        break
    GameNumber += 1
    FilePath = f"{folderPath}/{file}"

    replaydata = []
    with zipfile.ZipFile(FilePath,"r") as zipObj:
        zipPath = zipObj.namelist()[0]
        ReplayFile = zipObj.extract(zipPath)
        with open(ReplayFile) as replayFile:
            replaydata = (replayFile.read()).split("\n")

    PlayerDatas = dict()
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
                        if str(GameNumber)+player["name"] not in PlayerDatas:
                            playerData = []
                            print(frameNumber)
                            for i in range(frameNumber):
                                playerData.append(0)
                            PlayerDatas[str(GameNumber)+player["name"]] = playerData
                        PlayerDatas[str(GameNumber)+player["name"]].append(player["ping"])
        #print(PlayerDatas)
        frameNumber += 1
    for key,value in PlayerDatas.items():
        
        ax.plot(value,label = key)
plt.legend()
plt.show()
#print(PlayerDatas)



                        
                







