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
    "RemoteName",
    "RemoteInterface",
]
data = []

# Login

client = APIClient(
    apic_address=apic_address,
    username=apic_username,
    password=apic_password,
    verify=False,
    page_size=10,
)

# Get leaves

leaf_list = list(client.get_objects('/class/fabricNode.json?query-target-filter=and(eq(fabricNode.role,"leaf"))'))

# Get CDP neighbors

neighbor_list = list(client.get_objects('/class/cdpAdjEp.json?order-by=cdpAdjEp.dn'))

# Print output

for n in neighbor_list:
    neighbor = n["cdpAdjEp"]["attributes"]
    m = re.search(r"topology/pod-(\d+)/node-(\d+)/.*?/if-\[([^\]]+)\]", neighbor["dn"])
    pod_id, leaf_id, interface_id = m.groups()
    leaf_id = int(leaf_id)
    leaf_name = None
    for l in leaf_list:
        leaf = l["fabricNode"]["attributes"]
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
