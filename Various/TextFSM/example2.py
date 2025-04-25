#!/usr/bin/env python

import textfsm
from pprint import pprint

with open("example2.textfsm") as fd_t, open("example2.raw") as fd_o:
    re_table = textfsm.TextFSM(fd_t)
    parsed_header = re_table.header
    parsed_output = re_table.ParseText(fd_o.read())

pprint(parsed_header)
pprint(parsed_output)
