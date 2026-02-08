#!/usr/bin/env python3
"""Prepare an IaC EVE-NG image based on Cisco IOSv."""

import atexit
import signal
import sys
import time
from utils import (
    send_cmd,
    expect_output,
    finalize_qemu_template,
    is_qemu_template_configured,
    start_qemu_node,
)
from vios_utils import NODE_CONFIG, NODE_CREDENTIALS
from _iosxe_utils import (
    login,
    poweroff,
    ERRORS,
    EXEC_PROMPT,
    CONFIG_PROMPT,
)


def config(template):
    if is_qemu_template_configured(template):
        print('The template has already been configured.')
        return

    # Starting node
    child = start_qemu_node(template, boot_from_cd=False, **NODE_CONFIG)

    # Close before exit
    def cleanup():
        """Cleanup before exit."""
        child.kill(signal.SIGTERM)

    atexit.register(cleanup)

    # Boot menu
    child.expect(rb'GNU GRUB', timeout=300)
    child.sendline('')

    # Skip initial configuration
    expect_output(
        child,
        'Would you like to enter the initial configuration dialog',
        ERRORS,
        timeout=300,
    )
    send_cmd(child, 'no')

    # Login
    login(child)

    # Configuration
    expect_output(child, EXEC_PROMPT, ERRORS)
    for line in [
        'configure terminal',
        f'username {NODE_CREDENTIALS["username"]} privilege 15 password {NODE_CREDENTIALS["password"]}',
        'hostname vios',
        'ip domain name example.com',
        'crypto key generate rsa modulus 2048',
        'ip ssh version 2',
        'line vty 0 15',
        'login local',
        'transport input ssh',
        'vrf definition mgmt',
        'address-family ipv4',
        'interface GigabitEthernet0/0',
        'vrf forwarding mgmt',
        'ip address dhcp',
        'no shutdown',
    ]:
        send_cmd(child, line)
        expect_output(child, CONFIG_PROMPT, ERRORS)
    send_cmd(child, 'end')

    # Save configuration
    expect_output(child, EXEC_PROMPT, ERRORS)
    send_cmd(child, 'write memory')
    expect_output(child, '[OK]', ERRORS)
    time.sleep(5)

    # Poweroff
    poweroff(child)

    # Finalize image
    finalize_qemu_template(template, NODE_CONFIG | NODE_CREDENTIALS)


if __name__ == '__main__':
    config(template=sys.argv[1])
