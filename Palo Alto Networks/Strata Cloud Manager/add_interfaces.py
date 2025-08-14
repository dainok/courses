#!/usr/bin/env python
import os
import uuid
from api import APIClient

tenant_id = os.environ.get("SCM_TENANT_ID")
username = os.environ.get("SCM_USERNAME")
password = os.environ.get("SCM_PASSWORD")
api_timestamp = uuid.uuid4().hex[:8]
device_hostname = "PA-LGM-460"
interfaces = {
    "ethernet1/4": {
        "type": "layer3",
        "address": "172.23.1.1/24",
        "mgmt_profile": "mgmt-full",
    },
    "ethernet1/5": {
        "type": "layer3",
        "address": "172.23.1.1/24",
        "mgmt_profile": "mgmt-full",
    },
}

client = APIClient(
    tenant_id=tenant_id,
    username=username,
    password=password,
)

# Get devices
req = client.get("/config/setup/v1/devices")
req.raise_for_status()
devices = req.json()

device_id = None
for device in devices["data"]:
    if device["hostname"] == device_hostname:
        # Device found
        device_id = device["id"]
if not device_id:
    # Device not found
    raise ValueError(f"Device {device_hostname} not found")

# Get interfaces
req = client.get(f"/config/network/v1/ethernet-interfaces?device={device_id}")
req.raise_for_status()
device_interfaces = req.json()
interface_name_to_id_map = {
    interface["name"]: interface["id"] for interface in device_interfaces["data"]
}

# Create interfaces
for interface_name, interface in interfaces.items():
    if interface_name in interface_name_to_id_map:
        print(f"Interface {interface_name} already exists")
        continue
    data = {
        "name": interface_name,
        "comment": "Created via API",
        "link-speed": "auto",
        "link-duplex": "auto",
        "link-state": "auto",
        "layer3": {
            "interface_management_profile": interface["mgmt_profile"],
            "ip": [{"name": interface["address"]}],
            "lldp": {"enable": False},
        },
    }
    req = client.post(
        f"/config/network/v1/ethernet-interfaces?device={device_id}", json=data
    )
    req.raise_for_status()
