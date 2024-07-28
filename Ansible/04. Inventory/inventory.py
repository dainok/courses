#!/usr/bin/env python3
"""
Simple dynamic inventory for Ansible.

The script reads a CSV file and print a JSON formatted Ansible inventory.
"""
import csv
import json


INVENTORY_CSV = "inventory.csv"


def main():
    """Main function."""
    inventory = {
        "_meta": {
            "hostvars": {},
            "vars": {
                "ansible_connection": "ansible.netcommon.network_cli",
                "ansible_network_os": "cisco.ios.ios",
            },
        },
        "routers": {
            "hosts": [],
            "vars": {"ansible_ssh_pass": "cisco", "ansible_user": "admin"},
        },
        "switches": {
            "hosts": [],
            "vars": {"ansible_ssh_pass": "cisco", "ansible_user": "admin"},
        },
        "core": {
            "hosts": [],
        },
        "access": {
            "hosts": [],
        },
    }

    with open(INVENTORY_CSV, "r") as fh:
        csv_reader = csv.reader(fh, delimiter=";", dialect="excel")
        next(csv_reader, None)  # skip first row (header)

        for row in csv_reader:
            # Parse each row
            fqdn = row[0]
            ip_address = row[1]
            groups = row[2].split(",")

            # Add device to group "all"
            inventory["_meta"]["hostvars"][fqdn] = {"ansible_host": ip_address}

            for group in groups:
                # Add device to group
                inventory[group]["hosts"].append(fqdn)

    # Print inventory
    print(json.dumps(inventory, sort_keys=True, indent=2))


if __name__ == "__main__":
    # Calling main function
    main()
