#!/usr/bin/env python3
"""Build the Ansible inventory from a custom CSV."""

import csv
import json

CSV_FILE = "inventory.csv"
ANSIBLE_USER = "admin"
ANSIBLE_SSH_PASS = "cisco"
ANSIBLE_CONNECTION = "ansible.netcommon.network_cli"
ANSIBLE_NETWORK_OS = "cisco.ios.ios"


def inventory():
    """Return Ansible inventory."""
    # Inventory structure
    ansible_inventory = {
        "_meta": {
            "hostvars": {},
        },
        "routers": {
            "hosts": [],
            "vars": {
                "ansible_user": ANSIBLE_USER,
                "ansible_password": ANSIBLE_SSH_PASS,
                "ansible_connection": ANSIBLE_CONNECTION,
                "ansible_network_os": ANSIBLE_NETWORK_OS,
            },
        },
    }

    # Read the CSV file
    with open(CSV_FILE, encoding="utf-8") as csv_fh:
        csv_reader = csv.reader(csv_fh, delimiter=";", quotechar='"')
        next(csv_reader, None)  # Skip the headers
        for row in csv_reader:
            hostname = row[0]
            ip_address = row[1]

            # Add device
            ansible_inventory["_meta"]["hostvars"][hostname] = {
                "ansible_host": ip_address,
            }

            # Append device to group router
            ansible_inventory["routers"]["hosts"].append(hostname)

    return ansible_inventory


def main():
    """Main function."""
    print(json.dumps(inventory(), sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
