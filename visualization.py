import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('listening_history.sqlite')

query = "SELECT * FROM listening_history"
df = pd.read_sql_query(query, conn)

df['played_at'] = pd.to_datetime(df['played_at'])

daily_listen_count = df.groupby(df['played_at'].dt.date).size()

genres_count = df['genres'].str.split(',').explode().str.strip().value_counts().head(25)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

daily_listen_count.plot(kind='bar', ax=ax1, color='b', alpha=0.6)
ax1.set_title('Daily Listening Counts')
ax1.tick_params(axis='x', rotation=0)
ax1.set_xlabel('')
ax1.set_ylabel('') 

genres_count.plot(kind='bar', ax=ax2, color='g', alpha=0.6)
ax2.set_title('Genre Distribution')
ax2.tick_params(axis='x', rotation=90)
max_listen_count = max(genres_count)
ax2.set_yticks(range(0, max_listen_count + 1, 1))
ax2.set_yticklabels(range(0, max_listen_count + 1, 1))
ax2.set_xlabel('')
ax2.set_ylabel('') 

fig.tight_layout()
plt.show()

conn.close()
