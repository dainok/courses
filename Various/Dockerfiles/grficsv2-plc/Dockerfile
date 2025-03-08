ARG VERSION_AD=66
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update
RUN apt-get -y install sudo dos2unix build-essential pkg-config bison flex autoconf automake libtool make nodejs git net-tools libmodbus-dev

# Install OpenPLC
RUN git clone https://github.com/thiagoralves/OpenPLC_v2.git /usr/local/src/OpenPLC
WORKDIR /usr/local/src/OpenPLC
RUN git checkout b7baafe0f83233ee8f0a668a3b3281761692a2ce
RUN rm -rf /usr/local/src/OpenPLC/.git
COPY --chmod=0755 build.sh /usr/local/src/OpenPLC
RUN /usr/local/src/OpenPLC/build.sh
COPY --chmod=0755 set_sim_address.sh /sbin

# Copy PLC program
COPY mbconfig.cfg /usr/local/src/OpenPLC/mbconfig.cfg
COPY simplified_te.st /usr/local/src/OpenPLC/st_files/simplified_te.st

# Compile PLC program
WORKDIR /usr/local/src/OpenPLC/matiec_src
RUN /usr/local/src/OpenPLC/iec2c -f -l -p -r -R -a /usr/local/src/OpenPLC/st_files/simplified_te.st
RUN mv -f POUS.c POUS.h LOCATED_VARIABLES.h VARIABLES.csv Config0.c Config0.h Res0.c /usr/local/src/OpenPLC/core
WORKDIR /usr/local/src/OpenPLC
RUN /usr/local/src/OpenPLC/build_core.sh

# Cleanup
RUN apt-get autoclean
RUN rm -rf /var/lib/apt/lists/* /var/tmp/* /tmp/*

# Startup
EXPOSE 502:502
EXPOSE 80:8080
ENTRYPOINT /sbin/set_sim_address.sh && /usr/bin/nodejs server.js
