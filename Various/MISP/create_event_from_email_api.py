#!/usr/bin/env python
"""Create an event on MISP from a phishing email."""

import sys
import logging
import urllib3
import requests
import yaml
import email
from functions import parse_ioc_from_eml_headers, parse_ioc_from_eml_body

logging.basicConfig(level=logging.INFO)

with open("config.yml", "r") as fh:
    config = yaml.safe_load(fh)
with open("secrets.yml", "r") as fh:
    secrets = yaml.safe_load(fh)

params = {
    "headers": {
        "Authorization": secrets["misp"]["key"],
        "Accept": "application/json",
    },
    "verify": config["misp"]["verify_cert"],
    "timeout": config["misp"]["timeout"],
}
params_post = {
    "headers": {
        "Authorization": secrets["misp"]["key"],
        "Accept": "application/json",
        "Content-Type": "application/json",
    },
    "verify": config["misp"]["verify_cert"],
    "timeout": config["misp"]["timeout"],
}


# Parsing email
with open(sys.argv[1]) as fh:
    eml = email.message_from_file(fh)

ioc_from_headers = parse_ioc_from_eml_headers(eml.items())


# Disable SSL warning if cert validation is disabled
if not config["misp"]["verify_cert"]:
    logging.warning("Disabling certificate check")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Finding organization
org_id = None
url = f"{config['misp']['url']}/organisations"
req = requests.post(url, **params)
req.raise_for_status()
for org in req.json():
    if org["Organisation"]["name"] == config["event"]["org"]:
        org_id = org["Organisation"]["id"]
        break
if not org_id:
    raise (ValueError(f"Organization {config['event']['org']} not found"))


# Creating event
data = {
    "org_id": org_id,
    "distribution": int(config["event"]["distribution"]),
    "info": f"{config['event']['title']} from {ioc_from_headers['src-email']}",
    "published": False,
    "analysis": 0,
    "threat_level_id": int(config["event"]["threat_level"]),
}
url = f"{config['misp']['url']}/events/add"
req = requests.post(url, json=data, **params_post)
req.raise_for_status()
event_id = req.json()["Event"]["id"]


# Tag event
data = {
    "event": event_id,
    "tag": "tlp:green",
}
url = f"{config['misp']['url']}/events/AddTag"
req = requests.post(url, json=data, **params_post)
req.raise_for_status()


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
    url = f"{config['misp']['url']}/attributes/add/{event_id}"
    req = requests.post(url, json=misp_attribute, **params_post)
    req.raise_for_status()
    attribute_id = req.json()["Attribute"]["id"]

    # Tag attribute
    if misp_attribute["type"] in ["email-dst"]:
        data = {
            "attribute": attribute_id,
            "tag": "tlp:amber",
        }
        url = f"{config['misp']['url']}/attributes/AddTag"
        req = requests.post(url, json=data, **params_post)
        req.raise_for_status()
