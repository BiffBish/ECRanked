import os
import json
import requests
SKIMSPATH = "E:/ECRanked/Skims"

maps = ["combustion","dyson","fission","surge"]
for map in maps:
    for skim in os.listdir(f"{SKIMSPATH}/{map}"):
        SkimData = json.load(open(f"{SKIMSPATH}/{map}/{skim}"))
        Formdata = {
                "key": "1a508f8b-1dd2-412c-aa4e-0eda0c4aa6fc",
                "data" : json.dumps(SkimData)
                }
        print(requests.post(f"http://localhost/save_skim.py",data=Formdata))