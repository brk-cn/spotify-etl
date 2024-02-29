from flask import redirect, request, session, jsonify
from urllib.parse import urlencode
from datetime import datetime
from unidecode import unidecode
import pandas as pd
import requests
import base64


class SpotifyAPIHandler:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def login(self):
        auth_url = "https://accounts.spotify.com/authorize"
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "user-read-private user-read-email user-read-recently-played",
            "redirect_uri": self.redirect_uri,
        }
        redirect_url = f"{auth_url}?{urlencode(params)}"
        return redirect(redirect_url)

    def callback(self):
        error = request.args.get("error")
        if error:
            return jsonify({"error": error})

        code = request.args.get("code")
        if code:
            token_url = "https://accounts.spotify.com/api/token"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            }
            headers = {
                "content-type": "application/x-www-form-urlencoded",
                "Authorization": "Basic "
                + base64.b64encode(
                    (self.client_id + ":" + self.client_secret).encode()
                ).decode(),
            }

            response = requests.post(token_url, data=data, headers=headers)

            if response.status_code == 200:
                session["access_token"] = response.json()["access_token"]
                session["refresh_token"] = response.json()["refresh_token"]
                session["expires_at"] = (
                    datetime.now().timestamp() + response.json()["expires_in"]
                )
                return redirect("/tracks")
            else:
                return response.json()

    def refresh_token(self):
        if "access_token" not in session:
            return redirect("/login")

        if datetime.now().timestamp() > session["expires_at"]:
            token_url = "https://accounts.spotify.com/api/token"
            data = {
                "grant_type": "refresh_token",
                "refresh_token": session.get("refresh_token"),
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                session["access_token"] = response.json()["access_token"]
                session["refresh_token"] = response.json()["refresh_token"]
                session["expires_at"] = (
                    datetime.now().timestamp() + response.json()["expires_in"]
                )

                return redirect("/tracks")

    def get_tracks(self):
        if "access_token" not in session:
            return redirect("/login")

        if datetime.now().timestamp() > session["expires_at"]:
            return redirect("/refresh-token")

        api_base_url = "https://api.spotify.com/v1"
        today = datetime.now().strftime("%Y-%m-%d")

        params = {"limit": 50, "after": f"{today}T00:00:00Z"}
        headers = {"Authorization": f"Bearer {session['access_token']}"}

        response = requests.get(
            f"{api_base_url}/me/player/recently-played", headers=headers, params=params
        )

        if response.status_code == 200:
            tracks = response.json()

            df = pd.DataFrame(
                [
                    {
                        "played_at": item["played_at"],
                        "song_name": unidecode(item["track"]["name"]),
                        "artist_name": unidecode(item["track"]["artists"][0]["name"]),
                        "genres": self.get_genres(item["track"]["artists"][0]["id"]),
                    }
                    for item in tracks["items"]
                ]
            )
            return df

        else:
            return pd.DataFrame()

    def get_genres(self, artist_id):
        api_base_url = "https://api.spotify.com/v1"
        headers = {"Authorization": f"Bearer {session.get('access_token')}"}

        response = requests.get(f"{api_base_url}/artists/{artist_id}", headers=headers)
        if response.status_code == 200:
            artist_data = response.json()
            genres = artist_data.get("genres", [])
            return ",".join(genres)
        else:
            return "-"
