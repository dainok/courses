#!/usr/bin/env python
"""Create an event on MISP from a phishing email."""

import sys
import logging
import urllib3
from pymisp import MISPEvent, MISPAttribute, PyMISP, MISPAttribute
import yaml
import email
from functions import parse_ioc_from_eml_headers, parse_ioc_from_eml_body

logging.getLogger("pymisp").setLevel(logging.WARNING)

with open("config.yml", "r") as fh:
    config = yaml.safe_load(fh)
with open("secrets.yml", "r") as fh:
    secrets = yaml.safe_load(fh)


# Parsing email
with open(sys.argv[1]) as fh:
    eml = email.message_from_file(fh)

ioc_from_headers = parse_ioc_from_eml_headers(eml.items())
ioc_from_body = parse_ioc_from_eml_body(eml.get_payload())


# Disable SSL warning if cert validation is disabled
if not config["misp"]["verify_cert"]:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

misp = PyMISP(
    config["misp"]["url"], secrets["misp"]["key"], config["misp"]["verify_cert"], "json"
)


# Finding organization
org = None
for item in misp.organisations(pythonify=True):
    if item.name == config["event"]["org"]:
        org = item
        break
if not org:
    raise (ValueError(f"Organization {config['event']['org']} not found"))


# Creating event
event = MISPEvent()
event.orgc = org
event.distribution = int(config["event"]["distribution"])
event.info = f"{config['event']['title']} from {ioc_from_headers['src-email']}"
event.published = False
event.analysis = 0
event.threat_level_id = int(config["event"]["threat_level"])
event = misp.add_event(event, pythonify=True)


# Tag event
misp.tag(event, "tlp:green")


# Creating attributes
misp_attributes = []
if "src-email" in ioc_from_headers:
    misp_attributes.append(
        {
            "category": "Payload delivery",
            "type": "email-src",
            "distribution": 5,
            "value": ioc_from_headers["src-email"],
            "to_ids": True,
        }
    )
if "dst-email" in ioc_from_headers:
    misp_attributes.append(
        {
            "category": "Payload delivery",
            "type": "email-dst",
            "distribution": 0,
            "value": ioc_from_headers["dst-email"],
            "to_ids": False,
        }
    )
if "src-ip" in ioc_from_headers:
    misp_attributes.append(
        {
            "category": "Network activity",
            "type": "ip-src",
            "distribution": 5,
            "value": ioc_from_headers["src-ip"],
            "to_ids": True,
        }
    )
for eml_body in eml.get_payload():
    ioc_from_body = parse_ioc_from_eml_body(eml_body)
    if ioc_from_body.get("links"):
        for link in ioc_from_body.get("links"):
            misp_attributes.append(
                {
                    "category": "Payload delivery",
                    "type": "link",
                    "distribution": 5,
                    "value": link,
                    "to_ids": True,
                }
            )
for misp_attribute in misp_attributes:
    attribute = MISPAttribute()
    attribute.category = misp_attribute["category"]
    attribute.type = misp_attribute["type"]
    attribute.distribution = misp_attribute["distribution"]
    attribute.value = misp_attribute["value"]
    attribute.to_ids = misp_attribute["to_ids"]
    misp.add_attribute(event=event, attribute=attribute, pythonify=True)

    # Tag attribute
    if misp_attribute["type"] in ["email-dst"]:
        misp.tag(attribute, "tlp:amber")
