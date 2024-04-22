#!/usr/bin/env python3
"""
Connect to a Cisco IOS device via telnet and enable SSH.

Depends on: pip install netmiko==4.3.0
"""

import sys
import os
import argparse
from pprint import pprint
from netmiko import ConnectHandler

password = os.getenv("LEGACY_DEVICE_PASSWORD")
secret = os.getenv("LEGACY_DEVICE_SECRET")
if not password:
    print("Set environment variable LEGACY_DEVICE_PASSWORD")
    sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument("--hostname", required=True, help="device hostname")
parser.add_argument("--username", required=True, help="privileged username")
args = parser.parse_args()

device = {
    "host": args.hostname,
    "username": args.username,
    "password": password,
    "verbose": False,
}
if secret:
    device["secret"] = secret

output = ""
net_connect = ConnectHandler(**device, device_type="cisco_ios_telnet")
output += net_connect.send_config_set("ip domain name tndigit.it")
output += net_connect.send_config_set("crypto key generate rsa modulus 2048")
output += net_connect.send_config_set("ip ssh version 2")
output += net_connect.send_config_set(
    [
        "line vty 0 15",
        "transport input telnet ssh",
    ]
)
net_connect.disconnect()
pprint(output)

net_connect = ConnectHandler(**device, device_type="cisco_ios")
net_connect.disconnect()
print("*" * 70)
print(f"SSH is enabled on {device['host']}")
print("*" * 70)
