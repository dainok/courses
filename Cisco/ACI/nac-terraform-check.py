#!/usr/bin/env python3
"""Terraform import checker for Cisco APIC using NaC modeling."""
import re
import subprocess

EXCLUDED_ATTRIBUTES = ["annotation", "nameAlias", "userdom", "name"]

# Terraform import
cmd = "terraform plan -no-color"
result = subprocess.run(cmd.split(), capture_output=True, text=True)
if result.returncode != 0:
    print("CMD:", cmd)
    print("RC:", result.returncode)
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    raise

pattern = re.compile(r'^\s*[+-]\s+"([^"]+)"\s*=')
changed_attributes = set()
for line in result.stdout.splitlines():
    match = pattern.search(line)
    if match:
        changed_attribute = match.group(1)
        if changed_attribute not in EXCLUDED_ATTRIBUTES:
            changed_attributes.add(changed_attribute)

for attribute in changed_attributes:
    cmd = f"fgrep {attribute} /Users/dainese/src/3RDPARTY/terraform-aci-nac-aci -R"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    if result.returncode == 0:
        print(cmd)
        print(f"Attribute {attribute} should be supported")
