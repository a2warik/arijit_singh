# Using Alembic to evolve the database

Alembic tracks the database schema as a sequence of numbered "migrations."
Instead of dropping and rebuilding `arijit_songs.db` whenever you want a new
column, you write (or autogenerate) a small script that alters it in place —
and it remembers which changes have already been applied, both locally and
on any other copy of the database (like whatever's behind your Vercel site).

## Two things worth knowing up front

**`alembic init` was already run — you don't need to run it again.** That
command generates the scaffold (`../alembic.ini`, `env.py`,
`script.py.mako`, `migrations/versions/`) from nothing. I already
ran it and I'm handing you the result. Just place these files in your
project root, alongside `../models.py` and `arijit_songs.db`, and go straight
to the "one-time setup" step below.

**`Base.metadata.create_all()` has been removed from `get_session()` in
`../models.py`.** It used to run on every single database call. That call
itself is harmless to existing data — it only creates tables that don't
exist yet, it never drops or rewrites one that's already there — but it's
the wrong tool now that Alembic owns the schema: if a new table ever got
added to `../models.py` without a matching migration, `create_all()` would
silently create it anyway, and Alembic's version history would have no
record that it happened. From now on, schema changes only happen through
`alembic upgrade head`. `../seed_data.py` (the "wipe and rebuild a throwaway
copy" script) was updated the same way — it now calls `alembic upgrade
head` to build the schema instead of `create_all()`, so even a from-scratch
rebuild ends up with an accurate `alembic_version` table.

## One-time setup on your existing database

You already have `arijit_songs.db` with real data in it. Alembic needs to
know that its schema is already at the "initial schema" migration, without
trying to re-run the `CREATE TABLE` statements (which would fail, since the
tables already exist):

```
pip install alembic
alembic stamp head
```

`stamp` just writes a row into a new `alembic_version` table saying "this
database is already at this point" — it doesn't touch your songs, films, or
any other data. (I tested this against a copy of your real 70-song database
before writing this guide — confirmed 70 songs in, 70 songs out.)

From now on, `arijit_songs.db` and `../models.py` are meant to change together,
through migrations, rather than by hand-editing the schema.

## Adding a new column later (worked example)

Here's the exact workflow, demonstrated with `youtube_url` on `Song` — I ran
this for real against a copy of your database to make sure it works cleanly
before handing it to you.

**1. Add the column to the model** in `../models.py`:

```python
class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    film_id = Column(ForeignKey("films.id"), nullable=False)
    youtube_url = Column(String, nullable=True)   # <-- new
```

Always make new columns `nullable=True` (or give them a `default=`) —
your 476 existing rows won't have a value yet, and a `NOT NULL` column
with no default will fail to add.

**2. Let Alembic generate the migration by diffing the model against the live database:**

```
alembic revision --autogenerate -m "add youtube_url to songs"
```

This writes a new file into `migrations/versions/`. Open it and read it —
autogenerate is very reliable for simple additions like this, but always
worth a glance. For this example it generated:

```python
def upgrade() -> None:
    with op.batch_alter_table('songs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('youtube_url', sa.String(), nullable=True))

def downgrade() -> None:
    with op.batch_alter_table('songs', schema=None) as batch_op:
        batch_op.drop_column('youtube_url')
```

**3. Apply it:**

```
alembic upgrade head
```

Your existing songs keep every value they had; `youtube_url` comes back as
`NULL` for all of them until you fill it in (e.g. via a small script using
`add_song`-style helpers, or directly in a Python shell).

**4. If you ever need to undo a migration:**

```
alembic downgrade -1
```

## Doing the same for photos (composers, lyricists, vocalists, actors)

When you're ready, the pattern is identical — add a nullable column to each
model, one migration at a time (or all four in one migration, your call):

```python
class Composer(Base):
    ...
    photo_url = Column(String, nullable=True)

class Lyricist(Base):
    ...
    photo_url = Column(String, nullable=True)

class Vocalist(Base):
    ...
    photo_url = Column(String, nullable=True)

class Actor(Base):
    ...
    photo_url = Column(String, nullable=True)
```

then:
```
alembic revision --autogenerate -m "add photo_url to people tables"
alembic upgrade head
```

## After any migration — don't forget the site rebuild

Alembic changes the database; it doesn't touch `../archive_data.json` or
`../index.html`. Once you've populated some `youtube_url` / `photo_url` values,
you'd still update `../export_json.py` to include the new fields in the export,
then run your usual:

```
python export_json.py
python build_site.py
git add .
git commit -m "Add YouTube links"
git push
```

## Why SQLite needed `render_as_batch=True`

You'll see this option set in `env.py`. SQLite's own `ALTER
TABLE` can only add columns — it can't drop, rename, or change a column's
type directly. Alembic's "batch mode" works around that by rebuilding the
table under the hood when a migration needs one of those operations, so you
can write normal-looking migrations without worrying about SQLite's
limitations. Adding new nullable columns (like the examples above) doesn't
actually need this, but it's there and ready for when you do something
trickier.

## Files added

```
alembic.ini                          -- config: points Alembic at arijit_songs.db
migrations/
  env.py                             -- wired to import Base from models.py,
                                          so autogenerate can see your schema
  script.py.mako                     -- template new migrations are generated from
  versions/
    0001_initial_schema.py           -- baseline: the schema as it exists today
```
