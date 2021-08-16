

import os

old_file_name = "/home/career_karma/raw_data.csv"
new_file_name = "/home/career_karma/old_data.csv"


maps = ["combustion","dyson","fission","surge"]
for map in maps:
    mapPath = f"D:/Replays/{map}"
    files = os.listdir(mapPath)
    for f in files:
        print(f)
        os.rename(f"{mapPath}/{f}", f"{mapPath}/{f[:-10]}.ecreplay")

print("Files renamed!")