#!/usr/bin/env python
import os
from pprint import pprint
from api import APIClient

tenant_id = os.environ.get("SCM_TENANT_ID")
username = os.environ.get("SCM_USERNAME")
password = os.environ.get("SCM_PASSWORD")

client = APIClient(
    tenant_id=tenant_id,
    username=username,
    password=password,
)
req = client.get("/config/setup/v1/devices")
req.raise_for_status()
pprint(req.json())
