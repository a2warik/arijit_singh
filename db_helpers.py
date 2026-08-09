"""
db_helpers.py
-------------
"get or create" helpers -- the standard pattern for keeping reference
tables free of duplicates. Before inserting "Pritam" as a Composer, we
first check whether a Composer named "Pritam" already exists; if so we
reuse that row (and its id) instead of creating a second one.

add_song.py goes through these functions for every insert, which is
what guarantees "no repeats."
"""

from models import Film, Composer, Lyricist, Vocalist, Actor


def get_or_create_film(session, name, year):
    film = session.query(Film).filter_by(name=name, year=year).first()
    if film is None:
        film = Film(name=name, year=year)
        session.add(film)
        session.flush()  # assigns film.id without a full commit
    return film


def get_or_create_composer(session, name):
    name = name.strip()
    obj = session.query(Composer).filter_by(name=name).first()
    if obj is None:
        obj = Composer(name=name)
        session.add(obj)
        session.flush()
    return obj


def get_or_create_lyricist(session, name):
    name = name.strip()
    obj = session.query(Lyricist).filter_by(name=name).first()
    if obj is None:
        obj = Lyricist(name=name)
        session.add(obj)
        session.flush()
    return obj


def get_or_create_vocalist(session, name):
    name = name.strip()
    obj = session.query(Vocalist).filter_by(name=name).first()
    if obj is None:
        obj = Vocalist(name=name)
        session.add(obj)
        session.flush()
    return obj


def get_or_create_actor(session, name):
    name = name.strip()
    obj = session.query(Actor).filter_by(name=name).first()
    if obj is None:
        obj = Actor(name=name)
        session.add(obj)
        session.flush()
    return obj


def split_names(raw):
    """'Irshad Kamil, Gulzar' -> ['Irshad Kamil', 'Gulzar']"""
    return [n.strip() for n in raw.split(",") if n.strip()]
