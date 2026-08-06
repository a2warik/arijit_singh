"""
export_json_from_csv.py
------------------------
Builds archive_data.json from the full Wikipedia-sourced song list at
DataSets/arijit_wikipedia_songs_with_actor.csv (476 songs, 2011-2026),
including the researched male-lead-actor column and its accompanying
judgment-call notes.

This is now the site's data source, in place of the smaller SQLAlchemy-DB
-driven export_json.py.

Correct workflow after updating the CSV:

    python3 export_json_from_csv.py   # writes an updated archive_data.json
    python3 build_site.py             # bakes that data into index.html

Run:  python3 export_json_from_csv.py
"""

import csv
import json
from collections import Counter

CSV_PATH = "DataSets/arijit_wikipedia_songs_with_actor.csv"
OUTPUT_PATH = "archive_data.json"

LEAD_VOCALIST = "Arijit Singh"


def split_names(value):
    return [p.strip() for p in value.split(",") if p.strip()]


def split_actors(value):
    return [p.strip() for p in value.split("/") if p.strip()]


def to_ranked_list(counter):
    return [
        {"name": name, "count": count}
        for name, count in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    ]


def build():
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    songs = []
    composer_counts = Counter()
    lyricist_counts = Counter()
    vocalist_counts = Counter()
    actor_counts = Counter()

    for i, row in enumerate(rows, start=1):
        composers = split_names(row["composers"])
        lyricists = split_names(row["lyricists"])
        co_vocalists = split_names(row["co_vocalists"])
        actors = split_actors(row["actor"])

        vocalists = [{"name": LEAD_VOCALIST, "is_lead": True}]
        vocalists += [{"name": v, "is_lead": False} for v in co_vocalists]

        song = {
            "id": i,
            "title": row["title"].strip(),
            "film": row["film"].strip(),
            "year": int(row["year"]),
            "composers": composers,
            "lyricists": lyricists,
            "vocalists": vocalists,
            "actors": actors,
        }

        note = (row.get("note") or "").strip()
        if note:
            song["note"] = note

        youtube_url = (row.get("youtube_url") or "").strip()
        if youtube_url:
            song["youtube_url"] = youtube_url

        songs.append(song)

        for c in composers:
            composer_counts[c] += 1
        for l in lyricists:
            lyricist_counts[l] += 1
        for v in co_vocalists:
            vocalist_counts[v] += 1
        for a in actors:
            actor_counts[a] += 1

    data = {
        "songs": songs,
        "composers": to_ranked_list(composer_counts),
        "lyricists": to_ranked_list(lyricist_counts),
        "vocalists": to_ranked_list(vocalist_counts),
        "actors": to_ranked_list(actor_counts),
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(
        f"Wrote {OUTPUT_PATH}: {len(songs)} songs, {len(data['composers'])} composers, "
        f"{len(data['lyricists'])} lyricists, {len(data['vocalists'])} co-vocalists, "
        f"{len(data['actors'])} actors."
    )


if __name__ == "__main__":
    build()
