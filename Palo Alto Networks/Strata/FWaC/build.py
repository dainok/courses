#!/usr/bin/env python3

# Examples
# https://github.com/PaloAltoNetworks/pan-os-python/blob/develop/docs/examples.rst
# https://github.com/PaloAltoNetworks/pan-os-python/tree/develop/examples
# http://api-lab.paloaltonetworks.com/_static/panos-xml-api-rtd.pdf
# https://172.25.82.172/php/rest/browse.php

# TODO: check if objects are used (address groups, services)
# TODO: omit intra-network rules (used for microsegmentation)
# TODO: import rule hit ad sort if order is not important


import random
import logging
import ipaddress
from xml.etree import ElementTree
from xml.dom import minidom

import yaml
import pan.xapi
import pan.commit
import pan.config


RUNNING_CONFIG_FILE = "running-config.xml"
CANDIDATE_CONFIG_FILE = "generated-config.xml"
NETWORKS = [
    "rules/infra/networks.yml",
    "rules/www/networks.yml",
]
RULES = [
    "rules/infra/rules.yml",
    "rules/www/rules.yml",
]
SERVICES = [
    "shared/services.yml",
]
ZONE_NETWORK_MAPPING = "shared/network-zone_mapping.yml"
USERNAME = "admin"
PASSWORD = "password"
HOSTNAME = "172.16.1.1"
LOG_FORWARDING_PROFILE = "IoT Security Default Profile"
VSYS = "vsys1"
PROVIDED_NETWORKS = {}
PROVIDED_SERVICES = {}
REQUIRED_NETWORKS = []
REQUIRED_GROUPS = []
REQUIRED_SERVICES = []
RULES_DETAILS = {}
ZONE_NETWORKS = {}


class DuplicatedNetwork(Exception):
    def __init__(self, network):
        self.network = network
        message = "network must be unique"
        if network:
            message = f"network {network} has already been defined"
        super().__init__(message)


class MissingZone(Exception):
    def __init__(self, network):
        self.network = network
        message = "zone has not been found"
        if network:
            message = f"zone has not been found for {network}"
        super().__init__(message)


class MissingNetwork(Exception):
    def __init__(self, network):
        self.network = network
        message = "network has not been defined"
        if network:
            message = f"network {network} has not been defined"
        super().__init__(message)


class MissingService(Exception):
    def __init__(self, service):
        self.service = service
        message = "service has not been defined"
        if service:
            message = f"service {service} has not been defined"
        super().__init__(message)


def print_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ElementTree.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")


def get_zones(group_address):
    zones = []

    if group_address == "any":
        net = ipaddress.ip_network("0.0.0.0/0")
        for zone_name, zone in ZONE_NETWORKS["zones"].items():
            for zone_network in zone["networks"]:
                supernet = ipaddress.ip_network(zone_network)
                if supernet.supernet_of(net) or net == supernet:
                    if zone_name not in zones:
                        # A single zone is expected
                        zones.append(zone_name)
                        return zones
    else:
        for network in PROVIDED_NETWORKS[group_address]:
            net = ipaddress.ip_network(network)
            for zone_name, zone in ZONE_NETWORKS["zones"].items():
                found = False
                for zone_network in zone["networks"]:
                    supernet = ipaddress.ip_network(zone_network)
                    if supernet.supernet_of(net) or net == supernet:
                        found = True
                        if zone_name not in zones:
                            zones.append(zone_name)
                        break
                # Multiple zones are expected
                if found:
                    break

    if not zones:
        raise MissingZone(group_address)
    return zones


xapi = pan.xapi.PanXapi(api_username=USERNAME, api_password=PASSWORD, hostname=HOSTNAME)

# Reading configuration
xapi.export(category="configuration")
running_config = xapi.element_root

# Dumping running configuration to file
logging.info(f"saving {RUNNING_CONFIG_FILE}")
print("*" * 78)
print(f"* Dumping {RUNNING_CONFIG_FILE}")
with open(RUNNING_CONFIG_FILE, "w") as fh:
    fh.write(print_xml(running_config))

# Read rules UUID
logging.info("reading rule uuids")
print("*" * 78)
print("* Reading rule UUIDs")
rules = running_config.findall(".//rulebase/security/rules/entry")
for rule in rules:
    RULES_DETAILS[rule.attrib["name"]] = {
        "uuid": rule.attrib["uuid"],
        "hit": 0,
    }

# Read rule hit count
print("*" * 78)
print(f"* Loading rule hit count")
print("*" * 78)
cmd_xml = f"<show><rule-hit-count><vsys><vsys-name><entry name='{VSYS}'><rule-base><entry name='security'><rules><all/></rules></entry></rule-base></entry></vsys-name></vsys></rule-hit-count></show>"
xapi.op(cmd=cmd_xml)
hit_count = xapi.element_root
for rule_name in RULES_DETAILS:
    print(f"Looking for {rule_name}")
    hit = int(
        hit_count.find(
            f".//entry/rule-base/entry/rules/entry[@name='{rule_name}']/hit-count"
        ).text
    )
    RULES_DETAILS[rule_name]["hit"] = hit + random.randint(
        0, 1000
    )  # TODO: only for tests
# Resort
for k in sorted(RULES_DETAILS, key=lambda x: RULES_DETAILS[x]["hit"], reverse=False):
    RULES_DETAILS[k] = RULES_DETAILS.pop(k)

# Clearing configuration
logging.info("clearing configuration")
print("*" * 78)
print("* Clearing configuration")

element_vsys = running_config.find(f".//vsys/entry[@name='{VSYS}']")

element_rulebase = element_vsys.find("./rulebase")
if not element_rulebase is not None:
    element_rulebase = ElementTree.SubElement(element_vsys, "rulebase")

element_address = element_vsys.find("./address")
if element_address is not None:
    element_address.clear()
else:
    element_address = ElementTree.SubElement(element_vsys, "address")

element_address_group = element_vsys.find("address-group")
if element_address_group is not None:
    element_address_group.clear()
else:
    element_address_group = ElementTree.SubElement(element_vsys, "address-group")

element_services = element_vsys.find("service")
if element_services is not None:
    element_services.clear()
else:
    element_services = ElementTree.SubElement(element_vsys, "service")

element_security = element_rulebase.find("security")
if element_security is not None:
    element_security.clear()
else:
    element_security = ElementTree.SubElement(element_rulebase, "security")
element_security_rules = ElementTree.SubElement(element_security, "rules")


# Reading zone mapping
print("*" * 78)
print(f"* Loading {ZONE_NETWORK_MAPPING}")

with open(ZONE_NETWORK_MAPPING, "r", encoding="utf-8") as fh:
    ZONE_NETWORKS = yaml.safe_load(fh)

# Adding addresses
for network_file in NETWORKS:
    print("*" * 78)
    print(f"* Loading {network_file}")
    print("*" * 78)

    with open(network_file, "r") as fh:
        network_objects = yaml.safe_load(fh)

    # Addresses and address groups
    for network_name, networks in network_objects["networks"].items():
        print(f"Adding group {network_name}")
        if network_name in PROVIDED_NETWORKS:
            raise DuplicatedNetwork(network_name)
        PROVIDED_NETWORKS[network_name] = networks

        # Building address group
        #   <entry name="RFC1918">
        #         <description>Source shared/networks.yml</description>
        #         <static>
        #             <member>RFC1918_0</member>
        #             <member>RFC1918_1</member>
        #             <member>RFC1918_2</member>
        #         </static>
        #   </entry>
        element_group_entry = ElementTree.SubElement(
            element_address_group, "entry", name=network_name
        )
        element_group_description = ElementTree.SubElement(
            element_group_entry, "description"
        )
        element_group_description.text = f"Source {network_file}"
        element_group_static_entries = ElementTree.SubElement(
            element_group_entry, "static"
        )

        counter = 0
        for network in networks:
            # Building address entry
            # <entry name="OFFICE_0">
            #     <description>Group OFFICE, source shared/networks.yml</description>
            #     <ip-netmask>10.23.4.0/24</ip-netmask>
            # </entry>
            address_name = f"{network_name}_{counter}"
            print(f"Adding address {address_name} to {network_name}")
            counter += 1
            element_address_entry = ElementTree.SubElement(
                element_address, "entry", name=address_name
            )
            element_address_description = ElementTree.SubElement(
                element_address_entry, "description"
            )
            element_address_description.text = (
                f"Group {network_name}, source {network_file}"
            )
            element_address_ip_netmask = ElementTree.SubElement(
                element_address_entry, "ip-netmask"
            )
            element_address_ip_netmask.text = network

            # Adding address to address group
            element_group_member = ElementTree.SubElement(
                element_group_static_entries, "member"
            )
            element_group_member.text = address_name

# Adding services
for service_file in SERVICES:
    print("*" * 78)
    print(f"* Loading {service_file}")
    print("*" * 78)

    with open(service_file, "r") as fh:
        service_objects = yaml.safe_load(fh)

    # Adding services if port and protocol are specified
    for service_name, service in service_objects["services"].items():
        # Save for later
        PROVIDED_SERVICES[service_name] = service

        if service.get("protocol") and service.get("port"):
            # Building service
            # <services>
            #     <entry name="DNS">
            #     <description>Source shared/services.yml</description>
            #         <protocol>
            #             <udp>
            #             <port>53</port>
            #             </udp>
            #         </protocol>
            #     </entry>
            # </services>
            print(f"Adding service {service_name}")
            element_service_entry = ElementTree.SubElement(
                element_services, "entry", name=service_name
            )
            element_service_description = ElementTree.SubElement(
                element_service_entry, "description"
            )
            element_service_description.text = f"Source {service_file}"
            element_service_protocol = ElementTree.SubElement(
                element_service_entry, "protocol"
            )
            element_service_proto = ElementTree.SubElement(
                element_service_protocol, service["protocol"]
            )
            element_service_port = ElementTree.SubElement(element_service_proto, "port")
            element_service_port.text = str(service["port"])

# Adding rules
for rule_file in RULES:
    print("*" * 78)
    print(f"* Loading {rule_file}")
    print("*" * 78)

    with open(rule_file, "r") as fh:
        rule_objects = yaml.safe_load(fh)

    # Adding rules
    counter = 0
    for rule in rule_objects["rules"]:
        # Building rule
        # <security>
        #     <rules>
        #         <entry name="auto-name" uuid="7b730dfa-9388-4fcd-b24d-8130a89537e1">
        #             <to>
        #                 <member>any</member>
        #             </to>
        #             <from>
        #                 <member>any</member>
        #             </from>
        #             <source>
        #                 <member>RFC1918</member>
        #             </source>
        #             <destination>
        #                 <member>OFFICE</member>
        #             </destination>
        #             <source-user>
        #                 <member>any</member>
        #             </source-user>
        #             <category>
        #                 <member>any</member>
        #             </category>
        #             <application>
        #                 <member>dns</member>
        #             </application>
        #             <service>
        #                 <member>application-default</member>
        #             </service>
        #             <source-hip>
        #                 <member>any</member>
        #             </source-hip>
        #             <destination-hip>
        #                 <member>any</member>
        #             </destination-hip>
        #             <action>allow</action>
        #             <log-setting>kali</log-setting>
        #         </entry>
        #     </rules>
        # </security>

        rule_tag = rule_file.split("/")[1]
        rule_name = f"{rule_tag}_{counter}"
        service_name = rule["service"]
        service = PROVIDED_SERVICES.get(service_name)
        REQUIRED_SERVICES.append(service_name)
        if not service:
            raise MissingService(service_name)
        counter += 1
        print(f"Adding rule {rule_name}")
        element_security_rule_entry = ElementTree.SubElement(
            element_security_rules, "entry", name=rule_name
        )
        if rule_name in RULES_DETAILS:
            element_security_rule_entry.set("uuid", RULES_DETAILS[rule_name]["uuid"])
        element_security_rule_description = ElementTree.SubElement(
            element_security_rule_entry, "description"
        )
        element_security_rule_description.text = rule["description"]
        # Source address
        source_address = rule.get("source-address")
        if source_address:
            REQUIRED_GROUPS.append(source_address)
        else:
            source_address = "any"
        element_source_address = ElementTree.SubElement(
            element_security_rule_entry, "source"
        )
        element_source_address_member = ElementTree.SubElement(
            element_source_address, "member"
        )
        element_source_address_member.text = source_address
        # Source zone
        element_source_zone = ElementTree.SubElement(
            element_security_rule_entry, "from"
        )
        for zone_name in get_zones(source_address):
            element_source_zone_member = ElementTree.SubElement(
                element_source_zone, "member"
            )
            element_source_zone_member.text = zone_name
        # Source user
        element_source_user = ElementTree.SubElement(
            element_security_rule_entry, "source-user"
        )
        element_source_user_member = ElementTree.SubElement(
            element_source_user, "member"
        )
        element_source_user_member.text = "any"
        # Destination address
        destination_address = rule.get("destination-address")
        if destination_address:
            REQUIRED_GROUPS.append(destination_address)
        else:
            destination_address = "any"
        element_destination_address = ElementTree.SubElement(
            element_security_rule_entry, "destination"
        )
        element_destination_address_member = ElementTree.SubElement(
            element_destination_address, "member"
        )
        element_destination_address_member.text = destination_address
        # Destination zone
        element_destination_zone = ElementTree.SubElement(
            element_security_rule_entry, "to"
        )
        for destination_zone in get_zones(destination_address):
            element_destination_zone_member = ElementTree.SubElement(
                element_destination_zone, "member"
            )
            element_destination_zone_member.text = destination_zone
        # Category (not used)
        element_category = ElementTree.SubElement(
            element_security_rule_entry, "category"
        )
        element_category_member = ElementTree.SubElement(element_category, "member")
        element_category_member.text = "any"
        # Application
        element_application = ElementTree.SubElement(
            element_security_rule_entry, "application"
        )
        if service.get("applications"):
            for application in service["applications"].split(","):
                element_application_member = ElementTree.SubElement(
                    element_application, "member"
                )
                element_application_member.text = application
        else:
            element_application_member = ElementTree.SubElement(
                element_application, "member"
            )
            element_application_member.text = "any"
        # Service
        element_service = ElementTree.SubElement(element_security_rule_entry, "service")
        element_service_member = ElementTree.SubElement(element_service, "member")
        if service.get("protocol"):
            element_service_member.text = service_name
        else:
            element_service_member.text = "application-default"
        # Source HIP (not used)
        element_source_hip = ElementTree.SubElement(
            element_security_rule_entry, "source-hip"
        )
        element_source_hip_member = ElementTree.SubElement(element_source_hip, "member")
        element_source_hip_member.text = "any"
        # Destination HIP (not used)
        element_destination_hip = ElementTree.SubElement(
            element_security_rule_entry, "destination-hip"
        )
        element_destination_hip_member = ElementTree.SubElement(
            element_destination_hip, "member"
        )
        element_destination_hip_member.text = "any"
        # Action (static)
        element_action = ElementTree.SubElement(element_security_rule_entry, "action")
        element_action.text = "allow"
        # Log settings (static)
        element_logsettings = ElementTree.SubElement(
            element_security_rule_entry, "log-setting"
        )
        element_logsettings.text = LOG_FORWARDING_PROFILE
        element_log_start = ElementTree.SubElement(
            element_security_rule_entry, "log-start"
        )
        element_log_start.text = "no"
        element_log_end = ElementTree.SubElement(element_security_rule_entry, "log-end")
        element_log_end.text = "yes"
        # Tag (static)
        element_tag = ElementTree.SubElement(
            element_security_rule_entry, "tag", loc="shared"
        )
        element_tag_member = ElementTree.SubElement(element_tag, "member", loc="shared")
        element_tag_member.text = rule_tag

        # <profile-setting loc="shared">
        #     <group loc="shared">
        #         <member loc="shared">corporate-standard-internet</member>
        #     </group>
        # </profile-setting>


# Checking network dependencies
print("*" * 78)
print("* Checking network dependencies")
for network_name in REQUIRED_GROUPS:
    if network_name not in PROVIDED_NETWORKS:
        raise MissingNetwork(network_name)

# Checking service dependencies
print("*" * 78)
print("* Checking service dependencies")
for service_name in REQUIRED_SERVICES:
    if service_name not in PROVIDED_SERVICES:
        raise MissingService(service_name)

# Sorting rules
print("*" * 78)
print("* Sorting rules")
security_rulebase = running_config.find(
    f".//vsys/entry[@name='{VSYS}']/rulebase/security/rules"
)
for rule_name in RULES_DETAILS:
    rule = security_rulebase.find(f".//entry[@name='{rule_name}']")
    security_rulebase.remove(rule)
    security_rulebase.insert(0, rule)

# Dumping configuration to file
print("*" * 78)
print(f"* Saving {CANDIDATE_CONFIG_FILE}")
with open(CANDIDATE_CONFIG_FILE, "w", encoding="utf-8") as fh:
    fh.write(print_xml(running_config))

# Pushing configuration file to firewall
print("*" * 78)
print(f"* Pushing {CANDIDATE_CONFIG_FILE}")
xapi.import_file(
    category="configuration", filename=CANDIDATE_CONFIG_FILE, file=CANDIDATE_CONFIG_FILE
)

# Load named configuration
print("*" * 78)
print(f"* Loading named configuration {CANDIDATE_CONFIG_FILE}")
cmd_xml = f"<load><config><from>{CANDIDATE_CONFIG_FILE}</from></config></load>"
xapi.op(cmd=cmd_xml)

# Commit
print("*" * 78)
print("* Commit")
xapi.commit(cmd="<commit></commit>", sync=True, interval=5, timeout=300)
print("*" * 78)


# def main():

# if __name__ == '__main__':
#     main()
