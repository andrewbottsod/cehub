#!/usr/bin/env python3
"""Build per-prefix ZIP centroid files from US Census public-domain data.

Sources (downloaded, not committed):
  2024 Gazetteer national ZCTA file — internal point lat/lon
  2020 ZCTA-to-place relationship — place name, largest incorporated place
"""
import csv
import io
import json
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

GAZ_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_zcta_national.zip"
REL_URL = "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_place20_natl.txt"
OUT = Path(__file__).resolve().parents[1] / "cehub" / "data" / "zip"

FIPS = {
    "01":"AL","02":"AK","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT","10":"DE","11":"DC","12":"FL",
    "13":"GA","15":"HI","16":"ID","17":"IL","18":"IN","19":"IA","20":"KS","21":"KY","22":"LA","23":"ME",
    "24":"MD","25":"MA","26":"MI","27":"MN","28":"MS","29":"MO","30":"MT","31":"NE","32":"NV","33":"NH",
    "34":"NJ","35":"NM","36":"NY","37":"NC","38":"ND","39":"OH","40":"OK","41":"OR","42":"PA","44":"RI",
    "45":"SC","46":"SD","47":"TN","48":"TX","49":"UT","50":"VT","51":"VA","53":"WA","54":"WV","55":"WI",
    "56":"WY","60":"AS","66":"GU","69":"MP","72":"PR","78":"VI",
}
SUFFIXES = (" city and borough", " municipality", " comunidad", " zona urbana", " CDP", " city", " town", " village", " borough")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "cehub-zcta-build"})
    with urllib.request.urlopen(req, timeout=120) as res:
        return res.read()


def clean_place(name):
    for suf in SUFFIXES:
        if name.endswith(suf):
            return name[: -len(suf)]
    return name


def load_places(raw):
    text = raw.decode("utf-8-sig")
    best = {}
    for row in csv.reader(io.StringIO(text), delimiter="|"):
        if len(row) < 17 or not row[1] or not row[10]:
            continue
        z = row[1].zfill(5)
        try:
            area = int(row[16] or 0)
        except ValueError:
            area = 0
        incorporated = (row[14] or "").startswith("C")
        rank = (1 if incorporated else 0, area)
        cur = best.get(z)
        if cur is None or rank > cur[0]:
            st = FIPS.get((row[9] or "")[:2], "")
            best[z] = (rank, clean_place(row[10]), st)
    return {z: (city, st) for z, (_r, city, st) in best.items()}


def load_centroids(raw):
    zf = zipfile.ZipFile(io.BytesIO(raw))
    name = next(n for n in zf.namelist() if n.endswith(".txt"))
    text = zf.read(name).decode("latin1")
    out = {}
    for line in text.splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) < 7 or not parts[0].strip().isdigit():
            continue
        z = parts[0].strip().zfill(5)
        lat = round(float(parts[5]), 4)
        lon = round(float(parts[6]), 4)
        out[z] = (lat, lon)
    return out


def main():
    print("downloading gazetteer…")
    cents = load_centroids(fetch(GAZ_URL))
    print("centroids", len(cents))
    print("downloading place relationship…")
    places = load_places(fetch(REL_URL))
    print("places", len(places))
    buckets = defaultdict(dict)
    for z, (lat, lon) in cents.items():
        city, st = places.get(z, ("", ""))
        rec = [lat, lon]
        if city and st:
            rec.extend([city, st])
        elif city:
            rec.append(city)
        buckets[z[:3]][z] = rec
    if OUT.exists():
        for old in OUT.glob("*.json"):
            old.unlink()
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for prefix, rows in buckets.items():
        path = OUT / f"{prefix}.json"
        path.write_text(json.dumps(rows, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
        total += path.stat().st_size
    index = sorted(buckets)
    (OUT / "index.json").write_text(json.dumps(index, separators=(",", ":")), encoding="utf-8")
    total += (OUT / "index.json").stat().st_size
    sample = buckets.get("242", {}).get("24219")
    print("files", len(buckets), "bytes", total, "sample", sample)


if __name__ == "__main__":
    main()
