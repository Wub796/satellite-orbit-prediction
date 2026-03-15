import requests
import numpy as np
import pandas as pd
from sgp4.api import Satrec
import matplotlib.pyplot as plt

url = "https://celestrak.org/NORAD/elements/stations.txt"
data = requests.get(url).text
lines = data.split("\n")

satellites = []

for i in range(0, len(lines)-2, 3):
    name = lines[i].strip()
    line1 = lines[i+1].strip()
    line2 = lines[i+2].strip()

    satellites.append((name, line1, line2))

def tle_position(line1, line2):
    sat = Satrec.twoline2rv(line1, line2)
    jd = sat.jdsatepoch
    fr = sat.jdsatepochF
    e, r, v = sat.sgp4(jd, fr)
    return np.array(r)

rows = []

for sat in satellites:
    try:
        pos = tle_position(sat[1], sat[2])
        error = np.linalg.norm(pos)

        rows.append({
            "name": sat[0],
            "orbit_radius_km": error
        })
    except:
        pass

df = pd.DataFrame(rows)

plt.hist(df["orbit_radius_km"], bins=20)
plt.title("Satellite Orbit Radius Distribution")
plt.xlabel("Radius (km)")
plt.ylabel("Count")

plt.show()
