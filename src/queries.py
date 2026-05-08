import sqlite3
import pandas as pd


def get_connection(db_path="data/spotify.db"):
    return sqlite3.connect(db_path)


def streams_by_genre(db_path="data/spotify.db"):
    conn = get_connection(db_path)
    df = pd.read_sql_query("""
        SELECT genre,
               COUNT(*)                        AS track_count,
               ROUND(SUM(streams)/1e6, 2)      AS total_streams_m,
               ROUND(AVG(streams)/1e6, 4)      AS avg_streams_m,
               ROUND(AVG(danceability), 3)     AS avg_danceability,
               ROUND(AVG(energy), 3)           AS avg_energy,
               ROUND(AVG(valence), 3)          AS avg_valence,
               ROUND(AVG(tempo), 1)            AS avg_tempo
        FROM tracks
        GROUP BY genre
        ORDER BY total_streams_m DESC
    """, conn)
    conn.close()
    return df


def top_tracks(db_path="data/spotify.db", limit=20):
    conn = get_connection(db_path)
    df = pd.read_sql_query(f"""
        SELECT t.title, a.name AS artist, t.genre, t.mood,
               t.streams, t.saves, t.playlist_adds,
               t.danceability, t.energy, t.valence, t.tempo,
               t.release_date, t.explicit
        FROM tracks t
        JOIN artists a ON t.artist_id = a.artist_id
        ORDER BY t.streams DESC
        LIMIT {limit}
    """, conn)
    conn.close()
    return df


def audio_features_by_genre(db_path="data/spotify.db"):
    conn = get_connection(db_path)
    df = pd.read_sql_query("""
        SELECT genre,
               ROUND(AVG(danceability), 3)      AS danceability,
               ROUND(AVG(energy), 3)            AS energy,
               ROUND(AVG(valence), 3)           AS valence,
               ROUND(AVG(acousticness), 3)      AS acousticness,
               ROUND(AVG(instrumentalness), 3)  AS instrumentalness,
               ROUND(AVG(speechiness), 3)       AS speechiness,
               ROUND(AVG(tempo), 1)             AS tempo,
               ROUND(AVG(loudness), 2)          AS loudness
        FROM tracks
        GROUP BY genre
        ORDER BY genre
    """, conn)
    conn.close()
    return df


def mood_distribution(db_path="data/spotify.db"):
    conn = get_connection(db_path)
    df = pd.read_sql_query("""
        SELECT mood,
               COUNT(*)                    AS track_count,
               ROUND(SUM(streams)/1e6, 2) AS total_streams_m
        FROM tracks
        GROUP BY mood
        ORDER BY total_streams_m DESC
    """, conn)
    conn.close()
    return df


def release_trend(db_path="data/spotify.db"):
    conn = get_connection(db_path)
    df = pd.read_sql_query("""
        SELECT strftime('%Y', release_date) AS year,
               genre,
               COUNT(*)                    AS track_count,
               ROUND(SUM(streams)/1e6, 2) AS total_streams_m
        FROM tracks
        GROUP BY year, genre
        ORDER BY year, genre
    """, conn)
    conn.close()
    return df


def platform_stats(db_path="data/spotify.db"):
    conn = get_connection(db_path)
    df = pd.read_sql_query("""
        SELECT platform,
               COUNT(*)                        AS play_count,
               ROUND(AVG(completion_pct), 1)   AS avg_completion_pct
        FROM listening_history
        GROUP BY platform
        ORDER BY play_count DESC
    """, conn)
    conn.close()
    return df


def top_artists(db_path="data/spotify.db", limit=10):
    conn = get_connection(db_path)
    df = pd.read_sql_query(f"""
        SELECT a.name, a.genre, a.country,
               a.monthly_listeners, a.followers,
               COUNT(t.track_id)              AS track_count,
               ROUND(SUM(t.streams)/1e6, 2)  AS total_streams_m
        FROM artists a
        JOIN tracks t ON a.artist_id = t.artist_id
        GROUP BY a.artist_id
        ORDER BY total_streams_m DESC
        LIMIT {limit}
    """, conn)
    conn.close()
    return df


def kpi_summary(db_path="data/spotify.db"):
    conn = get_connection(db_path)
    cur  = conn.cursor()
    total_tracks   = cur.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
    total_streams  = cur.execute("SELECT SUM(streams) FROM tracks").fetchone()[0]
    total_artists  = cur.execute("SELECT COUNT(*) FROM artists").fetchone()[0]
    avg_dance      = cur.execute("SELECT ROUND(AVG(danceability),3) FROM tracks").fetchone()[0]
    avg_energy     = cur.execute("SELECT ROUND(AVG(energy),3) FROM tracks").fetchone()[0]
    explicit_pct   = cur.execute("SELECT ROUND(AVG(explicit)*100,1) FROM tracks").fetchone()[0]
    conn.close()
    return {
        "total_tracks":   total_tracks,
        "total_streams_b": round(total_streams / 1e9, 3),
        "total_artists":  total_artists,
        "avg_danceability": avg_dance,
        "avg_energy":     avg_energy,
        "explicit_pct":   explicit_pct,
    }
