import time
from datetime import datetime , timedelta
import json
import os
framerate = 90

import traceback

import zipfile
import subprocess 
from skims import CaculateSkims

import glob
import os
import requests

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
    SessionID = jsonData['sessionid']
    #Game just starting up
    print("GAME STARTED")
    print(f"SESSION ID = \"{SessionID}\"")
    StartTimeSTR = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    mapSaveLocation = ""
    if jsonData['map_name'] == "mpl_combat_dyson" : mapSaveLocation = "dyson" 
    if jsonData['map_name'] == "mpl_combat_combustion" : mapSaveLocation = "combustion" 
    if jsonData['map_name'] == "mpl_combat_fission" : mapSaveLocation = "fission" 
    if jsonData['map_name'] == "mpl_combat_gauss" : mapSaveLocation = "surge" 


    with open(f"{SessionID}.echoreplay","a+") as currentGametxt:
        CrashGameID = ""     
        r = None
        while True:
            try:
                r = requests.get('http://127.0.0.1:6721/session')

                if r.status_code == 404:
                    print(f"Game Finish! {jsonData['sessionid']}")    
                    break

                if CrashGameID != "":
                    jsonData = r.json()
                    if CrashGameID != jsonData["sessionid"]:
                        print(f"Game Crash Finish! {jsonData['sessionid']}")    
                        break
                    else:
                        currentGametxt.write("\n")
                        CrashGameID = ""
                print(f"80:  {(datetime.now() - nowTime).total_seconds()}")
                nowTime = datetime.now()
                #During entire game
                FrameCount += 1
                t += 1/framerate

                time.sleep(max(0,t-time.time()))  
            
                nowTime = datetime.now()
                currentGametxt.write(f"{nowTime}\t{r.text}\n")
                print(f"Capturing Frame! [{FrameCount}] ({nowTime})")
            except Exception as e: 
                jsonData = r.json()
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
                    subprocessList = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
                    output, error = subprocessList.communicate()
                    print(output)
                    target_process = "echovr.exe"
                    for line in output.splitlines():
                        if target_process in str(line):
                            pid = int(line.split(None, 1)[0])
                            os.kill(pid, 9)
                    target_process = "BsSndRpt64.exe"
                    for line in output.splitlines():
                        if target_process in str(line):
                            pid = int(line.split(None, 1)[0])
                            os.kill(pid, 9)
                print("Waiting 10s")
                time.sleep(10)
                print("Done!")   

    echoReplayPath = f"{ReplayFilePath}/{mapSaveLocation}/[{StartTimeSTR}] {SessionID}.echoreplay"
    zipObj = zipfile.ZipFile(echoReplayPath, 'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)

    # Add multiple files to the zip
    zipObj.write(f"{SessionID}.echoreplay")
    zipObj.close()
    SkimData = CaculateSkims(open(f"{SessionID}.echoreplay","r").read().split("\n"))
    with open(f"{SkimFilePath}/{mapSaveLocation}/[{StartTimeSTR}] {SessionID}.ecrs", 'w') as f:
        f.write(json.dumps(SkimData))

    SkimData["replay_link"] = echoReplayPath
    Formdata = {
            "key": "1a508f8b-1dd2-412c-aa4e-0eda0c4aa6fc",
            "data" : json.dumps(SkimData),
            "link" : echoReplayPath
            }
    print(requests.post(f"http://localhost/save_skim.py",data=Formdata))
    os.remove(f"{SessionID}.echoreplay")  

    webHookUrl = "https://discord.com/api/webhooks/882380147645354055/MzYHqnqatGkoidWApt0jlN5CO7FCKyK-kaDB8epctzKGw-tKRJgNovqpWv9cWdmskspb"
    playerIDs = list()
    for playerName , playerData in SkimData["players"].items():
        playerIDs.append(str(playerData["userid"]))

    data = {"content":",".join(playerIDs)}
    requests.post(webHookUrl,data= data)
 

TimerToRestart = 60
while True:
    try:
        r = requests.get('http://127.0.0.1:6721/session')
        if r.status_code == 200:
            TimerToRestart = 2
            HandleGame()
        else:
            time.sleep(10)
            TimerToRestart -= 1
            if TimerToRestart <= 0 :
                print("Restarting Echo VR")

                subprocess = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
                output, error = subprocess.communicate()
                print(output)
                target_process = "echovr.exe"
                print("Killing Echo VR")

                for line in output.splitlines():
                    if target_process in str(line):
                        pid = int(line.split(None, 1)[0])
                        os.kill(pid, 9)
                time.sleep(5)
                print("Killing Bugfinder")

                target_process = "BsSndRpt64.exe"
                for line in output.splitlines():
                    if target_process in str(line):
                        pid = int(line.split(None, 1)[0])
                        os.kill(pid, 9)
                time.sleep(5)
                print("rerunning Echo VR")
                subprocess.Popen(['run.bat'])
                print("Waiting")

                time.sleep(45)
                TimerToRestart = 60

    except:
        traceback.print_exc()
        if not process_exists("echovr.exe"):
            subprocess.Popen(['run.bat'])
        time.sleep(30)     