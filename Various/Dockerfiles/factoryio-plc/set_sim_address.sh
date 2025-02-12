#!/bin/bash

CFG=/usr/local/src/OpenPLC/webserver/mbconfig.cfg
DB=/usr/local/src/OpenPLC/webserver/openplc.db

sed -i "s/device0.address.*/device0.address = \"${SIM}\"/" ${CFG}
sed -i "s/device1.address.*/device1.address = \"${SIM}\"/" ${CFG}
sed -i "s/device2.address.*/device2.address = \"${SIM}\"/" ${CFG}
sed -i "s/device3.address.*/device3.address = \"${SIM}\"/" ${CFG}
sed -i "s/device4.address.*/device4.address = \"${SIM}\"/" ${CFG}
sed -i "s/device5.address.*/device5.address = \"${SIM}\"/" ${CFG}

echo "UPDATE Slave_dev SET ip_address='${SIM}';" | sqlite3 ${DB}
