#!/usr/bin/env python3

import json
import logging
from pprint import pprint
from nornir import InitNornir
from nornir.core.filter import F
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir.core.inventory import (
    Inventory,
    Host,
    Hosts,
    Group,
    Groups,
    ParentGroups,
    Defaults,
    ConnectionOptions,
)
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result

ANSIBLE_INVENTORY = {
    "_meta": {
        "hostvars": {
            "c8k1.eve-ng.local": {
                "ansible_connection": "ansible.netcommon.network_cli",
                "ansible_host": "172.24.1.61",
                "ansible_network_os": "cisco.ios.ios",
                "ansible_password": "cisco",
                # "ansible_become_password": "cisco",  
                "ansible_user": "admin",
                "netmiko_device_type": "cisco_ios",
            },
        },
    },
}

NORNIR_NETMIKO_READ_TIMEOUT = 120

CISCO_COMMANDS = [
    "show version",
    "show interfaces",
    "show cdp neighbors detail",
    "show lldp neighbors detail",
]

URLS = ["/"]

class AssetInventory:
    """Build Nornir AssetInventory."""

    def load(self) -> Inventory:
        """Load items from remote inventory."""
        defaults = Defaults()
        hosts = Hosts()
        groups = Groups()

        # Add "all" group
        groups["all"] = Group("all")

        # Load hosts from inventory
        for inventory_hostname, host_data in ANSIBLE_INVENTORY["_meta"]["hostvars"].items():
            hosts[inventory_hostname] = Host(
                name=inventory_hostname,
                hostname=host_data["ansible_host"],
                username=host_data["ansible_user"],
                password=host_data["ansible_password"],
                port=22,
                platform=host_data["netmiko_device_type"],
                data=host_data,
                groups=ParentGroups(),
            )

        return Inventory(hosts=hosts, groups=groups, defaults=defaults)


# Configuring Nornir
logger = logging.getLogger("nornir")
logger.setLevel(logging.DEBUG)
file_h = logging.FileHandler("nornir.log")
file_h.setLevel(logging.DEBUG)
logger.addHandler(file_h)

# Load Nornir custom inventory
InventoryPluginRegister.register("asset-inventory", AssetInventory)

# Create Nornir inventory
nrni = InitNornir(
    runner={
        "plugin": "threaded",
        "options": {
            "num_workers": 100,
        },
    },
    inventory={"plugin": "asset-inventory"},
    logging={"enabled": False},
)
# https://nornir.readthedocs.io/en/latest/howto/advanced_filtering.html
# nrni = nrni.filter(F(hostname="172.29.128.50"))
print(json.dumps(nrni.inventory.dict(), indent=4))


#######################################################################
# Tasks
#######################################################################
def multiple_tasks(task):
    for command in CISCO_COMMANDS:
        task.run(
            name=command,
            task=netmiko_send_command,
            command_string=command,
            use_textfsm=False,
            use_timing=False,
            read_timeout=NORNIR_NETMIKO_READ_TIMEOUT,        
        )

#######################################################################
# Run the playbook
#######################################################################
aggregated_results = nrni.run(task=multiple_tasks)

# Print the result
print_result(aggregated_results)
