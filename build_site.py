"""
build_site.py
--------------
The missing step. export_json.py only updates archive_data.json on disk --
it does NOT touch index.html, because index.html has its data baked
directly into a <script> tag for speed (so the page works by just
double-clicking it, with no local server needed).

This script does that baking: it takes index_template.html (the page
with a __ARCHIVE_JSON__ placeholder instead of real data) and
archive_data.json (the latest export), and writes out a fresh index.html
with the current data embedded.

Correct workflow after adding a song:

    python add_song.py          # or import add_song() in your own script
    python export_json.py       # writes an updated archive_data.json
    python build_site.py        # bakes that data into index.html  <-- this step was missing

Run:  python build_site.py
"""

import json

TEMPLATE_PATH = "index_template.html"
DATA_PATH = "archive_data.json"
OUTPUT_PATH = "index.html"


def build_site():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    archive_json = json.dumps(data, ensure_ascii=False)

    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        html = f.read()

    if "__ARCHIVE_JSON__" not in html:
        raise RuntimeError(
            f"{TEMPLATE_PATH} has no __ARCHIVE_JSON__ placeholder -- "
            "make sure you're editing index_template.html, not index.html, "
            "if you change the page's design or layout."
        )

    html = html.replace("__ARCHIVE_JSON__", archive_json)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(
        f"Rebuilt {OUTPUT_PATH}: {len(data['songs'])} songs, "
        f"{len(data['composers'])} composers, {len(data['lyricists'])} lyricists, "
        f"{len(data['vocalists'])} co-vocalists, {len(data['actors'])} actors."
    )


if __name__ == "__main__":
    build_site()
