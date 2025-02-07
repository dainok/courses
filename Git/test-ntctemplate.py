#!/usr/bin/env python3

import pprint
from ntc_templates.parse import parse_output

platform = "hp_procurve"
command = "show mac-address"
raw_output_file = "tests/hp_procurve/show_mac-address/hp_procurve_show_mac-address2.raw"

data = open(raw_output_file, "r").read()
parsed_output = parse_output(platform=platform, command=command, data=data)

pprint.pprint(parsed_output)
