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

headers = [
    "Device",
    "Interface",
    "Type",
    "IP Addresses",
    "Description",
]
lines = []

# Get devices
req = client.get("/config/setup/v1/devices")
req.raise_for_status()
devices = req.json()

# For each device, get interfaces
for device in devices["data"]:
    device_id = device["id"]
    device_hostname = device["hostname"]

    req = client.get(f"/config/network/v1/ethernet-interfaces?device={device_id}")
    req.raise_for_status()
    interfaces = req.json()

    for interface in interfaces["data"]:
        interface_id = interface["id"]
        interface_name = interface["name"]
        interface_description = interface.get("comment", "")
        interface_type = None
        interface_ip = None
        if "layer3" in interface:
            interface_type = "layer3"
            interface_ip = ",".join(
                ip["name"] for ip in interface.get("layer3", {}).get("ip", [])
            )

        # Add line to the table
        lines.append(
            [
                device_hostname,
                interface_name,
                interface_type,
                interface_ip,
                interface_description,
            ]
        )

print(tabulate(lines, headers=headers, tablefmt="grid"))
