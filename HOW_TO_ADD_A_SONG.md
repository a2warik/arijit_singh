# How to add a song

There are two ways, both going through `add_song.py` — so a song added either way ends up structured identically, with no duplicate composer/lyricist/vocalist rows.

## 1. Interactive (easiest)

From the folder with your project files:

```
python add_song.py
```

It will prompt you for each field:

```
Song title: Tere Bina
Film name: Example Film
Film year: 2025
Composer(s): Pritam
Lyricist(s): Amitabh Bhattacharya
Actor(s) picturised on, if any (leave blank if none): Ranbir Kapoor
Co-vocalist(s), if any (leave blank if solo): Shreya Ghoshal
```

- Separate multiple names with commas (e.g. `Amitabh Bhattacharya, Gulzar`).
- Arijit Singh is added as lead vocalist automatically — don't type his name.
- If "Pritam" or "Amitabh Bhattacharya" already exist in the database, their existing row is reused, not duplicated.
- If a song with that exact title + film is already in the database, it's skipped with a message instead of creating a duplicate.

## 2. From your own script (for bulk adds)

```python
from models import get_session
from add_song import add_song

session = get_session()

add_song(
    session,
    title="Tere Bina",
    film_name="Example Film",
    film_year=2025,
    composers=["Pritam"],
    lyricists=["Amitabh Bhattacharya"],
    vocalists=["Shreya Ghoshal"],   # co-vocalists only; Arijit is added for you
    actors=["Ranbir Kapoor"],       # optional — who it's picturised on
)

session.close()
```

Loop this over a list of tuples to add many songs at once — it's exactly what `seed_data.py` does with the original 70.

## After adding songs — update the website

`index.html` doesn't read `archive_data.json` live — its data is baked directly into the page (as a JS constant) so the site opens instantly with no local server needed. That means two steps, not one, after adding a song:

```
python export_json.py   # refreshes archive_data.json from the database
python build_site.py    # bakes that data into a fresh index.html
```

`build_site.py` reads `index_template.html` (the page's design, with a placeholder where the data goes) and `archive_data.json` (the latest data), and writes out `index.html`. If you only run `export_json.py` and skip `build_site.py`, the JSON file updates but the site itself won't change — that's the exact issue you'll hit if you forget this step.

If you ever want to redesign the page itself, edit `index_template.html`, not `index.html` directly — otherwise your next `build_site.py` run will overwrite your changes.
