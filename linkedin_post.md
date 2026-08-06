I built a database for a singer. Turns out it taught me more about databases than any tutorial did.

A few weeks ago I wanted a simple thing: a searchable archive of every Bollywood song sung by Arijit Singh, because as a fan I was tired of memorizing "who wrote what" and "which year was that song from."

What I ended up building was, quietly, my first real lesson in database design.

I started with the obvious approach — one big table. Song, film, year, composer, lyricist, all in one row, over and over. It worked. It also repeated "Pritam" or "Amitabh Bhattacharya" dozens of times, which is exactly the smell that tells you something's wrong.

So I rebuilt it properly:

→ Separate tables for Films, Composers, Lyricists, Vocalists, and Actors — each name stored exactly once
→ A Songs table that references them by ID instead of retyping text
→ Many-to-many relationships (a song can have multiple singers; a composer scores many songs) modeled with SQLAlchemy
→ A tiny "association object" to capture something a plain link table couldn't: not just who sang a song, but whether they were the lead voice or a featured guest

The payoff was immediate and genuinely satisfying: click "Irshad Kamil" and instantly see every song he wrote for Arijit. Click "Ranbir Kapoor" and see every track picturised on him. No manual joins, no duplicate data, no spreadsheet chaos — just relationships doing what they're designed to do.

Along the way I also:
— Scraped and cleaned 400+ additional song credits from Wikipedia (rowspans in HTML tables are sneakier than they look)
— Added Alembic for schema migrations, so I can evolve the database — add YouTube links, artist photos — without ever tearing it down and rebuilding from scratch
— Shipped it as a static site, hosted free on Vercel, source on GitHub under GNU license

The live site: arijit-singh-beta.vercel.app

I'm not a database engineer. I'm a fan who wanted a better way to find a song. But somewhere between "let's just use a spreadsheet" and "wait, what's a foreign key," I actually understood *why* relational databases are built the way they are — not as theory, but because I hit the exact problem they solve.

If you've ever thought database design sounded dry or abstract: it isn't, once it's solving a problem you actually care about. Mine happened to be Arijit Singh's discography. Yours could be anything.

#DatabaseDesign #SQLAlchemy #Python #SoftwareEngineering #LearningInPublic #SideProject #ArijitSingh
