#!/usr/bin/env python
from getpass import getpass
import requests
import urllib3
import time
import xml.etree.ElementTree as ET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}

token = getpass("Token: ")

# Commit
url = f"https://172.25.10.4/api/?type=commit&cmd=<commit></commit>&key={token}"
req = requests.get(url, headers=headers, verify=False)
req.raise_for_status()
root = ET.fromstring(req.text)
job = root.find("./result/job")
job_id = None
if job is not None:
    # msg = root.find("./result/msg")
    job_id = job.text
else:
    msg = root.find("./msg")


# Wait for job
if job_id:
    progress = 0
    result = None
    while progress < 100:
        url = f"https://172.24.1.34/api/?type=op&cmd=<show><jobs><id>{job_id}</id></jobs></show>&key={token}"
        req = requests.get(url, headers=headers, verify=False)
        req.raise_for_status()
        root = ET.fromstring(req.text)
        result_el = root.find("./result/job/result")
        if result_el is not None:
            result = result_el.text
        progress = int(root.find("./result/job/progress").text)
        print(f"Job ID {job_id}: {progress}%")
        time.sleep(5)

    if result != "OK":
        print("ERROR: failed to commit.")
