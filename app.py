from selenium_login_handler import SeleniumLoginHandler
from spotify_api_handler import SpotifyAPIHandler
from sqlite_handler import SQLiteHandler
from flask import Flask, render_template, request
from dotenv import load_dotenv
import threading
import signal
import uuid
import os

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

spotify_api_handler = SpotifyAPIHandler(client_id, client_secret, redirect_uri)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return spotify_api_handler.login()

@app.route("/callback")
def callback():
    return spotify_api_handler.callback()

@app.route("/refresh-token")
def refresh_token():
    return spotify_api_handler.refresh_token()

@app.route("/tracks")
def get_tracks():
    df = spotify_api_handler.get_tracks()
    db_path = "listening_history.sqlite"
    sqlite_handler = SQLiteHandler(db_path)
    sqlite_handler.save_df_to_db(df)
    
    template = render_template("tracks.html", data=df.to_dict(orient="records"))
    threading.Timer(1.0, shutdown).start()
    return template

@app.route('/shutdown', methods=['POST'])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({ "success": True, "message": "Server is shutting down..." })

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(debug=False, host="0.0.0.0", port=8888)).start()
    selenium_handler = SeleniumLoginHandler()
    selenium_handler.login()
