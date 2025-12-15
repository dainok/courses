#!/usr/bin/env python3
import os
import re
from api_client import APIClient
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

client = APIClient(
    apic_address=apic_address,
    username=apic_username,
    password=apic_password,
    verify=False,
    page_size=50,
)

# Get leaves

leaf_list = list(client.get_objects("/class/fabricNode.json"))

# Get interfaces

interface_list = client.get_objects("/class/l1PhysIf.json")

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
