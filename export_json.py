"""
export_json.py
---------------
Reads the normalized database and writes archive_data.json, a single
file the static front-end loads. It contains:

  songs       - one entry per song, with film + composer/lyricist/
                vocalist NAMES already resolved (joined) for display
  composers   - every composer, with a song count, for the browse view
  lyricists   - same, for lyricists
  vocalists   - same, for vocalists (co-vocalists, since Arijit is on
                every song by definition of this archive)

Run:  python export_json.py
"""

import json
from models import get_session, Song, Composer, Lyricist, Vocalist, Actor

session = get_session()

songs = (
    session.query(Song)
    .join(Song.film)
    .order_by("year", Song.title)
    .all()
)

song_data = []
for s in songs:
    song_data.append({
        "id": s.id,
        "title": s.title,
        "film": s.film.name,
        "year": s.film.year,
        "composers": [c.name for c in s.composers],
        "lyricists": [l.name for l in s.lyricists],
        "actors": [a.name for a in s.actors],
        "vocalists": [
            {"name": link.vocalist.name, "is_lead": link.is_lead}
            for link in s.vocalists
        ],
    })

def role_list(model):
    rows = session.query(model).all()
    out = [{"name": r.name, "count": len(r.songs)} for r in rows]
    return sorted(out, key=lambda r: (-r["count"], r["name"]))

def vocalist_list():
    rows = session.query(Vocalist).all()
    out = [{"name": r.name, "count": len(r.song_links)} for r in rows if r.name != "Arijit Singh"]
    return sorted(out, key=lambda r: (-r["count"], r["name"]))

data = {
    "songs": song_data,
    "composers": role_list(Composer),
    "lyricists": role_list(Lyricist),
    "vocalists": vocalist_list(),
    "actors": role_list(Actor),
}

with open("archive_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Exported {len(song_data)} songs, {len(data['composers'])} composers, "
      f"{len(data['lyricists'])} lyricists, {len(data['vocalists'])} co-vocalists, "
      f"{len(data['actors'])} actors to archive_data.json")

session.close()
