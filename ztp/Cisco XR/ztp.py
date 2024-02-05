#!/usr/bin/env python3
"""
HTTP server to deliver files required by Cisco XR ZTP process.

/ztp -> deliver the Bash script
/config -> deliver the basic config requested by the above Bash script

See the README.md to start the web server.
"""

import yaml
from slugify import slugify
from flask import Flask, request
from jinja2 import Template, select_autoescape

# Loading secrets
with open("secrets.yml", "r") as fh:
    SECRETS = yaml.safe_load(fh)

# Loading Ansible configuration
with open("config.yml", "r") as fh:
    CONFIG = yaml.safe_load(fh)

JINJA_AUTOESCAPE = select_autoescape(
    enabled_extensions=["html"], default_for_string=True
)

app = Flask(__name__)


@app.route("/ztp", methods=["GET"])
def get_ztp():
    """Return ZTP bash script to be loaded during Cisco XR boot."""
    with open("ztp.j2", "r") as fh:
        ztp_script_template = fh.read()

    url = request.url_root + "config"
    output = Template(ztp_script_template, autoescape=JINJA_AUTOESCAPE).render(url=url)

    return output


@app.route("/config", methods=["POST"])
def get_config():
    """Return Cisco XR config to be downloaded in the ZTP phase."""
    if request.method == "POST":
        data = {
            "username": SECRETS["username"],
            "password": SECRETS["password"],
            "hostname": slugify(request.form.get("serial")),
            "domain": CONFIG["domain"],
            "oob_address": CONFIG["oob_address"],
            "oob_mask": CONFIG["oob_mask"],
            "oob_gateway": CONFIG["oob_gateway"],
            "oob_interface": CONFIG["oob_interface"],
            "oob_vrf": CONFIG["oob_vrf"],
            "serial": request.form.get("serial"),
            "model": request.form.get("model"),
        }
        print(f' * Request for {data.get("model")} with SN {data.get("serial")}')
        with open("config.j2", "r") as fh:
            config_template = fh.read()

        output = Template(config_template, autoescape=JINJA_AUTOESCAPE).render(**data)

        return output
