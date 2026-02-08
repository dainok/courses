#!/usr/bin/env python3
"""Test an IaC EVE-NG image based on Cisco IOSv."""

import atexit
import paramiko
import pexpect
import re
import signal
import sys
from utils import (
    send_cmd,
    expect_output,
    start_qemu_node,
    is_qemu_template_configured,
)
from vios_utils import NODE_CONFIG, NODE_CREDENTIALS
from _iosxe_utils import (
    login,
    poweroff,
    ERRORS,
    EXEC_PROMPT,
)


def test(template=None):
    if not is_qemu_template_configured(template):
        raise RuntimeError('Template is not configured.')

    # Starting node
    child = start_qemu_node(
        template, boot_from_cd=False, mgmt_switch='nat0', **NODE_CONFIG
    )

    # Close before exit
    def cleanup():
        """Cleanup before exit."""
        child.kill(signal.SIGTERM)

    atexit.register(cleanup)

    # Boot menu
    child.expect(rb'GNU GRUB', timeout=300)
    child.sendline('')

    # Login
    login(child)

    # Wait for IP address
    ip_address = None
    expect_output(child, EXEC_PROMPT, ERRORS)
    for _ in range(10):
        try:
            send_cmd(child, 'show interfaces GigabitEthernet0/0')
            _, output = expect_output(child, EXEC_PROMPT, ERRORS)
            match = re.search(rb'Internet address is (\d{1,3}(?:\.\d{1,3}){3})', output)
            if match:
                ip_address = match.group(1).decode()
                break
        except pexpect.TIMEOUT:
            pass

    if not ip_address:
        raise RuntimeError('IP Address not found')

    # Test reachability
    send_cmd(child, 'ping vrf mgmt 8.8.8.8 repeat 5 source GigabitEthernet0/0')
    expect_output(child, '!!', ERRORS)

    # Test login
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(
            hostname=ip_address,
            username=NODE_CREDENTIALS['username'],
            password=NODE_CREDENTIALS['password'],
            timeout=10,
            look_for_keys=False,
        )
    except Exception:
        raise RuntimeError('Cannot connect via SSH')

    # Poweroff
    poweroff(child)


if __name__ == '__main__':
    test(template=sys.argv[1])
