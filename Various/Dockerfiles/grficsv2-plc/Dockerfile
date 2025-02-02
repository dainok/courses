ARG VERSION=45
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update
RUN apt-get -y install sudo dos2unix build-essential pkg-config bison flex autoconf automake libtool make nodejs git net-tools libmodbus-dev

# Install OpenPLC
RUN git clone https://github.com/thiagoralves/OpenPLC_v2.git /usr/local/src/OpenPLC
WORKDIR /usr/local/src/OpenPLC
RUN git checkout f1a26459ce1fa470b8f3760163f178b5c4ad2826
COPY --chmod=0755 build.sh /usr/local/src/OpenPLC
RUN ./build.sh linux
COPY --chmod=0755 set_sim_address.sh /sbin

# Copy PLC programs
COPY mbconfig.cfg /usr/local/src/OpenPLC/core/mbconfig.cfg
COPY chemical_program.st /usr/local/src/OpenPLC/st_files/chemical_program.st

# Cleanup
RUN apt-get autoclean
RUN rm -rf /var/lib/apt/lists/* /var/tmp/* /tmp/*

# Startup
EXPOSE 502:502
EXPOSE 80:8080
ENTRYPOINT /sbin/set_sim_address.sh && /usr/bin/nodejs server.js
