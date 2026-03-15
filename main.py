import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sgp4.api import Satrec, jday

TLE_URL = "https://celestrak.org/NORAD/elements/stations.txt"


def download_tle_data(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def parse_tle(tle_text):
    lines = [line.strip() for line in tle_text.strip().splitlines() if line.strip()]
    satellites = []
    i = 0
    while i + 2 < len(lines):
        name = lines[i]
        line1 = lines[i + 1]
        line2 = lines[i + 2]
        if line1.startswith("1 ") and line2.startswith("2 "):
            satellites.append({"name": name, "line1": line1, "line2": line2})
            i += 3
        else:
            i += 1
    return satellites


def tle_to_position(satellite):
    sat = Satrec.twoline2rv(satellite["line1"], satellite["line2"])
    e, r, v = sat.sgp4(2460000.5, 0.0)
    if e == 0:
        return r[0], r[1], r[2]
    return None, None, None


def main():
    print("Downloading TLE data from CelesTrak...")
    tle_text = download_tle_data(TLE_URL)

    print("Parsing TLE records...")
    satellites = parse_tle(tle_text)
    print(f"Found {len(satellites)} satellites.")

    print("Computing orbital positions...")
    records = []
    for sat in satellites:
        x, y, z = tle_to_position(sat)
        if x is not None:
            records.append(
                {
                    "name": sat["name"],
                    "x_km": x,
                    "y_km": y,
                    "z_km": z,
                }
            )

    df = pd.DataFrame(records, columns=["name", "x_km", "y_km", "z_km"])

    print("\nFirst few rows of orbital positions:")
    print(df.head())

    plt.figure(figsize=(10, 8))
    plt.scatter(df["x_km"], df["y_km"], s=10, alpha=0.7, color="steelblue")
    plt.title("Satellite Orbit Positions")
    plt.xlabel("X (km)")
    plt.ylabel("Y (km)")
    plt.tight_layout()
    plt.savefig("satellite_orbit_positions.png", dpi=150)
    try:
        plt.show()
    except Exception:
        pass
    print("\nPlot saved to satellite_orbit_positions.png")


if __name__ == "__main__":
    main()
