import sqlite3, random, os
from datetime import datetime, timedelta
import numpy as np

random.seed(42)
np.random.seed(42)

GENRES = ["Pop","Hip-Hop","Rock","Electronic","R&B","Latin","Country","Jazz","Classical","Metal"]
ARTISTS = {
    "Pop":        ["Aria Nova","Stella Vance","Max Holloway","Luna Pierce","Zoe Hartley"],
    "Hip-Hop":    ["K-Raze","Dex Malone","Yung Cipher","Nova Blaze","Tre Fontaine"],
    "Rock":       ["Iron Veil","The Cracked Bells","Static Wolves","Ember Road","Hollow Crown"],
    "Electronic": ["Synthex","Neon Drift","Pulse Array","Circuit Ghost","Wavefront"],
    "R&B":        ["Jade Monroe","Elise Carter","Marcus Soul","Tia Renee","Devon Skye"],
    "Latin":      ["Carlos Vega","Sofia Reyes","Mateo Cruz","Valentina Rios","Diego Fuentes"],
    "Country":    ["Blake Rivers","Cassidy Lane","Travis Cole","Savannah Mae","Colt Briggs"],
    "Jazz":       ["Miles Ashford","Clara Benson","Ray Dupont","Nina Holloway","Oscar Trent"],
    "Classical":  ["Vienna Ensemble","Prague Quartet","Elara Strings","Nordic Philharmonic","Solaris Chamber"],
    "Metal":      ["Void Hammer","Serpent Throne","Blackened Sky","Iron Requiem","Chaos Engine"],
}
TRACK_TEMPLATES = {
    "Pop":        ["Neon Lights","Heartbeat","Summer Fade","Golden Hour","Electric Feel","Midnight Run","Chasing Stars","Breathe Again"],
    "Hip-Hop":    ["Street Anthem","No Cap","Grind Season","Flex Mode","Real Talk","Block Party","Hustle Hard","Crown Up"],
    "Rock":       ["Broken Glass","Fade to Static","Last Stand","Burning Down","Stone Cold","Reckless","Overdrive","Shattered"],
    "Electronic": ["Pulse Wave","Neon Grid","Hyperdrive","Frequency","Voltage Drop","Laser Rain","Synth City","Data Stream"],
    "R&B":        ["Slow Burn","All Night","Velvet Touch","Soulfire","Midnight Glow","Tender","Gravity","Silk Road"],
    "Latin":      ["Fuego","Ritmo","Corazon","Bailar","Cielo","Amor Eterno","La Noche","Vibra"],
    "Country":    ["Dirt Road","Whiskey Nights","Hometown","Tailgate","Boots & Dust","Open Fields","Porch Light","River Bend"],
    "Jazz":       ["Blue Smoke","Late Session","Velvet Keys","Midnight Sax","Swing Low","Ivory Dreams","Cool Breeze","Ember Jazz"],
    "Classical":  ["Opus in D","Nocturne No.3","Allegro Vivace","Sonata in G","Prelude","Adagio","Fugue in C","Concerto No.1"],
    "Metal":      ["Wrath of Iron","Eternal Darkness","Skull Crusher","Inferno","Death March","Chaos Rising","Blood Moon","Obliterate"],
}
MOOD_BY_GENRE = {
    "Pop":        ["Happy","Uplifting","Energetic","Romantic"],
    "Hip-Hop":    ["Energetic","Angry","Happy","Uplifting"],
    "Rock":       ["Energetic","Angry","Melancholic","Uplifting"],
    "Electronic": ["Energetic","Happy","Calm","Uplifting"],
    "R&B":        ["Romantic","Sad","Calm","Melancholic"],
    "Latin":      ["Happy","Energetic","Romantic","Uplifting"],
    "Country":    ["Sad","Happy","Melancholic","Calm"],
    "Jazz":       ["Calm","Melancholic","Romantic","Sad"],
    "Classical":  ["Calm","Melancholic","Uplifting","Sad"],
    "Metal":      ["Angry","Energetic","Melancholic","Uplifting"],
}

def _audio_features(genre):
    profiles = {
        "Pop":        dict(danceability=(0.60,0.90),energy=(0.55,0.85),valence=(0.45,0.85),tempo=(100,135),acousticness=(0.02,0.30),instrumentalness=(0.00,0.05),speechiness=(0.03,0.12),loudness=(-8,-3)),
        "Hip-Hop":    dict(danceability=(0.65,0.92),energy=(0.55,0.88),valence=(0.30,0.75),tempo=(75,115),acousticness=(0.02,0.25),instrumentalness=(0.00,0.08),speechiness=(0.10,0.40),loudness=(-7,-2)),
        "Rock":       dict(danceability=(0.35,0.70),energy=(0.65,0.97),valence=(0.25,0.70),tempo=(110,160),acousticness=(0.01,0.20),instrumentalness=(0.00,0.15),speechiness=(0.03,0.08),loudness=(-7,-2)),
        "Electronic": dict(danceability=(0.60,0.95),energy=(0.65,0.97),valence=(0.30,0.80),tempo=(120,145),acousticness=(0.00,0.10),instrumentalness=(0.30,0.90),speechiness=(0.03,0.08),loudness=(-8,-3)),
        "R&B":        dict(danceability=(0.55,0.88),energy=(0.35,0.72),valence=(0.30,0.75),tempo=(70,110),acousticness=(0.10,0.50),instrumentalness=(0.00,0.05),speechiness=(0.03,0.12),loudness=(-10,-4)),
        "Latin":      dict(danceability=(0.65,0.95),energy=(0.55,0.90),valence=(0.50,0.90),tempo=(90,130),acousticness=(0.05,0.35),instrumentalness=(0.00,0.05),speechiness=(0.04,0.12),loudness=(-8,-3)),
        "Country":    dict(danceability=(0.40,0.75),energy=(0.40,0.80),valence=(0.35,0.80),tempo=(85,130),acousticness=(0.20,0.70),instrumentalness=(0.00,0.05),speechiness=(0.03,0.08),loudness=(-10,-4)),
        "Jazz":       dict(danceability=(0.30,0.70),energy=(0.20,0.65),valence=(0.25,0.75),tempo=(70,130),acousticness=(0.40,0.95),instrumentalness=(0.10,0.70),speechiness=(0.03,0.06),loudness=(-15,-6)),
        "Classical":  dict(danceability=(0.15,0.50),energy=(0.10,0.60),valence=(0.10,0.70),tempo=(60,140),acousticness=(0.70,0.99),instrumentalness=(0.70,0.99),speechiness=(0.03,0.05),loudness=(-20,-8)),
        "Metal":      dict(danceability=(0.25,0.55),energy=(0.80,0.99),valence=(0.10,0.45),tempo=(130,200),acousticness=(0.00,0.08),instrumentalness=(0.00,0.20),speechiness=(0.03,0.10),loudness=(-6,-1)),
    }
    p = profiles[genre]
    return {k: round(random.uniform(*v),4) if k!="tempo" else round(random.uniform(*v),1) for k,v in p.items()}


def generate_database(db_path="data/spotify.db", n_tracks=2000):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS artists")
    cur.execute("""CREATE TABLE artists (
        artist_id INTEGER PRIMARY KEY, name TEXT NOT NULL, genre TEXT NOT NULL,
        monthly_listeners INTEGER NOT NULL, followers INTEGER NOT NULL, country TEXT NOT NULL)""")
    countries = ["US","UK","CA","AU","BR","MX","DE","FR","NG","KR"]
    artists_rows, aid = [], 1
    for genre, names in ARTISTS.items():
        for name in names:
            listeners = random.randint(50_000, 25_000_000)
            followers = int(listeners * random.uniform(0.3, 0.9))
            artists_rows.append((aid, name, genre, listeners, followers, random.choice(countries)))
            aid += 1
    cur.executemany("INSERT INTO artists VALUES (?,?,?,?,?,?)", artists_rows)

    cur.execute("DROP TABLE IF EXISTS tracks")
    cur.execute("""CREATE TABLE tracks (
        track_id INTEGER PRIMARY KEY, title TEXT NOT NULL, artist_id INTEGER NOT NULL,
        genre TEXT NOT NULL, mood TEXT NOT NULL, release_date TEXT NOT NULL,
        duration_ms INTEGER NOT NULL, explicit INTEGER NOT NULL,
        streams INTEGER NOT NULL, saves INTEGER NOT NULL, playlist_adds INTEGER NOT NULL,
        danceability REAL NOT NULL, energy REAL NOT NULL, valence REAL NOT NULL,
        tempo REAL NOT NULL, acousticness REAL NOT NULL, instrumentalness REAL NOT NULL,
        speechiness REAL NOT NULL, loudness REAL NOT NULL,
        FOREIGN KEY (artist_id) REFERENCES artists(artist_id))""")

    artist_by_genre = {}
    for row in artists_rows:
        artist_by_genre.setdefault(row[2], []).append(row[0])

    start = datetime(2018,1,1); end = datetime(2025,12,31)
    total_days = (end - start).days
    tracks_rows, used_titles = [], set()
    for tid in range(1, n_tracks+1):
        genre     = random.choice(GENRES)
        artist_id = random.choice(artist_by_genre[genre])
        base      = random.choice(TRACK_TEMPLATES[genre])
        title, s  = base, 2
        while title in used_titles:
            title = f"{base} {s}"; s += 1
        used_titles.add(title)
        mood         = random.choice(MOOD_BY_GENRE[genre])
        release_date = (start + timedelta(days=random.randint(0,total_days))).strftime("%Y-%m-%d")
        duration_ms  = random.randint(120_000, 360_000)
        explicit     = random.choices([0,1], weights=[65,35])[0]
        streams      = max(1000, min(int(np.random.lognormal(13.5,1.8)), 2_000_000_000))
        saves        = int(streams * random.uniform(0.02,0.18))
        playlist_adds= int(streams * random.uniform(0.01,0.12))
        af = _audio_features(genre)
        tracks_rows.append((tid,title,artist_id,genre,mood,release_date,duration_ms,explicit,
                            streams,saves,playlist_adds,af["danceability"],af["energy"],
                            af["valence"],af["tempo"],af["acousticness"],af["instrumentalness"],
                            af["speechiness"],af["loudness"]))
    cur.executemany("INSERT INTO tracks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tracks_rows)

    cur.execute("DROP TABLE IF EXISTS listening_history")
    cur.execute("""CREATE TABLE listening_history (
        entry_id INTEGER PRIMARY KEY, track_id INTEGER NOT NULL,
        listened_at TEXT NOT NULL, completion_pct REAL NOT NULL, platform TEXT NOT NULL,
        FOREIGN KEY (track_id) REFERENCES tracks(track_id))""")
    platforms = ["mobile","desktop","web","smart_tv","game_console"]
    pw = [50,25,15,6,4]
    history_rows = []
    track_ids = [r[0] for r in tracks_rows]
    for eid in range(1, min(n_tracks*3,6000)+1):
        tid = random.choice(track_ids)
        listened = (start + timedelta(days=random.randint(0,total_days),
                    seconds=random.randint(0,86399))).strftime("%Y-%m-%d %H:%M:%S")
        history_rows.append((eid,tid,listened,round(random.betavariate(5,2)*100,1),
                             random.choices(platforms,weights=pw)[0]))
    cur.executemany("INSERT INTO listening_history VALUES (?,?,?,?,?)", history_rows)

    conn.commit(); conn.close()
    return db_path


if __name__ == "__main__":
    print(f"Database generated: {generate_database()}")
