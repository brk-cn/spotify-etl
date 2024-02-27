from flask import Flask, redirect, request, session, jsonify
from datetime import datetime, timedelta
from unidecode import unidecode
from dotenv import load_dotenv
import urllib.parse
import requests
import base64
import uuid
import os
from db import create_table, save_data

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())


@app.route("/")
def index():
    return "<a href='/login'>Spotify ile Giriş Yap</a>"


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
    error = request.args.get("error")

    if error:
        return jsonify({"error": error})

    if code:
        token_url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic "
            + base64.b64encode((client_id + ":" + client_secret).encode()).decode(),
        }

        response = requests.post(token_url, data=data, headers=headers)

        if response.status_code == 200:
            session["access_token"] = response.json()["access_token"]
            session["refresh_token"] = response.json()["refresh_token"]
            session["expires_at"] = (
                datetime.now().timestamp() + response.json()["expires_in"]
            )

            return redirect("/tracks")


@app.route("/refresh-token")
def refresh_token():
    if "access_token" not in session:
        return redirect("/login")

    if datetime.now().timestamp() > session["expires_at"]:
        token_url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": session.get("refresh_token"),
            "client_id": client_id,
            "client_secret": client_secret,
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            session["access_token"] = response.json()["access_token"]
            session["refresh_token"] = response.json()["refresh_token"]
            session["expires_at"] = (
                datetime.now().timestamp() + response.json()["expires_in"]
            )

            return redirect("/tracks")


def get_genres(artist_id):
    api_base_url = "https://api.spotify.com/v1"
    headers = {"Authorization": f"Bearer {session.get('access_token')}"}

    response = requests.get(f"{api_base_url}/artists/{artist_id}", headers=headers)
    if response.status_code == 200:
        artist_data = response.json()
        genres = artist_data.get("genres", [])
        return genres
    else:
        return []


@app.route("/tracks")
def get_track_list():
    if "access_token" not in session:
        return redirect("/login")

    if datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")

    api_base_url = "https://api.spotify.com/v1"
    params = {"limit": 50, "before": int((datetime.now().timestamp())) * 1000}
    headers = {"Authorization": f"Bearer {session['access_token']}"}

    response = requests.get(
        f"{api_base_url}/me/player/recently-played", headers=headers, params=params
    )

    if response.status_code == 200:
        tracks = response.json()
        final_track_list = []
        today = datetime.now().strftime("%d-%m-%Y")
        for item in tracks["items"]:
            played_at = datetime.strptime(
                item["played_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).strftime("%d-%m-%Y")
            if played_at == today:
                artist_id = item["track"]["artists"][0]["id"]
                genres = get_genres(artist_id)
                track_info = {
                    "song_name": unidecode(item["track"]["name"]),
                    "artist_name": unidecode(item["track"]["artists"][0]["name"]),
                    "played_at": played_at,
                    "genres": genres,
                }
                save_data(
                    played_at,
                    unidecode(item["track"]["artists"][0]["name"]),
                    unidecode(item["track"]["name"]),
                    ", ".join(get_genres(item["track"]["artists"][0]["id"])),
                )
                final_track_list.append(track_info)

        return final_track_list
    else:
        return response.json()


if __name__ == "__main__":
    create_table()
    app.run(debug=True, host="0.0.0.0", port=8080)
