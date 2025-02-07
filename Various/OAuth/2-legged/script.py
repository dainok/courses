#!/usr/bin/env python3

from getpass import getpass
import requests
import yaml


def save_config(config):
    """Save parameters to secrets.yml."""
    config = config
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

    return config


def main():
    """Main program."""
    # Read config
    config = read_config()
    if not config.get("access_token"):
        config["access_token"] = getpass(prompt="Creator's Access Token:")
        save_config(config)

    # Test the token
    headers = {"Authorization": f"Bearer {config['access_token']}"}
    uri = "https://www.patreon.com/api/oauth2/api/current_user"
    req = requests.get(uri, headers=headers, timeout=30)
    if req.status_code == 200:
        print("Token is valid")
    else:
        print(f"Got {req.status_code} error from Patreon")


if __name__ == "__main__":
    main()
