import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('listening_history.sqlite')

query = "SELECT * FROM listening_history"
df = pd.read_sql_query(query, conn)

df['played_at'] = pd.to_datetime(df['played_at'])

daily_listen_count = df.groupby(df['played_at'].dt.date).size()
daily_listen_count.plot(kind='bar', figsize=(10, 6))
plt.title('')
plt.xlabel('')
plt.ylabel('')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

genres_count = df['genres'].str.split(',').explode().str.strip().value_counts()
genres_count.plot(kind='bar', figsize=(10, 6))
plt.title('')
plt.xlabel('')
plt.ylabel('')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

conn.close()
