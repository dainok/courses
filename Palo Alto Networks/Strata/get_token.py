#!/usr/bin/env python
from getpass import getpass
import requests

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}
data = {
    "user": "admin",
    "password": getpass(),
}
url = "https://172.25.10.4/api/?type=keygen"
req = requests.post(url, headers=headers, data=data, verify=False)
req.raise_for_status()
print(req.text)
