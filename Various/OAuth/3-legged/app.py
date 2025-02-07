#!/usr/bin/env python3

import yaml
import requests
from flask import Flask, request, redirect

app = Flask(__name__)
app.config["redirect_uri"] = "http://localhost:5000/callback"


def save_config():
    """Save WebApp parameters to secrets.yml."""
    config = {
        "client_id": app.config.get("client_id"),
        "client_secret": app.config.get("client_secret"),
        "access_token": app.config.get("access_token"),
    }
    with open("secrets.yml", "w") as fh:
        yaml.dump(config, fh, default_flow_style=False)


def read_config():
    """Read parameters from secrets.yml and configure the WebApp."""
    try:
        with open("secrets.yml", "r") as fh:
            config = yaml.safe_load(fh)
    except FileNotFoundError:
        # File not found, create an empty file
        config = {}
    app.config.update(
        client_id=config.get("client_id"),
        client_secret=config.get("client_secret"),
        access_token=config.get("access_token"),
    )


@app.route("/")
def main():
    """Home page."""
    read_config()
    if app.config["access_token"]:
        # Access token exists, let's test it
        headers = {"Authorization": f"Bearer {app.config['access_token']}"}
        uri = "https://www.patreon.com/api/oauth2/api/current_user"
        req = requests.get(uri, headers=headers, timeout=30)
        if req.status_code == 200:
            return "Token is valid"

    if app.config["client_id"]:
        # App has been configured
        uri = f"https://www.patreon.com/oauth2/authorize?response_type=code&client_id={app.config['client_id']}&redirect_uri={app.config['redirect_uri']}"
        return f'<a href="{uri}">Login with Patreon</a>'

    # App has not been configured, prompt for parameters
    return """
        <form action="/config" method="post">
            <b>Client ID:<b> <input type="text" name="client_id"><br>
            <b>Client Secret:</b> <input type="password" name="client_secret"><br>
            <input type="submit" value="Configure">
        </form>
    """


@app.route("/config", methods=["POST"])
def config():
    """Receive parameters."""
    client_id = request.form.get("client_id")
    client_secret = request.form.get("client_secret")
    if client_id and client_secret:
        # Both parameters are set
        app.config.update(
            client_id=client_id,
            client_secret=client_secret,
        )
        save_config()
        return redirect("/")

    # Missing parameters
    return "Both <code>client_id</code> and <code>client_secret</code> must be filled"


@app.route("/callback")
def callback():
    if request.args.get("code"):
        # Got an authorization code, let's test it
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        uri = "https://www.patreon.com/api/oauth2/token"
        data = {
            "code": request.args.get("code"),
            "grant_type": "authorization_code",
            "client_id": app.config["client_id"],
            "client_secret": app.config["client_secret"],
            "redirect_uri": app.config["redirect_uri"],
        }
        req = requests.post(uri, data=data, headers=headers, timeout=30)
        if req.status_code == 200:
            # Authorization code is good, let's save the access token
            data = req.json()
            app.config["access_token"] = data.get("access_token")
            save_config()
            return "App has been configured"

        # Something went wrong
        return f"Got {req.status_code} error from Patreon"

    # Missing parameters
    return "<code>code</code> must be filled"
