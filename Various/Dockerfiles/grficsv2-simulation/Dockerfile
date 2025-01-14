FROM ubuntu:xenial

# Update repos and install packages
RUN apt-get update
RUN apt-get install -y libjsoncpp-dev liblapacke-dev python-pymodbus build-essential apache2 php libapache2-mod-php
RUN apt-get install -y sudo

# Build the app
COPY . /opt/simulation
WORKDIR /opt/simulation/simulation
RUN make
RUN rm /var/www/html/index.html
RUN ln -s /opt/simulation/web_visualization/* /var/www/html

# Startup
EXPOSE 80:80
EXPOSE 5020:5020
EXPOSE 5021:5021
EXPOSE 5022:5022
EXPOSE 5023:5023
EXPOSE 5024:5024
EXPOSE 5025:5025
ENTRYPOINT service apache2 start && ./remote_io/modbus/run_all.sh && ./simulation
