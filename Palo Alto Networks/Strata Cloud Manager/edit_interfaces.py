#!/usr/bin/env python
import os
import uuid
from api import APIClient

tenant_id = os.environ.get("SCM_TENANT_ID")
username = os.environ.get("SCM_USERNAME")
password = os.environ.get("SCM_PASSWORD")
api_timestamp = uuid.uuid4().hex[:8]

client = APIClient(
    tenant_id=tenant_id,
    username=username,
    password=password,
)

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

        # Get interface details
        interface_url = f"/config/network/v1/ethernet-interfaces/{interface_id}"
        req = client.get(interface_url)
        req.raise_for_status()
        interface_details = req.json()

        # Edit comment
        interface_name = interface_details["name"]
        interface_details["comment"] = f"{interface_name} managed via API ({api_timestamp})"
        req = client.put(interface_url, json=interface_details)
        req.raise_for_status()
