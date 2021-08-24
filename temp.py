import pickle
import bz2
import json
path = "C:/Users/kaleb/Desktop/ECRanked/Replays/combustion/{1.1}[2021-08-22 23-02-25] F4911213-422A-4712-B475-E25AB1AB31C0.ecrreplay"
with bz2.open(path) as f:
    data = pickle.load(f)
with open("tempExport.txt","w") as f:
    f.write(json.dumps(data))