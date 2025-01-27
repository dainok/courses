#!/usr/bin/env python3

import argparse
import time
import math
from datetime import datetime
from tabulate import tabulate
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException

REGISTER_TYPES = ["discrete", "coil", "input", "holding"]

if __name__ == "__main__":
    """Main function."""
    started_at = datetime.now()
    started_timestamp = started_at.timestamp()
    error = False

    parser = argparse.ArgumentParser(
        prog="modbus_monitor.py",
        description="Monitor Modbus registries over time",
        epilog="Don't use it on production PLC. Use at your own risk.",
    )
    parser.add_argument("-i", "--ip", type=str, required=True, help="PLC IP address")
    parser.add_argument("-p", "--port", type=int, default=502, help="PLC TCP port")
    parser.add_argument(
        "-t",
        "--type",
        type=str,
        required=True,
        choices=REGISTER_TYPES,
        help="Register type",
    )
    parser.add_argument(
        "-s", "--start", type=int, default=0, help="The starting address"
    )
    parser.add_argument(
        "-c", "--count", type=int, default=16, help="The number of registers"
    )
    parser.add_argument("-u", "--unit", type=int, default=1, help="The slave unit")
    parser.add_argument(
        "-w", "--wait", type=int, default=1, help="Seconds between requests"
    )
    parser.add_argument("-k", "--kill", type=int, help="Seconds to wait before stop")
    args = parser.parse_args()
    round_count = math.ceil(args.count / 8) * 8

    # Connect to the PLC
    client = ModbusClient(args.ip, args.port)

    # Prepare the header
    header = ["Time"] + list(range(args.start, args.start + round_count))
    data = []
    print(header)

    try:
        while True:
            now = datetime.now()
            now_timestamp = now.timestamp()
            if args.kill is not None and started_timestamp + args.kill < now_timestamp:
                # Stop after k seconds
                break

            # Get registries
            try:
                if args.type == "discrete":
                    req = client.read_discrete_inputs(
                        args.start, count=round_count, unit=args.unit
                    )
                    reg = req.bits
                if args.type == "coil":
                    req = client.read_coils(
                        args.start, count=round_count, unit=args.unit
                    )
                    reg = req.bits
                if args.type == "input":
                    req = client.read_input_registers(
                        args.start, count=round_count, unit=args.unit
                    )
                    reg = req.registers
                if args.type == "holding":
                    req = client.read_holding_registers(
                        args.start, count=round_count, unit=args.unit
                    )
                    reg = req.registers
            except ConnectionException:
                error = True
                break

            # Prepare the output
            output = [f"{now.hour}:{now.minute}:{now.second}"] + reg
            data.append(output)
            print(output)

            time.sleep(args.wait)
    except KeyboardInterrupt:
        # Terminate on CTRL+C
        pass

    # Disconnect from the PLC
    client.close()

    # Calculate min and max
    if args.type in ["input", "holding"]:
        min = ["Min"] + list([None] * (round_count))
        max = ["Max"] + list([None] * (round_count))
        for line in data:
            for i in range(1, round_count + 1):
                if min[i] is None:
                    min[i] = line[i]
                if max[i] is None:
                    max[i] = line[i]
                if line[i] < min[i]:
                    min[i] = line[i]
                if line[i] > max[i]:
                    max[i] = line[i]
        data.append(min)
        data.append(max)

    # TODO: Check if registers change
    # if args.type in ["discrete", "coil"]:
    #     change = ["Change?"] + list([False] * (round_count))
    #     for line in data:
    #         for i in range(1, round_count + 1):

    # Display output
    print("\n")  # Clear the line
    print(tabulate(data, headers=header))

    if error:
        print("\nERROR: failed to connect to the PLC.\n")
