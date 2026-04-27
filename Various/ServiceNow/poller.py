#!/usr/bin/env python3

import requests
import uuid
import ansible_runner

SN_INSTANCE = "https://dev354802.service-now.com/"
USER = "admin"
PASS = "password"

AUTH = (USER, PASS)

STATE_MAP = {
    "open": 1,
    "work_in_progress": 2,
    "closed_complete": 3,
    "closed_incomplete": 4,
}

CATALOG_MAP = {
    "network_request": "8ea0b64593908710be22fd245d03d61b",
    "whitelist_request": "e91336da4fff0200086eeed18110c7a3",
    "vm_request": "f3937ada4fff0200086eeed18110c7f2",
}

DATA_MAP = {
    "4c46f68193d08710be22fd245d03d6f2": "network_ip_address",
    "0046f68193d08710be22fd245d03d6f3": "network_vlan",
    "8846f68193d08710be22fd245d03d6f2": "network_name",
}

def get_req_from_ritm(ritm_sys_id):
    """Get REQ from RITM."""
    url = f"{SN_INSTANCE}/api/now/table/sc_req_item/{ritm_sys_id}"
    params = {"sysparm_fields": "request"}
    r = requests.get(url, auth=AUTH, params=params)
    r.raise_for_status()
    return r.json()["result"]["request"]["value"]

def get_all_ritm_from_req(req_sys_id):
    """Get all RITMs from REQ."""
    url = f"{SN_INSTANCE}/api/now/table/sc_req_item"
    params = {
        "sysparm_query": f"request={req_sys_id}",
        "sysparm_fields": "sys_id,state,closed_at",
    }
    r = requests.get(url, auth=AUTH, params=params)
    r.raise_for_status()
    return r.json()["result"]

def get_ritms(category=None):
    """Get active RITMs for a specific category."""
    url = f"{SN_INSTANCE}/api/now/table/sc_req_item"
    params = {
        "sysparm_query": f"state={STATE_MAP.get('open')}",
        "sysparm_fields": "sys_id,state,number,variables,cat_item,sc_item_option"
    }
    if category:
        params["sysparm_query"] += f"^cat_item={CATALOG_MAP[category]}"

    r = requests.get(url, auth=AUTH, params=params)
    r.raise_for_status()
    return r.json()["result"]

def get_ritm_variables(ritm_sys_id):
    """Get RITM variabiles."""
    # Get RITM variable IDs
    url = f"{SN_INSTANCE}/api/now/table/sc_item_option_mtom"
    params = {
        "sysparm_query": f"request_item={ritm_sys_id}",
        "sysparm_fields": "sc_item_option",
        "sysparm_limit": 100,
    }
    r = requests.get(url, auth=AUTH, params=params)
    r.raise_for_status()
    option_ids = [
        item["sc_item_option"]["value"] 
        for item in r.json()["result"]
    ]

    # Get all RITM variables
    variables = {}
    ids_query = "^ORsys_id=".join(option_ids)
    url = f"{SN_INSTANCE}/api/now/table/sc_item_option"
    params = {
        "sysparm_query": f"sys_id={ids_query}",
        "sysparm_fields": "item_option_new.name,item_option_new.question_text,value",
        "sysparm_display_value": "all",
        "sysparm_limit": 100,
    }
    r = requests.get(url, auth=AUTH, params=params)
    r.raise_for_status()
    for item in r.json()["result"]:
        name  = item.get("item_option_new.name", {}).get("value", "")
        value = item.get("value", {}).get("display_value", "")
        if name:
            variables[name] = value

    return variables

def close_req(req_sys_id):
    """Close REQ using state=3 (Closed Complete)."""
    url = f"{SN_INSTANCE}/api/now/table/sc_request/{req_sys_id}"
    payload = {
        "state": "3",
        "active": "false",
    }
    r = requests.patch(url, auth=AUTH, json=payload)
    r.raise_for_status()
    return r.json()["result"]

def all_ritm_closed(ritm_list):
    """Check if all RITMs are closed (3, 4 or 7)."""
    CLOSED_STATES = {"3", "4", "7"}
    return all(ritm["state"] in CLOSED_STATES for ritm in ritm_list)

def update_ritm(ritm_sys_id, state, output=None):
    """Update RITM."""
    url = f"{SN_INSTANCE}/api/now/table/sc_req_item/{ritm_sys_id}"
    payload = {
        "state": STATE_MAP[state],
    }
    if output:
        payload["work_notes"] = output

    requests.patch(url, json=payload, auth=AUTH)

    # Close REQ if all RITMs are closed
    req_sys_id = get_req_from_ritm(ritm_sys_id)
    ritm_list = get_all_ritm_from_req(req_sys_id)
    if all_ritm_closed(ritm_list):
        print("Closing request")
        close_req(req_sys_id)

def run_ansible_network(name, vlan, ip_address):
    """Run Ansible."""
    extravars = {
        'network_name': name,
        'network_vlan': vlan,
        'network_ip_address': ip_address,
    }
    print("Running Ansible playbook with", extravars)
    run = ansible_runner.run(
        private_data_dir='.',
        playbook=f'playbook-snow_network.yml',
        extravars=extravars,
        envvars={
            "ANSIBLE_FORCE_COLOR": "false",
            "NO_COLOR": "1",
        }
    )
    return run

def run_ansible_vm(cpu, ram, storage):
    """Run Ansible."""
    extravars = {
        'vm_name': f'vm-snow-portal-{str(uuid.uuid4())}',
        'vm_ram': int(ram) * 1024,
        'vm_cpu': int(cpu),
        'vm_storage': storage,
    }
    print("Running Ansible playbook with", extravars)
    run = ansible_runner.run(
        private_data_dir='.',
        playbook=f'playbook-snow_vm.yml',
        extravars=extravars,
        envvars={
            "ANSIBLE_FORCE_COLOR": "false",
            "NO_COLOR": "1",
        }
    )
    return run

def main():
    requests_list = get_ritms(category="network_request")
    requests_list = get_ritms()

    for req in requests_list:
        print(f"Processing {req['number']}")

        # Get request data
        sys_id = req["sys_id"]
        variables = get_ritm_variables(sys_id)

        if req["cat_item"]["value"] == CATALOG_MAP["network_request"]:
            print(f"{sys_id} is a network request")

            # Mark ticket as WIP
            update_ritm(sys_id, "work_in_progress")

            # Run Ansible
            result = run_ansible_network(name=variables.get("name"), vlan=variables.get("vlan"), ip_address=variables.get("ip_address"))
            rc = result.rc
            stdout = result.stdout.read()
            stderr = result.stderr.read()
            if rc == 0:
                update_ritm(sys_id, "closed_complete", stdout)
            else:
                update_ritm(sys_id, "closed_incomplete", stdout + "\n" * 3 + stderr)
        elif req["cat_item"]["value"] == CATALOG_MAP["vm_request"]:
            print(f"{sys_id} is a vm request")

            # Mark ticket as WIP
            update_ritm(sys_id, "work_in_progress")

            # Run Ansible
            print(variables)
            storage=variables.get("storage")
            storage=storage.replace(" GB", "")
            storage=storage.replace(" TB", "000")
            storage=int(storage)
            result = run_ansible_vm(cpu=variables.get("cpu"), ram=variables.get("ram"), storage=storage)
            rc = result.rc
            stdout = result.stdout.read()
            stderr = result.stderr.read()
            if rc == 0:
                update_ritm(sys_id, "closed_complete", stdout)
            else:
                update_ritm(sys_id, "closed_incomplete", stdout + "\n" * 3 + stderr)

if __name__ == "__main__":
    main()
