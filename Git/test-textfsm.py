#!/usr/bin/env python3

import textfsm
import pprint

template_file = "ntc_templates/templates/hp_procurve_show_mac-address.textfsm"
raw_output_file = "tests/hp_procurve/show_mac-address/hp_procurve_show_mac-address2.raw"

with open(template_file) as fd_t, open(raw_output_file) as fd_o:
    re_table = textfsm.TextFSM(fd_t)
    parsed_header = re_table.header
    parsed_output = re_table.ParseText(fd_o.read())

pprint.pprint(parsed_header)
pprint.pprint(parsed_output)
