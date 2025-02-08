ARG VERSION_AD=18
ARG BASE_TAG="1.16.0"
ARG BASE_IMAGE="core-ubuntu-jammy"
FROM kasmweb/$BASE_IMAGE:$BASE_TAG
USER root

ENV HOME=/home/kasm-default-profile
ENV STARTUPDIR=/dockerstartup
ENV INST_SCRIPTS=$STARTUPDIR/install
WORKDIR $HOME

######### Customize Container Here ###########

RUN usermod -aG sudo kasm-user
COPY ./src/ubuntu/install/openplc-editor $INST_SCRIPTS/openplc-editor/
RUN bash $INST_SCRIPTS/openplc-editor/install_openplc-editor.sh  && rm -rf $INST_SCRIPTS/openplc-editor/

# Include projects
COPY Documents /home/kasm-user/Documents

# Add additional packages
RUN apt-get update
RUN apt-get install -y epiphany-browser

# Cleaning
RUN apt-get autoclean
RUN rm -rf /var/lib/apt/lists/* /var/tmp/* /tmp/*

######### End Customizations ###########

RUN chown 1000:0 $HOME

ENV HOME=/home/kasm-user
WORKDIR $HOME
RUN mkdir -p $HOME && chown -R 1000:0 $HOME

USER 1000
