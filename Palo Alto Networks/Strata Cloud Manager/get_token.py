#!/usr/bin/env python
from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}
username = input("Username: ")
tenant_id = input("Tenant ID: ")
password = getpass()
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
print(token)
