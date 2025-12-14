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
    "Admin",
    "AutoNeg",
    "Description",
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

# Fetch objects
def fetch_objects(class_name, page_size=10):
    page = 0
    while True:
        url = f"https://{apic_address}/api/class/{class_name}.json?page-size={page_size}&page={page}"
        res = session.get(url, verify=False)
        res.raise_for_status()
        items = res.json().get("imdata", [])
        if not items:
            # No more data
            break
        for item in items:
            # Return one object
            yield item
        # Next page
        page += 1


# Get leaves

leaf_list = list(fetch_objects("fabricNode"))

# Get interfaces

interface_list = fetch_objects("l1PhysIf")

for interface in interface_list:
    interface_attrs = interface["l1PhysIf"]["attributes"]
    m = re.search(r"topology/pod-(\d+)/node-(\d+)/.*?/.*", interface_attrs["dn"])
    pod_id, leaf_id = m.groups()
    leaf_name = None
    for leaf in leaf_list:
        leaf_attribute = leaf["fabricNode"]["attributes"]
        if leaf_id == leaf_attribute["id"]:
            leaf_name = leaf_attribute["name"]
    data.append([
        pod_id, # PodID
        leaf_id, # LeafID
        leaf_name, # LeafName
        interface_attrs["id"], # Interface
        interface_attrs["adminSt"], # Admin
        interface_attrs["autoNeg"], # AutoNeg
        interface_attrs["descr"], # Description
    ])

print(tabulate(data, headers=headers))
