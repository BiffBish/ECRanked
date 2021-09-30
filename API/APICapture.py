import time
from datetime import datetime , timedelta
import json
import os
framerate = 30

import traceback

import zipfile
import subprocess 
from skims import CaculateSkims

import glob
import os
import requests
import psutil
import aiohttp
import asyncio
import threading
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SkimFilePath = "C:/Users/kaleb/DiscordBots/ECRanked/API/Skims"
ReplayFilePath = "C:/Users/kaleb/DiscordBots/ECRanked/API/Replays"

def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())


CrashGameID = ""
async def HandleGame(session):
    r = await session.get('http://127.0.0.1:6721/session')
    startingTime = time.time() 
    t=time.time()
    CurrentGame = dict()
    FrameCount = 0
    ActivePlayerList = dict()
    jsonData = await r.json()
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
        running = False
        while True:
            try:
                thread_return={"session": None,"player_bones":None}
                
                from threading import Thread
                def task(thread_return,url,value):
                    req = requests.get(url)
                    thread_return[value] = {"text":req.text,"status":req.status_code}
                    
                sessionThread = Thread(target=task, args=(thread_return,'http://127.0.0.1:6721/session',"session",))
                bonesThread = Thread(target=task, args=(thread_return,'http://127.0.0.1:6721/player_bones',"player_bones",))
                
                sessionThread.start()
                bonesThread.start()

                sessionThread.join()
                bonesThread.join()

                # r = await session.get('http://127.0.0.1:6721/session')
                # boneData = await session.get('http://127.0.0.1:6721/player_bones')

                if thread_return["session"]["status"] == 404:
                    running = False
                    print(f"Game Finish! {jsonData['sessionid']}")    
                    break

                if CrashGameID != "":
                    if running == False:
                        jsonData = await r.json()
                        if CrashGameID != jsonData["sessionid"]:
                            print(f"Game Crash Finish! {jsonData['sessionid']}")    
                            break
                    running = True
                    currentGametxt.write("\n")
                    CrashGameID = ""
                nowTime = datetime.now()
                #During entire game
                FrameCount += 1
                t += 1/framerate

            
                currentGametxt.write(f"{nowTime}\t{thread_return['session']['text']}\t{thread_return['player_bones']['text']}\n")
                print(f"Capturing Frame! [{FrameCount}] ({nowTime})")
                time.sleep(max(0,t-time.time()))  
            except Exception as e: 
                print(e)
                traceback.print_exc()
                running = False
                jsonData = await r.json()
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
                    print("Killing Echo VR")
                    PROCNAME = "echovr.exe"
                    for proc in psutil.process_iter():
                        # check whether the process name matches
                        if proc.name() == PROCNAME:
                            proc.kill()
                    time.sleep(5)
                    print("Killing Bugfinder")
                    PROCNAME = "BsSndRpt64.exe"
                    for proc in psutil.process_iter():
                        # check whether the process name matches
                        if proc.name() == PROCNAME:
                            proc.kill()

                print("Waiting 10s")
                time.sleep(10)
                print("Done!")   

    echoReplayPath = f"{ReplayFilePath}/{mapSaveLocation}/[{StartTimeSTR}] {SessionID}.echoreplay"
    zipObj = zipfile.ZipFile(echoReplayPath, 'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)

    # Add multiple files to the zip
    zipObj.write(f"{SessionID}.echoreplay")
    zipObj.close()
    SkimData = CaculateSkims(open(f"{SessionID}.echoreplay","r").read().split("\n"))
    SkimLink = f"{SkimFilePath}/{mapSaveLocation}/[{StartTimeSTR}] {SessionID}.ecrs"
    with open(SkimLink, 'w') as f:
        f.write(json.dumps(SkimData))

    SkimData["replay_link"] = echoReplayPath
    SkimData["skim_link"] = SkimLink
    SkimData["session_id"] = SessionID

    Formdata = {
            "key": "1a508f8b-1dd2-412c-aa4e-0eda0c4aa6fc",
            "data" : json.dumps(SkimData)
    }
    print(requests.post(f"http://localhost/save_skim.py",data=Formdata))
    os.remove(f"{SessionID}.echoreplay")  

    webHookUrl = "https://discord.com/api/webhooks/882380147645354055/MzYHqnqatGkoidWApt0jlN5CO7FCKyK-kaDB8epctzKGw-tKRJgNovqpWv9cWdmskspb"
    playerIDs = []
    for playerData in SkimData["players"]:
        playerIDs.append(str(playerData["userid"]))

    data = {"content":",".join(playerIDs)}
    requests.post(webHookUrl,data= data)

async def main():
    async with aiohttp.ClientSession() as session:
        TimerToRestart = 60
        while True:
            try:
                r = requests.get('http://127.0.0.1:6721/session')
                if r.status_code == 200:
                    TimerToRestart = 60
                    await HandleGame(session)
                else:
                    print(f"Got 200:{TimerToRestart}")
                    time.sleep(10)
                    TimerToRestart -= 1
                    if TimerToRestart <= 0 :
                        print("Restarting Echo VR")


                        
                        print("Killing Echo VR")
                        PROCNAME = "echovr.exe"
                        for proc in psutil.process_iter():
                            # check whether the process name matches
                            if proc.name() == PROCNAME:
                                proc.kill()
                        time.sleep(5)
                        print("Killing Bugfinder")
                        PROCNAME = "BsSndRpt64.exe"
                        for proc in psutil.process_iter():
                            # check whether the process name matches
                            if proc.name() == PROCNAME:
                                proc.kill()
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

asyncio.run(main())