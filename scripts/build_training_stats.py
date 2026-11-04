"""Summarize Garmin activity exports into assets/life/training.json for the Life page.

Why a committed summary instead of a live API call: the site is built by
GitHub Actions, which cannot reach the owner's Garmin data, and a public page
should only ever see aggregates. So this runs on the owner's machine against
the Garmin activity JSON files (one per activity, as returned by Garmin's
personal API) and writes totals only:

  - per-year hours by discipline, the last 52 weeks of weekly hours,
  - lifetime distance/hours/elevation per discipline,
  - longest ride, best 20-minute power, and running best efforts.

Nothing that locates or identifies a single session is written: no GPS
coordinates, place or activity names, start times, heart rate, or other
health data. Activities the owner marked private on Garmin are skipped, and
motorised or non-training types (e-bike, ATV, breathwork...) never count.

Usage: python scripts/build_training_stats.py --src <dir of activity .json> [--out assets/life/training.json]
"""
import argparse
import datetime as dt
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DISCIPLINES = {
    "swim": {"lap_swimming", "open_water_swimming", "swimming"},
    "bike": {"cycling", "road_biking", "virtual_ride", "indoor_cycling", "mountain_biking", "gravel_cycling"},
    "run": {"running", "treadmill_running", "trail_running", "track_running", "indoor_running", "street_running", "ultra_run"},
    "row": {"rowing_v2", "indoor_rowing"},
    "hike": {"hiking", "mountaineering"},
}
ORDER = ["swim", "bike", "run", "row", "hike", "other"]
# Motorised or not training: never counted anywhere.
EXCLUDE = {"atv_v2", "e_bike_fitness", "e_bike_mountain", "stop_watch", "breathwork", "meditation"}
# Treadmill splits come from a foot pod or the belt, not a measured course.
OUTDOOR_RUN = {"running", "trail_running", "track_running", "street_running", "ultra_run"}
BEST_EFFORTS = [("5K", "fastestSplit_5000", 5000), ("10K", "fastestSplit_10000", 10000),
                ("Half marathon", "fastestSplit_21098", 21097.5), ("Marathon", "fastestSplit_42195", 42195)]
MIN_PACE_S_PER_KM = 180  # anything faster than 3:00/km is a GPS glitch for this athlete
# A forgotten stop button turns a walk into a 20-hour "activity"; cap what one session can add.
MAX_SESSION_HOURS = 24


def discipline(type_key):
    for name, keys in DISCIPLINES.items():
        if type_key in keys:
            return name
    return "other"


def load(src):
    out = []
    for path in glob.glob(os.path.join(src, "*.json")):
        with open(path, encoding="utf-8") as f:
            a = json.load(f)
        privacy = a.get("privacy")
        if (privacy.get("typeKey") if isinstance(privacy, dict) else privacy) == "private":
            continue
        type_key = (a.get("activityType") or {}).get("typeKey", "")
        if type_key in EXCLUDE or not a.get("startTimeLocal"):
            continue
        a["_type"] = type_key
        a["_disc"] = discipline(type_key)
        a["_date"] = dt.date.fromisoformat(str(a["startTimeLocal"])[:10])
        a["_hours"] = min((a.get("duration") or 0) / 3600, MAX_SESSION_HOURS)
        a["_km"] = (a.get("distance") or 0) / 1000
        a["_elev"] = a.get("elevationGain") or 0
        out.append(a)
    return out


def summarize(acts):
    if not acts:
        raise SystemExit("No activities found")
    as_of = max(a["_date"] for a in acts)
    years = range(min(a["_date"].year for a in acts), as_of.year + 1)

    by_year = {y: {d: 0.0 for d in ORDER} for y in years}
    for a in acts:
        by_year[a["_date"].year][a["_disc"]] += a["_hours"]

    week0 = as_of - dt.timedelta(days=as_of.weekday()) - dt.timedelta(weeks=51)
    weeks = [{"start": (week0 + dt.timedelta(weeks=i)).isoformat(), "hours": 0.0} for i in range(52)]
    for a in acts:
        i = (a["_date"] - week0).days // 7
        if 0 <= i < 52:
            weeks[i]["hours"] += a["_hours"]

    disciplines = {}
    for d in ORDER:
        group = [a for a in acts if a["_disc"] == d]
        if not group:
            continue
        info = {
            "activities": len(group),
            "hours": round(sum(a["_hours"] for a in group)),
            "km": round(sum(a["_km"] for a in group)),
            "elevation_m": round(sum(a["_elev"] for a in group)),
            "since": min(a["_date"].year for a in group),
        }
        longest = max(group, key=lambda a: a["_km"])
        if longest["_km"] > 0:
            info["longest_km"] = round(longest["_km"], 1)
            info["longest_year"] = longest["_date"].year
        disciplines[d] = info

    power = [(a["max20MinPower"], a["_date"].year) for a in acts if a["_disc"] == "bike" and a.get("max20MinPower")]
    if power:
        watts, year = max(power)
        disciplines["bike"]["best_20min_w"] = round(watts)
        disciplines["bike"]["best_20min_year"] = year

    efforts = []
    for label, key, meters in BEST_EFFORTS:
        times = [(a[key], a["_date"].year) for a in acts
                 if a["_type"] in OUTDOOR_RUN and a.get(key) and a[key] / (meters / 1000) >= MIN_PACE_S_PER_KM]
        if times:
            seconds, year = min(times)
            # Truncate like Garmin Connect does, so 4:07:44.9 reads 4:07:44 in both places.
            efforts.append({"label": label, "seconds": int(seconds), "year": year})
    if efforts:
        disciplines["run"]["best_efforts"] = efforts

    return {
        "source": "Garmin Connect",
        "as_of": as_of.isoformat(),
        "totals": {
            "activities": len(acts),
            "hours": round(sum(a["_hours"] for a in acts)),
            "km": round(sum(a["_km"] for a in acts)),
            "elevation_m": round(sum(a["_elev"] for a in acts)),
            "since": years[0],
        },
        "years": [{"year": y, "hours": {d: round(h, 1) for d, h in by_year[y].items()}} for y in years],
        "weeks": [{"start": w["start"], "hours": round(w["hours"], 1)} for w in weeks],
        "disciplines": disciplines,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, help="directory of Garmin activity .json files")
    ap.add_argument("--out", default=os.path.join(ROOT, "assets", "life", "training.json"))
    args = ap.parse_args()
    data = summarize(load(args.src))
    tmp = args.out + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, args.out)
    t = data["totals"]
    print(f"{args.out}: {t['activities']} activities, {t['hours']} h, {t['km']} km through {data['as_of']}")


if __name__ == "__main__":
    main()
