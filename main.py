from flask import Flask, redirect, request, session
from dotenv import load_dotenv
import urllib.parse
import requests
import base64
import time
import os

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8znxec]/'

@app.route("/")
def index():
    return "<a href='/login'>Login</a>"


@app.route("/login")
def login():
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": "user-read-private user-read-email user-read-recently-played",
        "redirect_uri": redirect_uri,
    }
    redirect_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(redirect_url)


@app.route("/callback")
def callback():
    code = request.args.get("code")

    if code:
        token_url = "https://accounts.spotify.com/api/token"
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic "
            + base64.b64encode((client_id + ":" + client_secret).encode()).decode(),
        }
        response = requests.post(token_url, data=payload, headers=headers)
        if response.status_code == 200:
            access_token = response.json()["access_token"]
            session["access_token"] = access_token
            return redirect("/tracks")


@app.route("/tracks")
def get_track_list():
    if "access_token" not in session:
        return redirect("/login")
    
    today_start_timestamp = int(time.mktime(time.localtime())) 

    api_base_url = "https://api.spotify.com/v1/"
    params = {
        "limit": 50,
        "after": today_start_timestamp*1000
    }
    headers = {"Authorization": f"Bearer {session["access_token"]}"}

    response = requests.get(f"{api_base_url}me/player/recently-played", headers=headers)
    if response.status_code == 200:
        track_list = response.json()
        return track_list
    else:
        return response.json()



if __name__ == "__main__":
    app.run(debug=True, port=8080)
