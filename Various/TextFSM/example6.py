#!/usr/bin/env python

import textfsm
from pprint import pprint

with open("example6.textfsm") as fd_t, open("example6.raw") as fd_o:
    re_table = textfsm.TextFSM(fd_t)
    parsed_header = re_table.header
    parsed_output = re_table.ParseText(fd_o.read())

pprint(parsed_header)
pprint(parsed_output)
