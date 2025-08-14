#!/usr/bin/env python
from getpass import getpass
import requests
from pprint import pprint
from requests.auth import HTTPBasicAuth

# Get input data
username = input("Username: ")
tenant_id = input("Tenant ID: ")
password = getpass()

# Get token
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}
http_username = f"{username}@{tenant_id}.iam.panserviceaccount.com"
basic_auth = HTTPBasicAuth(http_username, password)
data = {
    "grant_type": "client_credentials",
    "scope": f"tsg_id:{tenant_id}",
}
url = "https://auth.apps.paloaltonetworks.com/oauth2/access_token"
req = requests.post(url, auth=basic_auth, headers=headers, data=data)
req.raise_for_status()
token = req.json()["access_token"]

# Get devices
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Bearer {token}"
}
req = requests.get("https://api.strata.paloaltonetworks.com/config/setup/v1/devices", headers=headers)
req.raise_for_status()
pprint(req.json())

