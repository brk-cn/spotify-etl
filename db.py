import sqlite3


def create_table():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS listening_history (id INTEGER PRIMARY KEY, played_at TEXT,song_name TEXT,artist_name TEXT,genres TEXT);",
    )
    conn.commit()
    conn.close()


def save_data(played_at, artist_name, song_name, genres):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO listening_history (played_at, artist_name, song_name, genres) VALUES (?, ?, ?, ?)",
        (played_at, artist_name, song_name, genres),
    )
    conn.commit()
    conn.close()
