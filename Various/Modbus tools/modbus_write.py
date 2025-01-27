#!/usr/bin/env python3

import argparse
from datetime import datetime
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException

REGISTER_TYPES = ["c", "coil", "h", "holding"]


def parse_set(items):
    """Validate a list of [type, address, value]."""
    output = []
    for item in items:
        if item[0] not in REGISTER_TYPES:
            raise ValueError
        output.append([item[0], int(item[1]), int(item[2])])
    return output


if __name__ == "__main__":
    """Main function."""
    started_timestamp = datetime.now().timestamp()
    error = False
    counter = 0

    parser = argparse.ArgumentParser(
        prog="modbus_monitor.py",
        description="Override the value of Modbus registries over time",
        epilog="Don't use it on production PLC. Use at your own risk.",
    )
    parser.add_argument("-i", "--ip", type=str, required=True, help="PLC IP address")
    parser.add_argument("-p", "--port", type=int, default=502, help="PLC TCP port")
    parser.add_argument(
        "-s",
        "--set",
        type=str,
        metavar=("type", "address", "value"),
        required=True,
        nargs=3,
        action="append",
        help="The registry to write (e.g. -s h 12 1)",
    )
    parser.add_argument("-u", "--unit", type=int, default=1, help="The slave unit")
    parser.add_argument("-k", "--kill", type=int, help="Seconds to wait before stop")
    args = parser.parse_args()

    # Validate args.set
    try:
        modbus_sets = parse_set(args.set)
    except ValueError:
        parser.error("argument -s/--set: expected c|h int int")

    # Connect to the PLC
    client = ModbusClient(args.ip, args.port)

    try:
        while True:
            now_timestamp = datetime.now().timestamp()

            # Write registries
            try:
                for item in modbus_sets:
                    if item[0] in ["c", "coil"]:
                        client.write_coil(item[1], bool(item[2]))
                    if item[0] in ["h", "holding"]:
                        client.write_register(item[1], item[2])
            except ConnectionException:
                error = True
                break

            counter = counter + 1
            if args.kill == 0:
                # Stop after 1 write
                break
            if args.kill is None:
                # Run forever
                continue
            if started_timestamp + args.kill < now_timestamp:
                # Stop after k seconds
                break

    except KeyboardInterrupt:
        # Terminate on CTRL+C
        pass

    # Disconnect from the PLC
    client.close()

    print(
        f"Wrote {counter} times in {round(now_timestamp - started_timestamp)} seconds"
    )

    if error:
        print("\nERROR: failed to connect to the PLC.\n")
