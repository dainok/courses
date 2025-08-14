#!/usr/bin/env python
import os
from tabulate import tabulate
from api import APIClient

tenant_id = os.environ.get("SCM_TENANT_ID")
username = os.environ.get("SCM_USERNAME")
password = os.environ.get("SCM_PASSWORD")

client = APIClient(
    tenant_id=tenant_id,
    username=username,
    password=password,
)
folder = "FOLDER_NAME"
req = client.get(f"/config/objects/v1/addresses?folder={folder}")
req.raise_for_status()

headers = [
    "Folder",
    "Snippet",
    "Name",
    "IP/FQDN",
]
lines = []
for item in req.json()["data"]:
    host = None
    if "ip_netmask" in item:
        host = item["ip_netmask"]
    if "fqdn" in item:
        host = item["fqdn"]
    lines.append([
        item.get("folder", ""),
        item.get("snippet", ""),
        item.get("name", ""),
        host,
    ])
print(tabulate(lines, headers=headers, tablefmt="grid"))
