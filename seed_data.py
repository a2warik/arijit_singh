"""
seed_data.py
------------
Builds arijit_songs.db from scratch and populates it with a curated,
best-effort collection of Arijit Singh's Bollywood songs.

Every row goes through add_song(), the exact same function used by the
interactive "add a song" tool -- so seeding the database and adding to
it later are the same code path, and Composer/Lyricist/Vocalist rows
are automatically reused instead of duplicated (e.g. "Pritam" is
created once the first time he appears, then just linked to every
other song after that).

Run:  python seed_data.py

Requires alembic.ini and migrations/ to be present in this same folder
(they define the schema this script builds).
"""

import os
import subprocess
from models import get_session
from add_song import add_song

# ---------------------------------------------------------------------------
# (title, film, year, "composer(s)", "lyricist(s)", "co-vocalist(s)", "actor(s) picturised on")
# Composer/lyricist/co-vocalist/actor fields are comma-separated where a
# song credits more than one. Arijit Singh is added as lead vocalist
# automatically by add_song() and does not need to be listed here.
# ---------------------------------------------------------------------------
SONGS = [
    ("Phir Mohabbat", "Murder 2", 2011, "Mithoon", "Sayeed Quadri", "", "Emraan Hashmi"),
    ("Tum Hi Ho", "Aashiqui 2", 2013, "Mithoon", "Mithoon", "", "Aditya Roy Kapur"),
    ("Sunn Raha Hai Na Tu (Male)", "Aashiqui 2", 2013, "Mithoon", "Mithoon", "", "Aditya Roy Kapur"),
    ("Chahun Main Ya Naa", "Aashiqui 2", 2013, "Jeet Gannguli", "Mithoon", "Palak Muchhal", "Aditya Roy Kapur, Shraddha Kapoor"),
    ("Tum Hi Ho Bandhu", "Cocktail", 2012, "Pritam", "Irshad Kamil", "Shefali Alvares", "Saif Ali Khan"),
    ("Phir Le Aya Dil", "Barfi!", 2012, "Pritam", "Sayeed Quadri", "", "Ranbir Kapoor"),
    ("Ilahi", "Yeh Jawaani Hai Deewani", 2013, "Pritam", "Irshad Kamil", "", "Ranbir Kapoor"),
    ("Kabira (Encore)", "Yeh Jawaani Hai Deewani", 2013, "Pritam", "Amitabh Bhattacharya", "Harshdeep Kaur", "Ranbir Kapoor, Deepika Padukone"),
    ("Raabta", "Agent Vinod", 2012, "Pritam", "Kausar Munir", "", "Saif Ali Khan, Kareena Kapoor"),
    ("Manwa Laage", "Happy New Year", 2014, "Vishal-Shekhar", "Irshad Kamil", "Shreya Ghoshal", "Shah Rukh Khan, Deepika Padukone"),
    ("Muskurane", "Citylights", 2014, "Jeet Gannguli", "Rashmi Singh", "", "Rajkummar Rao"),
    ("Suno Na Sangemarmar", "Youngistaan", 2014, "Jeet Gannguli", "Manoj Yadav", "", "Jackky Bhagnani"),
    ("Gerua", "Dilwale", 2015, "Pritam", "Amitabh Bhattacharya", "Antara Mitra", "Shah Rukh Khan, Kajol"),
    ("Janam Janam", "Dilwale", 2015, "Pritam", "Amitabh Bhattacharya", "Antara Mitra", "Shah Rukh Khan, Kajol"),
    ("Manma Emotion Jaage", "Dilwale", 2015, "Pritam", "Amitabh Bhattacharya", "Shreya Ghoshal, Nakash Aziz, Kanika Kapoor", "Varun Dhawan, Kriti Sanon"),
    ("Agar Tum Saath Ho", "Tamasha", 2015, "A. R. Rahman", "Irshad Kamil", "Alka Yagnik", "Ranbir Kapoor, Deepika Padukone"),
    ("Ae Dil Hai Mushkil", "Ae Dil Hai Mushkil", 2016, "Pritam", "Amitabh Bhattacharya", "", "Ranbir Kapoor"),
    ("Channa Mereya", "Ae Dil Hai Mushkil", 2016, "Pritam", "Amitabh Bhattacharya", "", "Ranbir Kapoor"),
    ("The Breakup Song", "Ae Dil Hai Mushkil", 2016, "Pritam", "Amitabh Bhattacharya", "Badshah, Jonita Gandhi, Nakash Aziz", "Ranbir Kapoor, Anushka Sharma"),
    ("Ae Watan", "Raazi", 2018, "Shankar-Ehsaan-Loy", "Gulzar", "", "Alia Bhatt"),
    ("Kalank (Title Track)", "Kalank", 2019, "Pritam", "Amitabh Bhattacharya", "", "Madhuri Dixit, Sanjay Dutt"),
    ("First Class", "Kalank", 2019, "Pritam", "Amitabh Bhattacharya", "Neeti Mohan", "Varun Dhawan, Kiara Advani"),
    ("Tabaah Ho Gaye", "Kalank", 2019, "Pritam", "Amitabh Bhattacharya", "", "Sanjay Dutt, Alia Bhatt"),
    ("Ghungroo", "War", 2019, "Vishal-Shekhar", "Kumaar", "Shilpa Rao", "Hrithik Roshan, Tiger Shroff"),
    ("Naina", "Dangal", 2016, "Pritam", "Amitabh Bhattacharya", "", "Aamir Khan"),
    ("Roke Na Ruke Naina", "Badrinath Ki Dulhania", 2017, "Amaal Mallik", "Kumaar", "Neha Kakkar", "Varun Dhawan, Alia Bhatt"),
    ("Zaalima", "Raees", 2017, "JAM8", "Amitabh Bhattacharya", "Harshdeep Kaur", "Shah Rukh Khan, Mahira Khan"),
    ("Enna Sona", "OK Jaanu", 2017, "A. R. Rahman", "Gulzar", "", "Shraddha Kapoor, Aditya Roy Kapur"),
    ("Humdard", "Ek Villain", 2014, "Mithoon", "Mithoon", "", "Shraddha Kapoor, Siddharth Malhotra"),
    ("Tera Yaar Hoon Main", "Sonu Ke Titu Ki Sweety", 2018, "Rochak Kohli", "Kumaar", "Rochak Kohli", "Kartik Aaryan, Sunny Singh"),
    ("Dil Jaaniye", "Sonu Ke Titu Ki Sweety", 2018, "Payal Dev", "Kumaar", "Neeti Mohan", "Kartik Aaryan, Nushrat Bharucha"),
    ("Khairiyat", "Chhichhore", 2019, "Pritam", "Amitabh Bhattacharya", "", "Sushant Singh Rajput, Shraddha Kapoor"),
    ("Kesariya", "Brahmastra", 2022, "Pritam", "Amitabh Bhattacharya", "", "Ranbir Kapoor, Alia Bhatt"),
    ("Deva Deva", "Brahmastra", 2022, "Pritam", "Amitabh Bhattacharya", "Jonita Gandhi", "Ranbir Kapoor"),
    ("Apna Bana Le", "Bhediya", 2022, "Sachin-Jigar", "Amitabh Bhattacharya", "", "Varun Dhawan, Kriti Sanon"),
    ("Dil Bechara (Title Track)", "Dil Bechara", 2020, "A. R. Rahman", "Amitabh Bhattacharya", "", "Sushant Singh Rajput"),
    ("Pachtaoge", "Genius", 2018, "B Praak", "Manoj Muntashir", "", "Vicky Kaushal, Nora Fatehi"),
    ("Shayad", "Love Aaj Kal", 2020, "Pritam", "Irshad Kamil", "", "Kartik Aaryan, Sara Ali Khan"),
    ("Phir Bhi Tumko Chaahunga", "Half Girlfriend", 2017, "Mithoon", "Mithoon", "", "Arjun Kapoor, Shraddha Kapoor"),
    ("Sanam Re (Title Track)", "Sanam Re", 2016, "Mithoon", "Mithoon", "", "Pulkit Samrat, Yami Gautam"),
    ("Tujhe Kitna Chahne Lage", "Kabir Singh", 2019, "Mithoon", "Irshad Kamil", "", "Shahid Kapoor, Kiara Advani"),
    ("Ve Maahi", "Kesari", 2019, "Arko", "Irshad Kamil", "Asees Kaur", "Akshay Kumar, Parineeti Chopra"),
    ("Judaai", "Badlapur", 2015, "Sachin-Jigar", "Sayeed Quadri", "", "Varun Dhawan"),
    ("Laal Ishq", "Goliyon Ki Raasleela Ram-Leela", 2013, "Sanjay Leela Bhansali", "Siddharth-Garima", "", "Ranveer Singh, Deepika Padukone"),
    ("Sawan Aaya Hai", "Creature 3D", 2014, "Mithoon", "Mithoon", "Aakanksha Sharma", "Bipasha Basu, Imran Abbas"),
    ("Bolna", "Kapoor & Sons", 2016, "Tanishk Bagchi", "Amitabh Bhattacharya", "Asees Kaur", "Sidharth Malhotra, Alia Bhatt"),
    ("Sooraj Dooba Hai", "Roy", 2015, "Amaal Mallik", "Kumaar", "Aditi Singh Sharma", "Ranbir Kapoor, Jacqueline Fernandez"),
    ("Chal Wahan Jaate Hain", "Non-Film Single", 2016, "Jeet Gannguli", "Kumaar", "", "Tiger Shroff"),
    ("Tera Chehra", "Sanam Teri Kasam", 2016, "Himesh Reshammiya", "Manoj Muntashir", "Palak Muchhal", "Harshvardhan Rane, Mawra Hocane"),
    ("Kabhi Jo Baadal Barse", "Jackpot", 2013, "Mithoon", "Sayeed Quadri", "", "Sachiin Joshi"),
    ("O Saathi", "Baaghi 2", 2018, "Arko", "Kumaar", "", "Tiger Shroff, Disha Patani"),
    ("Nashe Si Chadh Gayi", "Befikre", 2016, "Vishal-Shekhar", "Jaideep Sahni", "", "Ranveer Singh, Vaani Kapoor"),
    ("Hawayein", "Jab Harry Met Sejal", 2017, "Pritam", "Irshad Kamil", "", "Shah Rukh Khan, Anushka Sharma"),
    ("Yeh Fitoor Mera", "Fitoor", 2016, "Amit Trivedi", "Amitabh Bhattacharya", "", "Aditya Roy Kapur, Katrina Kaif"),
    ("Chal Ghar Chalen", "Malang", 2020, "Mithoon", "Manoj Muntashir", "", "Aditya Roy Kapur"),
    ("Rait Zara Si", "Atrangi Re", 2021, "A. R. Rahman", "A. M. Turaz", "Shreya Ghoshal", "Akshay Kumar"),
    ("Chaka Chak", "Atrangi Re", 2021, "A. R. Rahman", "A. M. Turaz", "", "Sara Ali Khan"),
    ("Mere Sohneya", "Kabir Singh", 2019, "Sachet-Parampara", "Irshad Kamil", "Asees Kaur", "Shahid Kapoor, Kiara Advani"),
    ("Jhoome Jo Pathaan", "Pathaan", 2023, "Vishal-Shekhar", "Kumaar", "Sukriti Kakar, Vishal Dadlani, Caralisa Monteiro", "Shah Rukh Khan, Deepika Padukone"),
    ("Tum Kya Mile", "Rocky Aur Rani Kii Prem Kahaani", 2023, "Pritam", "Amitabh Bhattacharya", "Shreya Ghoshal", "Ranveer Singh, Alia Bhatt"),
    ("What Jhumka", "Rocky Aur Rani Kii Prem Kahaani", 2023, "Pritam", "Amitabh Bhattacharya", "Jonita Gandhi", "Ranveer Singh, Alia Bhatt"),
    ("Ve Kamleya", "Rocky Aur Rani Kii Prem Kahaani", 2023, "Pritam", "Amitabh Bhattacharya", "Jonita Gandhi, Shreya Ghoshal", "Ranveer Singh, Alia Bhatt"),
    ("Dhoop", "Rocky Aur Rani Kii Prem Kahaani", 2023, "Pritam", "Amitabh Bhattacharya", "", "Ranveer Singh, Alia Bhatt"),
    ("Satranga", "Animal", 2023, "Shreyas Puranik", "Manoj Muntashir Shukla", "", "Ranbir Kapoor, Tripti Dimri"),
    ("Papa Meri Jaan", "Animal", 2023, "Harshavardhan Rameshwar", "Manoj Muntashir Shukla", "", "Ranbir Kapoor"),
    ("Chaleya", "Jawan", 2023, "Anirudh Ravichander", "Irshad Kamil", "Shilpa Rao", "Shah Rukh Khan, Nayanthara"),
    ("Aayi Nai", "Jawan", 2023, "Anirudh Ravichander", "Kumaar", "", "Shah Rukh Khan"),
    ("Aayat", "Bajirao Mastani", 2015, "Sanjay Leela Bhansali", "Siddharth-Garima", "", "Ranveer Singh, Deepika Padukone"),
    ("O Bedardeya", "Tu Jhoothi Main Makkaar", 2023, "Pritam", "Amitabh Bhattacharya", "", "Ranbir Kapoor, Shraddha Kapoor"),
    ("Heeriye", "Non-Film Single", 2023, "Jasleen Royal, Arijit Singh", "Jasleen Royal", "", ""),
]


def build_database():
    """
    Wipes arijit_songs.db and rebuilds it from scratch, purely for local
    development / re-seeding a throwaway copy. The schema is now built
    by running Alembic's migrations (not Base.metadata.create_all), so
    the freshly-built file ends up with an accurate alembic_version
    table -- as if it had been migrated up from nothing, because it
    was.

    IMPORTANT: only run this on a database you're OK losing. Never run
    it against your real production database -- that's what
    add_song.py / import_from_csv.py are for.
    """
    if os.path.exists("arijit_songs.db"):
        os.remove("arijit_songs.db")

    print("Building schema via `alembic upgrade head` ...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)

    session = get_session()

    for title, film, year, composers, lyricists, co_vocalists, actors in SONGS:
        add_song(
            session,
            title=title,
            film_name=film,
            film_year=year,
            composers=composers.split(","),
            lyricists=lyricists.split(","),
            vocalists=co_vocalists.split(",") if co_vocalists else [],
            actors=actors.split(",") if actors else [],
        )

    from models import Song, Composer, Lyricist, Vocalist, Actor, Film
    print("\n--- Build complete ---")
    print(f"Songs:      {session.query(Song).count()}")
    print(f"Films:      {session.query(Film).count()}")
    print(f"Composers:  {session.query(Composer).count()}")
    print(f"Lyricists:  {session.query(Lyricist).count()}")
    print(f"Vocalists:  {session.query(Vocalist).count()}")
    print(f"Actors:     {session.query(Actor).count()}")
    session.close()


if __name__ == "__main__":
    build_database()
