#!/usr/bin/env python
from getpass import getpass
from panos.firewall import Firewall, FirewallCommit

token = getpass("Token: ")
fw = Firewall("172.24.1.34", api_key=token)

# Commit
job_id = fw.commit()
if job_id:
    result = fw.syncjob(job_id)
    if not result["success"]:
        print("ERROR: failed to commit.")
