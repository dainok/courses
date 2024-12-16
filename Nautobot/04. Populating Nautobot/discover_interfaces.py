#!/usr/bin/env python3

from getpass import getpass
from netmiko import ConnectHandler
import requests

# Reading input data
nautobot_apikey = "ced15098774a01a54fb7f4fcfadba56e9e68a8c0"
nautobot_base_url = "http://localhost:8000"
host = input("Address: ")
device_type = input("Model (default cisco_ios): ")
if not device_type:
    # Default model is cisco_ios
    device_type = "cisco_ios"
username = input("Username: ")
password = getpass(prompt="Password: ")

# Connecting to device
data = {
    "device_type": device_type,
    "host": host,
    "username": username,
    "password": password,
    # "secret": secret,
}
with ConnectHandler(**data) as net_connect:
    show_version = net_connect.send_command("show version", use_textfsm=True)
    show_interfaces = net_connect.send_command("show interfaces", use_textfsm=True)

# Parsing data
device_name = show_version[0]["hostname"].upper()
device_interfaces = {
    item["interface"]: {
        "description": item["description"],
        "status": "Active" if item["link_status"] == "up" else "Decommissioning",
    }
    for item in show_interfaces
}

# Ingesting data to Nautobot
headers = {
    "Authorization": f"Token {nautobot_apikey}",
    "Accept": "application/json",
}

# Get device ID
url = f"{nautobot_base_url}/api/dcim/devices/?name={device_name}"
req = requests.get(url, headers=headers, timeout=30).json()
if req["count"] < 1:
    raise ValueError(f"{device_name} not found")
device_id = req["results"][0]["id"]

# For each interface
for interface_name, interface in device_interfaces.items():
    url = f"{nautobot_base_url}/api/dcim/interfaces/?device_id={device_id}&name={interface_name}"
    req = requests.get(url, headers=headers, timeout=30).json()
    if req["count"] == 0:
        # Create interface
        headers["Content-Type"] = "application/json"
        url = f"{nautobot_base_url}/api/dcim/interfaces/"
        data = {
            "device": device_id,
            "name": interface_name,
            "description": interface["description"],
            "status": interface["status"],
            "type": "other",
        }
        requests.post(url, headers=headers, json=data, timeout=30).json()
