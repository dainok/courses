FROM ubuntu:22.04

# Install dependencies
RUN apt-get update
RUN apt-get -y install sudo dos2unix build-essential pkg-config bison flex autoconf automake libtool make nodejs git

# Install OpenPLC
RUN git clone https://github.com/thiagoralves/OpenPLC_v3 /usr/local/src/OpenPLC
WORKDIR /usr/local/src/OpenPLC
RUN git checkout c490ebf82c715c028bea3ad0a44db4a78033f35d
RUN ./background_installer.sh linux
COPY --chmod=0755 set_sim_address.sh /sbin

# Copy PLC programs
COPY openplc.db /usr/local/src/OpenPLC/webserver/openplc.db
COPY mbconfig.cfg /usr/local/src/OpenPLC/webserver/mbconfig.cfg
COPY chemical_program.st /usr/local/src/OpenPLC/webserver/st_files/chemical_program.st

# Cleanup
RUN apt-get autoclean
RUN rm -rf /var/lib/apt/lists/* /var/tmp/* /tmp/*

# Startup
EXPOSE 502:502
EXPOSE 80:8080
ENTRYPOINT /sbin/set_sim_address.sh && /usr/local/src/OpenPLC/start_openplc.sh
