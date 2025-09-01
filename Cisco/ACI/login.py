#!/usr/bin/env python3
import os
import requests

apic_address = os.environ.get("ACI_ADDRESS")
apic_username = os.environ.get("ACI_USERNAME")
apic_password = os.environ.get("ACI_PASSWORD")

url = f"https://{apic_address}/api/aaaLogin.json"
payload = {
    "aaaUser": {
        "attributes": {
            "name": apic_username,
            "pwd": apic_password,
        }
    }
}

session = requests.Session()
res = session.post(url, json=payload, verify=False)
res.raise_for_status()

print(
    "Timeout:",
    res.json()["imdata"][0]["aaaLogin"]["attributes"]["refreshTimeoutSeconds"],
)
print("Token:", res.json()["imdata"][0]["aaaLogin"]["attributes"]["token"])
print("Cookies", res.cookies)

timeout = res.json()["imdata"][0]["aaaLogin"]["attributes"]["refreshTimeoutSeconds"]
token = res.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]
url = f"https://{apic_address}/api/node/class/fvTenant.json?challenge={token}"
res = session.get(url, json=payload, verify=False)
res.raise_for_status()
