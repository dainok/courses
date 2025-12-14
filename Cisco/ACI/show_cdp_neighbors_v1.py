#!/usr/bin/env python3
import os
import requests
from tabulate import tabulate

apic_address = os.environ.get("ACI_ADDRESS")
apic_username = os.environ.get("ACI_USERNAME")
apic_password = os.environ.get("ACI_PASSWORD")

headers = [
    "PodID",
    "LeafID",
    "LeafName",
    "Interface",
    "RemoteName",
    "RemoteInterface",
]
data = []

# Login

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
token = res.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]

# Get leaves

url = f"https://{apic_address}/api/node/mo/topology/pod-1.json?query-target=children&target-subtree-class=fabricNode&challenge={token}"
res = session.get(url, verify=False)
res.raise_for_status()
for node in res.json()["imdata"]:
    if node["fabricNode"]["attributes"]["role"] == "leaf":
        leaf = node["fabricNode"]["attributes"]

        # Get interfaces

        url = f"https://{apic_address}/api/node/class/topology/pod-1/node-{leaf['id']}/l1PhysIf.json?rsp-subtree=children&rsp-subtree-class=ethpmPhysIf&rsp-subtree-include=required&order-by=l1PhysIf.id|asc&page=0&page-size=100&challenge={token}"
        res = session.get(url, verify=False)
        res.raise_for_status()
        for item in res.json()["imdata"]:
            interface = item["l1PhysIf"]["attributes"]

            # Get CDP neighbors
            
            url = f"https://{apic_address}/api/node/mo/topology/pod-1/node-{leaf['id']}/sys/cdp/inst/if-[{interface['id']}].json?query-target=children&target-subtree-class=cdpAdjEp&challenge={token}"
            res = session.get(url, verify=False)
            res.raise_for_status()
            for item in res.json()["imdata"]:
                neighbor = item["cdpAdjEp"]["attributes"]
                data.append([
                    1, # PodID
                    leaf["id"], # LeafID
                    leaf["name"], # LeafName
                    interface["id"], # Interface
                    neighbor["devId"], # RemoteName
                    neighbor["portId"], # RemoteInterface
                ])

# Print output

print(tabulate(data, headers=headers))
