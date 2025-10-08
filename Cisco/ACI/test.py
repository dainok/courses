#!/usr/bin/env python

import os
from api import APIClient

apic = os.environ.get("ACI_ADDRESS")
username = os.environ.get("ACI_USERNAME")
password = os.environ.get("ACI_PASSWORD")

client = APIClient(
    apic_address=apic,
    username=username,
    password=password,
    verify=False,
)


print("FIRST")
res = client.get("/node/class/fvTenant.json")
print(res.status_code)


import time

time.sleep(570)

print("REFRESH")
res = client.get("/node/class/fvTenant.json")
print(res.status_code)

time.sleep(630)

print("FAIL")
res = client.get("/node/class/fvTenant.json")
print(res.status_code)
