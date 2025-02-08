#!/usr/bin/env bash
set -ex

# Install OpenPLC Editor
apt-get update
apt-get install -y git
rm -rf \
  /var/lib/apt/lists/* \
  /var/tmp/*
git clone https://github.com/thiagoralves/OpenPLC_Editor $HOME/OpenPLC_Editor
git -C $HOME/OpenPLC_Editor checkout dd2379ed36b530dde6f09902e84d11ef63e073d7
$HOME/OpenPLC_Editor/install.sh

# Cleanup for app layer
chown -R 1000:0 $HOME
find /usr/share/ -name "icon-theme.cache" -exec rm -f {} \;
if [ -z ${SKIP_CLEAN+x} ]; then
  rm -rf $HOME/OpenPLC_Editor/.git
  rm -rf $HOME/OpenPLC_Editor/editor/.git
  rm -rf $HOME/OpenPLC_Editor/matiec/.git
  apt-get autoclean
  rm -rf \
    /var/lib/apt/lists/* \
    /var/tmp/* \
    /tmp/*
fi
