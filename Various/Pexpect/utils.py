"""Common functions for config scripts."""

import json
import os
import sys
import time
import pexpect

GREEN = '\033[92m'
RESET = '\033[0m'


class TeeLogger:
    """Print output in stdout and in file."""

    def __init__(self, log_file=None):
        self.raw = None
        if log_file:
            self.raw = open(log_file, 'wb')

    def write(self, data):
        if isinstance(data, bytes):
            if self.raw:
                self.raw.write(data)
                self.raw.flush()
            text = data.decode(errors='ignore')
        else:
            if self.raw:
                self.raw.write(data.encode(errors='ignore'))
                self.raw.flush()
            text = data

        sys.stdout.write(text)
        sys.stdout.flush()

    def flush(self):
        if self.raw:
            self.raw.flush()
        sys.stdout.flush()


def send_cmd(child, text, delay=1):
    """Send command using to pexpect process."""
    time.sleep(delay)
    print(f'{GREEN}{text}⮐{RESET}')
    child.send(text.encode() + b'\r')


def expect_output(child, expected, errors, timeout=10):
    if isinstance(expected, (bytes, str)):
        expected = [expected]

    patterns = list(expected) + list(errors)
    output = b''

    try:
        res = child.expect(patterns, timeout=timeout)
        output += child.before

        if res < len(expected):
            while True:
                # Consume the rest of the line
                try:
                    child.expect(rb'.+', timeout=0.1)
                    output += child.before
                except pexpect.TIMEOUT:
                    break
            return res, output

        err = errors[res - len(expected)]
        raise RuntimeError(f'Command error {err!r} (expected={expected})')
    except pexpect.TIMEOUT:
        raise pexpect.TIMEOUT(
            f'Timeout occurred (expected={expected}, timeout={timeout})'
        )
    except pexpect.EOF:
        raise RuntimeError('EOF reached (expected={expected})')


def is_qemu_template_configured(template):
    """Return true if a template has already been prepared."""
    template = template.rstrip('/')
    template = os.path.basename(template)
    template_dir = f'/opt/unetlab/addons/qemu/{template}'
    if os.path.exists(f'{template_dir}/config.json'):
        return True
    return False


def get_start_qemu_node_cmd(
    template,
    qemu_version='4.1.0',
    cpu_count=1,
    ram_count=512,
    net_driver='virtio-net-pci',
    hdd_driver='virtio',
    boot_from_cd=False,
    mgmt_switch=None,
):
    """Return command to start a QEMU node."""
    template = template.rstrip('/')
    template = os.path.basename(template)
    template_dir = f'/opt/unetlab/addons/qemu/{template}'

    # Building CMD
    cmd = f'/opt/qemu-{qemu_version}/bin/qemu-system-x86_64 -serial stdio -nographic -no-user-config -nodefaults -rtc base=utc -machine type=pc,accel=kvm -cpu host -enable-kvm -smp {cpu_count} -m {ram_count}'
    if mgmt_switch:
        cmd += (
            f' -netdev bridge,id=net0,br={mgmt_switch} -device {net_driver},netdev=net0'
        )
    else:
        cmd += f' -device {net_driver}'
    if boot_from_cd:
        cmd += f' -cdrom {template_dir}/cdrom.iso -boot dc'
    if hdd_driver == 'virtio':
        cmd += f' -drive file={template_dir}/virtioa.qcow2,if=virtio,bus=0,unit=0,cache=none'
    elif hdd_driver == 'sata':
        cmd += f' -device ahci,id=ahci0,bus=pci.0 -drive file={template_dir}/sataa.qcow2,if=none,id=drive-sata-disk0,format=qcow2,cache=none -device ide-drive,bus=ahci0.0,drive=drive-sata-disk0,id=drive-sata-disk0,bootindex=1 -bios /opt/qemu/share/qemu/OVMF-sata.fd'
    print(f'{GREEN}Starting: {cmd}{RESET}')
    return cmd


def finalize_qemu_template(template, data):
    """Finalize a QEMU image writing credentials."""
    template = template.rstrip('/')
    template = os.path.basename(template)
    template_dir = f'/opt/unetlab/addons/qemu/{template}'
    with open(f'{template_dir}/config.json', 'w') as fh:
        json.dump(data, fh, indent=4)


def start_qemu_node(template, **kwargs):
    """Start a QEMU node from a template and return a pexepct.child."""
    # Checking template
    cmd = get_start_qemu_node_cmd(template, **kwargs)
    child = pexpect.spawn(
        cmd,
        encoding=None,
        timeout=10,
        echo=False,
    )
    child.logfile = TeeLogger()
    return child
