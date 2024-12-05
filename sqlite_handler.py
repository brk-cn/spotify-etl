import sqlite3
import pandas as pd

class SQLiteHandler:
    def __init__(self, db_path):
        self.db_path = db_path

    def save_df_to_db(self, df, table_name="listening_history"):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = f"""
              CREATE TABLE IF NOT EXISTS {table_name} (
                played_at VARCHAR(255),
                song_name VARCHAR(255),
                artist_name VARCHAR(255),
                genres TEXT,
                 PRIMARY KEY (played_at)
              )
            """
            cursor.execute(query)

            df.to_sql(table_name, conn, index=False, if_exists="append")

            conn.commit()

        except sqlite3.OperationalError as e:
            print(f"Error: {e}")

        finally:
            conn.close() if conn else None

    def read_data(self, table_name="listening_history"):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            sql_query = f"SELECT * FROM {table_name}"
            cursor.execute(sql_query)
            data = cursor.fetchall()

        except sqlite3.OperationalError as e:
            print(f"Error: {e}")
            data = []

        finally:
            conn.close() if conn else None

        return pd.DataFrame(
            data, columns=["played_at", "song_name", "artist_name", "genres"]
        )
