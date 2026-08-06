"""
models.py
---------
The database design.

WHY IT'S SHAPED THIS WAY
=========================
A flat spreadsheet repeats "Irshad Kamil" or "Pritam" on every row they
worked on. That's the exact problem relational design solves: store each
composer / lyricist / vocalist / film ONCE, in its own table, and have
songs *point to* those rows by id (a foreign key) instead of retyping
the name. SQLAlchemy's `relationship()` is what turns those foreign keys
into easy two-way navigation in Python, e.g.:

    irshad = session.query(Lyricist).filter_by(name="Irshad Kamil").first()
    irshad.songs        # -> every Song he wrote, no extra query needed

Tables
------
Film        (id, name, year)                 -- one row per film+year
Composer    (id, name)                       -- one row per composer/duo
Lyricist    (id, name)                       -- one row per lyricist/duo
Vocalist    (id, name)                       -- one row per singer
Song        (id, title, film_id)             -- one row per song

A song can have MULTIPLE composers/lyricists/vocalists, and a person can
appear on MULTIPLE songs -> that's a many-to-many relationship, which in
a relational database always needs a link table in between:

song_composers   (song_id, composer_id)
song_lyricists   (song_id, lyricist_id)
song_vocalists   (song_id, vocalist_id, is_lead)  -- association OBJECT,
                  because it needs to carry extra info (is Arijit Singh
                  the lead voice, or a featured/co-vocalist?)
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Boolean,
    UniqueConstraint, Table,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DB_PATH = "sqlite:///arijit_songs.db"
Base = declarative_base()


# ---------------------------------------------------------------------------
# Plain many-to-many link tables (no extra data of their own -> a simple
# Table() is enough; SQLAlchemy manages the rows automatically).
# ---------------------------------------------------------------------------
song_composers = Table(
    "song_composers", Base.metadata,
    Column("song_id", ForeignKey("songs.id"), primary_key=True),
    Column("composer_id", ForeignKey("composers.id"), primary_key=True),
)

song_lyricists = Table(
    "song_lyricists", Base.metadata,
    Column("song_id", ForeignKey("songs.id"), primary_key=True),
    Column("lyricist_id", ForeignKey("lyricists.id"), primary_key=True),
)

song_actors = Table(
    "song_actors", Base.metadata,
    Column("song_id", ForeignKey("songs.id"), primary_key=True),
    Column("actor_id", ForeignKey("actors.id"), primary_key=True),
)


# ---------------------------------------------------------------------------
# Reference tables -- each name lives here exactly once.
# ---------------------------------------------------------------------------
class Film(Base):
    __tablename__ = "films"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)

    songs = relationship("Song", back_populates="film")

    __table_args__ = (UniqueConstraint("name", "year", name="uq_film_name_year"),)

    def __repr__(self):
        return f"<Film {self.name} ({self.year})>"


class Composer(Base):
    __tablename__ = "composers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    songs = relationship("Song", secondary=song_composers, back_populates="composers")

    def __repr__(self):
        return f"<Composer {self.name}>"


class Lyricist(Base):
    __tablename__ = "lyricists"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    songs = relationship("Song", secondary=song_lyricists, back_populates="lyricists")

    def __repr__(self):
        return f"<Lyricist {self.name}>"


class Vocalist(Base):
    __tablename__ = "vocalists"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    # goes through the SongVocalist association OBJECT (see below),
    # since that link also stores whether this person was the lead voice.
    song_links = relationship("SongVocalist", back_populates="vocalist")

    def __repr__(self):
        return f"<Vocalist {self.name}>"


class Actor(Base):
    __tablename__ = "actors"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    # the actor(s) the song was picturised on -- same many-to-many
    # shape as Composer/Lyricist, since a song can have more than one
    # (a duet on-screen) and an actor appears across many songs.
    songs = relationship("Song", secondary=song_actors, back_populates="actors")

    def __repr__(self):
        return f"<Actor {self.name}>"


# ---------------------------------------------------------------------------
# Association OBJECT for Song <-> Vocalist.
# A plain Table() can't hold the "is_lead" flag, so this is mapped as its
# own class instead -- same many-to-many idea, with one extra column.
# ---------------------------------------------------------------------------
class SongVocalist(Base):
    __tablename__ = "song_vocalists"
    song_id = Column(ForeignKey("songs.id"), primary_key=True)
    vocalist_id = Column(ForeignKey("vocalists.id"), primary_key=True)
    is_lead = Column(Boolean, default=False, nullable=False)

    song = relationship("Song", back_populates="vocalist_links")
    vocalist = relationship("Vocalist", back_populates="song_links")


# ---------------------------------------------------------------------------
# The main table. No song title/film/person text is ever duplicated here --
# everything is a foreign key or a link through the tables above.
# ---------------------------------------------------------------------------
class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    film_id = Column(ForeignKey("films.id"), nullable=False)
    youtube_url = Column(String, nullable=True)

    film = relationship("Film", back_populates="songs")
    composers = relationship("Composer", secondary=song_composers, back_populates="songs")
    lyricists = relationship("Lyricist", secondary=song_lyricists, back_populates="songs")
    actors = relationship("Actor", secondary=song_actors, back_populates="songs")
    vocalist_links = relationship("SongVocalist", back_populates="song", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("title", "film_id", name="uq_song_title_film"),)

    @property
    def vocalists(self):
        """All vocalists on this song, lead first."""
        return sorted(self.vocalist_links, key=lambda l: not l.is_lead)

    def __repr__(self):
        return f"<Song {self.title} ({self.film.name if self.film else '?'})>"


def get_engine():
    return create_engine(DB_PATH, echo=False)


def get_session():
    """
    Opens a session against the existing database.

    This deliberately does NOT call Base.metadata.create_all() anymore.
    Schema creation and every schema change now goes through Alembic
    (`alembic upgrade head`), so this file stays the single source of
    truth for what the tables look like, and Alembic's version history
    stays accurate. If the tables don't exist yet, run:

        alembic upgrade head

    before using get_session() for the first time.
    """
    engine = get_engine()
    return sessionmaker(bind=engine)()
