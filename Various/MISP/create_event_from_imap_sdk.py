#!/usr/bin/env python
"""Create an event on MISP from a phishing email."""

import imaplib
import logging
import email
import yaml
import urllib3
from pymisp import MISPEvent, MISPAttribute, PyMISP, MISPAttribute
from functions import parse_ioc_from_eml_body, parse_ioc_from_eml_headers, email_unpack

username = "bithorn.it@gmail.com"
password = "clti lnoy fymx jbex"
imap_url = "imap.gmail.com"

logging.getLogger("pymisp").setLevel(logging.WARNING)

with open("config.yml", "r") as fh:
    config = yaml.safe_load(fh)
with open("secrets.yml", "r") as fh:
    secrets = yaml.safe_load(fh)


# Disable SSL warning if cert validation is disabled
if not config["misp"]["verify_cert"]:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

misp = PyMISP(config["misp"]["url"], secrets["misp"]["key"], config["misp"]["verify_cert"], "json")


# Finding organization
org = None
for item in misp.organisations(pythonify=True):
    if item.name == config['event']["org"]:
        org = item
        break
if not org:
    raise(ValueError(f"Organization {config['event']['org']} not found"))


try:
    box = imaplib.IMAP4_SSL(imap_url)
    box.login(username, password)
    box.select('inbox')  # Connect to the inbox.
except Exception as e:
    logging.error("Connection failed: {}".format(e))
    raise

for mailbox in ["INBOX", "[Gmail]/Spam"]:
    box.select(mailbox=mailbox)
    typ, data = box.search(None, "ALL")
    for num in data[0].split():
        typ, msg = box.fetch(num, '(RFC822)')
        eml = email.message_from_bytes(msg[0][1])
        emails_unpacked = email_unpack(eml)
        # Analize attached emails only (drop the container)
        for email_unpacked in emails_unpacked[0:-1]:
            ioc_from_headers = parse_ioc_from_eml_headers(email_unpacked["headers"])

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
                misp_attributes.append({
                    "category": "Payload delivery",
                    "type": "email-src",
                    "distribution": 5,
                    "value": ioc_from_headers["src-email"],
                    "to_ids": True,
                })
            if "dst-email" in ioc_from_headers:
                misp_attributes.append({
                    "category": "Payload delivery",
                    "type": "email-dst",
                    "distribution": 0,
                    "value": ioc_from_headers["dst-email"],
                    "to_ids": False,
                })
            if "src-ip" in ioc_from_headers:
                misp_attributes.append({
                    "category": "Network activity",
                    "type": "ip-src",
                    "distribution": 5,
                    "value": ioc_from_headers["src-ip"],
                    "to_ids": True,
                })
            for payload in email_unpacked["payloads"]:
                if payload["content-type"].startswith("text/"):
                    ioc_from_body = parse_ioc_from_eml_body(payload["payload"])
                    if ioc_from_body.get("links"):
                        for link in ioc_from_body.get("links"):
                            misp_attributes.append({
                                "category": "Payload delivery",
                                "type": "link",
                                "distribution": 5,
                                "value": link,
                                "to_ids": True,
                            })
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

        # Delete email
        box.store(num, "+FLAGS", "\\Deleted")

    # Clear mailbox before moving to the next one
    box.expunge()
    box.close()
box.logout()

# https://github.com/MISP/mail_to_misp/blob/main/mail2misp/mail2misp.py
