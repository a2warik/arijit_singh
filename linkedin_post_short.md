I built a searchable database of every Bollywood song sung by Arijit Singh — and it taught me database design better than any tutorial.

Started with one flat table: song, film, composer, lyricist, all repeated row after row. Rebuilt it properly instead — separate tables for Films, Composers, Lyricists, Vocalists, and Actors, each name stored once, linked by relationships (SQLAlchemy) instead of retyped text.

Now I can click "Irshad Kamil" and see every song he wrote for Arijit. Click "Ranbir Kapoor" and see every track picturised on him. No duplicates, no manual joins — just relationships doing their job.

Along the way: scraped 400+ more credits from Wikipedia, added Alembic for schema migrations, and shipped it as a free static site on Vercel, source on GitHub.

Live site: arijit-singh-beta.vercel.app

I'm not a database engineer — just a fan who wanted a better way to find a song, and ended up actually understanding *why* relational databases work the way they do.

#DatabaseDesign #SQLAlchemy #Python #SideProject #ArijitSingh
