#!/usr/bin/env python
from getpass import getpass
import ssl
from pan import xapi

token = getpass("Token: ")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
fw = xapi.PanXapi(hostname="172.24.1.34", api_key=token, ssl_context=ctx)

# Commit (async)
cmd = "<commit></commit>"
fw.commit(cmd=cmd, sync=False)
root = fw.element_root
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
        fw.op(cmd=f"<show><jobs><id>{job_id}</id></jobs></show>", cmd_xml=False)
        root = fw.element_root
        result_el = root.find("./result/job/result")
        if result_el is not None:
            result = result_el.text
        progress = int(root.find("./result/job/progress").text)
        print(f"Job ID {job_id}: {progress}%")
        time.sleep(5)

    if result != "OK":
        print("ERROR: failed to commit.")
