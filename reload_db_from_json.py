"""
reload_db_from_json.py
-----------------------
Wipes every row from the database and reloads it from archive_data.json
(built by export_json_from_csv.py from the full Wikipedia-sourced CSV),
using the same normalized schema and get-or-create insert path as
add_song.py -- this is the bulk equivalent of calling add_song() once per
song in the JSON, so composers/lyricists/vocalists/actors still each get
exactly one row no matter how many songs they appear on.

archive_data.json's "note" field (why an ambiguous male-lead pick was
made) is imported into Song.actor_note.

Run:  python3 reload_db_from_json.py
"""

import json

from sqlalchemy import text

from db_helpers import (
    get_or_create_actor,
    get_or_create_composer,
    get_or_create_film,
    get_or_create_lyricist,
    get_or_create_vocalist,
)
from models import Song, SongVocalist, get_session

DATA_PATH = "archive_data.json"

# Deletion order matters under foreign-key constraints: link/association
# tables and dependents first, then the reference tables they point to.
TABLES_IN_DELETE_ORDER = [
    "song_vocalists",
    "song_composers",
    "song_lyricists",
    "song_actors",
    "songs",
    "films",
    "composers",
    "lyricists",
    "vocalists",
    "actors",
]


def wipe(session):
    # None of these tables use AUTOINCREMENT, so SQLite has no sqlite_sequence
    # counter to reset -- once a table is empty, plain INTEGER PRIMARY KEY
    # ids naturally start back at 1 on the next insert.
    for table in TABLES_IN_DELETE_ORDER:
        session.execute(text(f"DELETE FROM {table}"))
    session.commit()


def load(session, data):
    inserted = 0
    for entry in data["songs"]:
        film = get_or_create_film(session, entry["film"].strip(), int(entry["year"]))

        song = Song(
            title=entry["title"].strip(),
            film=film,
            youtube_url=(entry.get("youtube_url") or None),
            actor_note=(entry.get("note") or None),
        )
        session.add(song)

        for name in entry["composers"]:
            song.composers.append(get_or_create_composer(session, name))
        for name in entry["lyricists"]:
            song.lyricists.append(get_or_create_lyricist(session, name))
        for name in entry["actors"]:
            song.actors.append(get_or_create_actor(session, name))

        session.flush()  # song.id now exists, needed for the vocalist link rows

        for v in entry["vocalists"]:
            vocalist = get_or_create_vocalist(session, v["name"])
            session.add(SongVocalist(
                song_id=song.id,
                vocalist_id=vocalist.id,
                is_lead=bool(v["is_lead"]),
            ))

        inserted += 1

    session.commit()
    return inserted


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    session = get_session()
    wipe(session)
    count = load(session, data)
    session.close()
    print(f"Reloaded database: {count} songs from {DATA_PATH}.")


if __name__ == "__main__":
    main()
