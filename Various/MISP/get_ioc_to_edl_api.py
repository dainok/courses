#!/usr/bin/env python
"""Export an EDL of IP addresses."""

import logging
import urllib3
from datetime import datetime, timedelta
import requests
from http.server import BaseHTTPRequestHandler,HTTPServer
import yaml
import time

logging.getLogger("pymisp").setLevel(logging.WARNING)

with open("config.yml", "r") as fh:
    config = yaml.safe_load(fh)
with open("secrets.yml", "r") as fh:
    secrets = yaml.safe_load(fh)

params_post = {
    "headers": {
        "Authorization": secrets["misp"]["key"],
        "Accept": "application/json",
        "Content-Type": "application/json",
    },
    "verify": config["misp"]["verify_cert"],
    "timeout": config["misp"]["timeout"],
}

last_days = datetime.now() - timedelta(days=config["export"]["last_days"])
last_days_unix = int(time.mktime(last_days.timetuple()))

# Disable SSL warning if cert validation is disabled
if not config["misp"]["verify_cert"]:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Search for IP addresses
ip_list = []
data = {
    "controller": "attributes",
    "type": ["ip-src", "ip-dst"],
    "to_ids": True,
    "deleted": False,
    "timestamp": last_days_unix,
    "order": "timestamp desc",
    "limit": config["export"]["last_ioc"],
}
url = f"{config['misp']['url']}/attributes/restSearch"
req = requests.post(url, json=data, **params_post)
req.raise_for_status()
print("Most recent IoC: ", time.ctime(int(req.json()["response"]["Attribute"][0]["timestamp"])))
print("Most old IoC:    ", time.ctime(int(req.json()["response"]["Attribute"][-1]["timestamp"])))


# Parse the result
for item in req.json()["response"]["Attribute"]:
    if item["value"] not in ip_list:
        ip_list.append(item["value"])
ioc_page = "\n".join(ip_list).encode("utf-8")
print(f"Exporting {len(ip_list)} IP addresses")

class pageHandler(BaseHTTPRequestHandler):
    """Handle webserver requests."""
    def do_GET(self):
        """Handle GET requests."""
        self.send_response(200)
        self.send_header("Content-type","text/plain")
        self.end_headers()
        self.wfile.write(ioc_page)
        return

try:
    # Start the webserver
    server = HTTPServer(("0.0.0.0", config["export"]["port"]), pageHandler)
    print(f"Webserver started on port {config['export']['port']}")
    server.serve_forever()
except KeyboardInterrupt:
    # Stop the webserver
    print("Webserver stopped")
    server.socket.close()
