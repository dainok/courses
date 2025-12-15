#!/usr/bin/env python3
import os
import re
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

url = f'https://{apic_address}/api/class/fabricNode.json?query-target-filter=and(eq(fabricNode.role,"leaf"))&challenge={token}'
res = session.get(url, verify=False)
res.raise_for_status()
leaf_list = [node["fabricNode"]["attributes"] for node in res.json()["imdata"]]

# Get CDP neighbors

url = f'https://{apic_address}/api/class/cdpAdjEp.json?order-by=cdpAdjEp.dn&challenge={token}'
res = session.get(url, verify=False)
res.raise_for_status()
neighbor_list = [neighbor["cdpAdjEp"]["attributes"] for neighbor in res.json()["imdata"]]

# Print output

for neighbor in neighbor_list:
    m = re.search(r"topology/pod-(\d+)/node-(\d+)/.*?/if-\[([^\]]+)\]", neighbor["dn"])
    pod_id, leaf_id, interface_id = m.groups()
    leaf_id = int(leaf_id)
    leaf_name = None
    for leaf in leaf_list:
        if leaf["id"] == leaf_id:
            leaf_name = leaf["name"]

    data.append([
        pod_id, # PodID
        leaf_id, # LeafID
        leaf_name, # LeafName
        interface_id, # Interface
        neighbor["devId"], # RemoteName
        neighbor["portId"], # RemoteInterface
    ])

print(tabulate(data, headers=headers))
