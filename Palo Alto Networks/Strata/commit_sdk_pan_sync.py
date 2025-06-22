#!/usr/bin/env python
from getpass import getpass
import ssl
from pan import xapi

token = getpass("Token: ")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
fw = xapi.PanXapi(hostname="172.24.1.34", api_key=token, ssl_context=ctx)

# Commit (sync)
cmd = "<commit></commit>"
fw.commit(cmd=cmd, sync=True)
if "no changes to commit" in fw.status_detail:
    pass
elif fw.status != "success" or "successfully" not in fw.status_detail:
    print("ERROR: failed to commit."
