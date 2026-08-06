"""
add_song.py
-----------
Adds one new song to the database. This is the "adding data to the main
table" piece: it inserts a row into `songs`, and for every composer /
lyricist / vocalist named, it either reuses their existing row (via the
get_or_create helpers) or creates a new one -- so the reference tables
never end up with duplicate people.

Two ways to use it:

1) Import the function from another script:

    from models import get_session
    from add_song import add_song

    session = get_session()
    add_song(
        session,
        title="Tere Bina",
        film_name="Example Film",
        film_year=2024,
        composers=["Pritam"],                       # reuses existing Pritam row
        lyricists=["Amitabh Bhattacharya"],          # reuses existing row
        vocalists=["Arijit Singh", "Shreya Ghoshal"],  # Arijit auto-marked lead
        actors=["Ranbir Kapoor"],                    # optional -- who it's picturised on
    )
    session.commit()

2) Run this file directly for an interactive prompt:

    python add_song.py
"""

from models import get_session, Song
from db_helpers import (
    get_or_create_film,
    get_or_create_composer,
    get_or_create_lyricist,
    get_or_create_vocalist,
    get_or_create_actor,
    split_names,
)


def add_song(session, title, film_name, film_year, composers, lyricists, vocalists,
             actors=None, lead_vocalist="Arijit Singh"):
    """
    Adds a new song. `composers`, `lyricists`, `vocalists`, `actors` are
    lists of plain name strings (`actors` is optional -- some songs, like
    non-film singles, aren't picturised on anyone). Returns the created
    Song, or None if a song with that exact title + film already exists
    (no duplicate rows).
    """
    film = get_or_create_film(session, film_name.strip(), int(film_year))

    existing = (
        session.query(Song)
        .filter_by(title=title.strip(), film_id=film.id)
        .first()
    )
    if existing is not None:
        print(f'Skipped: "{title}" ({film_name}, {film_year}) is already in the database.')
        return None

    # Make sure Arijit Singh is always credited -- this is his archive.
    vocalist_names = [v.strip() for v in vocalists if v.strip()]
    if lead_vocalist not in vocalist_names:
        vocalist_names.insert(0, lead_vocalist)

    song = Song(title=title.strip(), film=film)
    session.add(song)

    for name in composers:
        song.composers.append(get_or_create_composer(session, name))

    for name in lyricists:
        song.lyricists.append(get_or_create_lyricist(session, name))

    for name in (actors or []):
        song.actors.append(get_or_create_actor(session, name))

    session.flush()  # song.id now exists, needed for the vocalist link rows

    from models import SongVocalist
    for name in vocalist_names:
        vocalist = get_or_create_vocalist(session, name)
        link = SongVocalist(
            song_id=song.id,
            vocalist_id=vocalist.id,
            is_lead=(name == lead_vocalist),
        )
        session.add(link)

    session.commit()
    print(f'Added: "{title}" -- {film_name} ({film_year})')
    return song


def _prompt(label, default=None):
    suffix = f" [{default}]" if default else ""
    val = input(f"{label}{suffix}: ").strip()
    return val or default


def interactive_add():
    session = get_session()
    print("Add a new song to the Arijit Singh archive.\n(Separate multiple names with commas.)\n")

    title = _prompt("Song title")
    film_name = _prompt("Film name")
    film_year = _prompt("Film year")
    composers = split_names(_prompt("Composer(s)"))
    lyricists = split_names(_prompt("Lyricist(s)"))
    actors = split_names(_prompt("Actor(s) picturised on, if any (leave blank if none)", default=""))
    other_vocalists = split_names(_prompt("Co-vocalist(s), if any (leave blank if solo)", default=""))

    add_song(
        session,
        title=title,
        film_name=film_name,
        film_year=film_year,
        composers=composers,
        lyricists=lyricists,
        vocalists=["Arijit Singh"] + other_vocalists,
        actors=actors,
    )
    session.close()


if __name__ == "__main__":
    interactive_add()
