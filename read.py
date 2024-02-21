import sqlite3


def read_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listening_history")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        print("id:", row[0])
        print("played at:", row[1])
        print("song name:", row[2])
        print("artist name:", row[3])
        print("genres:", row[4])
        print("-" * 25)


read_database()
