"""Parameters and functions for Cisco IOS-XE."""

import pexpect
import signal
from utils import send_cmd, expect_output

UNPRIVILEGED_PROMPT = rb'[A-Za-z0-9._-]+>'
EXEC_PROMPT = rb'[A-Za-z0-9._-]+#'
CONFIG_PROMPT = rb'[A-Za-z0-9._-]+\((config[^)]*)\)#'
ERRORS = [
    '% Incomplete',
    '% Invalid input',
    '% Unknown command',
]


def login(child):
    """Login to a Cisco IOS-XE device using a pexpect.child."""
    expect_output(child, 'Press RETURN to get started', ERRORS, timeout=300)
    for _ in range(36):
        send_cmd(child, '')
        try:
            expect_output(child, UNPRIVILEGED_PROMPT, ERRORS, timeout=5)
            break
        except pexpect.TIMEOUT:
            pass
    send_cmd(child, 'enable')
    expect_output(child, EXEC_PROMPT, ERRORS)
    send_cmd(child, 'terminal length 0')


def poweroff(child):
    """Poweroff and stop a Cisco IOS-XE node."""
    send_cmd(child, '')
    expect_output(child, EXEC_PROMPT, ERRORS)
    child.kill(signal.SIGTERM)
