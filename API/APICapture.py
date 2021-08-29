import requests
import time
from datetime import datetime , timedelta
import json
import bz2
import pickle
import win32ui
import os
framerate = 60

import traceback


import zipfile
import psutil
import subprocess 

SkimFilePath = "E:/ECRanked/Skims"
ReplayFilePath = "E:/ECRanked/Replays"

def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())


CrashGameID = ""
def HandleGame():
    
    r = requests.get('http://127.0.0.1:6721/session')
    startingTime = time.time() 
    t=time.time()
    CurrentGame = dict()
    FrameCount = 0
    ActivePlayerList = dict()
    jsonData = r.json()
    #Game just starting up
    print("GAME STARTED")
    print(f"SESSION ID = \"{jsonData['sessionid']}\"")
    StartTimeSTR = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    mapSaveLocation = ""
    CrashGameID = ""     
    jsonData = dict()  

    with open("currentgame.echoreplay","a") as currentGametxt:
        while True:
            try:
                r = requests.get('http://127.0.0.1:6721/session')
                if r.status_code == 404:
                    print(f"Game Finish! {jsonData['sessionid']}")     

                    CrashGameID == ""

                    if jsonData['map_name'] == "mpl_combat_dyson" : mapSaveLocation = "dyson" 
                    if jsonData['map_name'] == "mpl_combat_combustion" : mapSaveLocation = "combustion" 
                    if jsonData['map_name'] == "mpl_combat_fission" : mapSaveLocation = "fission" 
                    if jsonData['map_name'] == "mpl_combat_gauss" : mapSaveLocation = "surge" 
                  
                    break
                jsonData = r.json()


                    

                jsonData = r.json()
                if CrashGameID != "" and CrashGameID != jsonData["sessionid"]:
                    print(f"Game Crash Finish! {jsonData['sessionid']}")     

                    CrashGameID == ""

                    if jsonData['map_name'] == "mpl_combat_dyson" : mapSaveLocation = "dyson" 
                    if jsonData['map_name'] == "mpl_combat_combustion" : mapSaveLocation = "combustion" 
                    if jsonData['map_name'] == "mpl_combat_fission" : mapSaveLocation = "fission" 
                    if jsonData['map_name'] == "mpl_combat_gauss" : mapSaveLocation = "surge" 
                
                    break

                #During entire game
                FrameCount += 1
                t += 1/framerate

                time.sleep(max(0,t-time.time()))  
                
                Nowtime = datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
                currentGametxt.write(f"{Nowtime}\t{r.text}\n")
                print(f"Capturing Frame! [{FrameCount}] ({Nowtime})")
            except Exception as e: 
                traceback.print_exc()
                print("Game Crash!")
                CrashGameID = jsonData["sessionid"]
                print("Waiting 5s")
                time.sleep(5)
                if not process_exists("echovr.exe"):
                    print("Echo VR Restarting!")
                    subprocess.Popen(['run.bat'])
                    print("Waiting 30s")
                    time.sleep(45)
                else:
                    for proc in psutil.process_iter():
                        # check whether the process name matches
                        if proc.name() == "echovr.exe":
                            proc.kill()
                        if proc.name() == "BsSndRpt64.exe":
                            proc.kill()
                print("Waiting 10s")
                time.sleep(10)
                print("Done!")   


    zipObj = zipfile.ZipFile(f"{ReplayFilePath}/{mapSaveLocation}/[{StartTimeSTR}] {jsonData['sessionid']}.echoreplay", 'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)

    # Add multiple files to the zip
    zipObj.write('currentgame.echoreplay')
    zipObj.close()
    os.remove("currentgame.echoreplay")  




    
def saveStrippedVersion(CurrentGame,ActivePlayerList):
    PositionData = dict()
    
    PositionData["sessionid"] = CurrentGame["sessionid"]
    PositionData["map_name"] = CurrentGame["map_name"]
    PositionData["framerate"] = CurrentGame["framerate"]
    PositionData["start_time"] = CurrentGame["start_time"]
    PositionData["players"] = CurrentGame["players"]


    PlayerPosData = dict()



    #Loop Through all the frames
    for frameData in CurrentGame["data"]:
        teamData = frameData["teams"]
        for team in teamData:
            for player in team:
                playerID = str(player["id"])
                if playerID not in PlayerPosData:
                    PlayerPosData[playerID] = list()
                
                PlayerPosData[playerID].append(player["h"][0])


    PositionData["Data"] = PlayerPosData



    CurrentGame["players"] = ActivePlayerList
    if CurrentGame['map_name'] == "mpl_combat_dyson" : mapSaveLocation = "dyson" 
    if CurrentGame['map_name'] == "mpl_combat_combustion" : mapSaveLocation = "combustion" 
    if CurrentGame['map_name'] == "mpl_combat_fission" : mapSaveLocation = "fission" 
    if CurrentGame['map_name'] == "mpl_combat_gauss" : mapSaveLocation = "surge" 
    print("saving position replay")
    with open(f"{SkimFilePath}/{mapSaveLocation}/[{CurrentGame['start_time']}] {CurrentGame['sessionid']}.ecrs", 'w') as f:
        f.write(json.dumps(PositionData))


while True:
    try:
        r = requests.get('http://127.0.0.1:6721/session')
        if r.status_code == 200:
            HandleGame()
        else:
            time.sleep(10)
    except:
        if not process_exists("echovr.exe"):
            subprocess.Popen(['run.bat'])
        time.sleep(20)     