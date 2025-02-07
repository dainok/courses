#!/usr/bin/env bash
set -ex

# Install VirtuaPlant
apt-get update
apt-cache search python-pip
apt-get install -y git wget virtualenv gir1.2-gtk-3.0 python-pygame python-gobject python-dev build-essential python-pip-whl python-gi
rm -rf \
  /var/lib/apt/lists/* \
  /var/tmp/*
git clone https://github.com/dainok/virtuaplant $HOME/virtuaplant
git -C $HOME/virtuaplant checkout 5c67f2e46938e839add9846142d1b198375afd9c

# Download PIP modules
cd $HOME
wget https://files.pythonhosted.org/packages/76/9a/ed7a9cabefd919c861249d39d11111d5d8fba2e8d0b2a1bce7ee8933a8fd/Twisted-15.0.0.tar.bz2
wget https://files.pythonhosted.org/packages/29/04/ed171a21850aa1ff9b683b061f1168b3dc6461c6c7c4550b238e97fef197/zope.interface-4.1.2.tar.gz
wget https://files.pythonhosted.org/packages/6f/ad/86448942ad49c5fe05bfdf7ebc874807f521dfcca5ee543afaca2974ad5a/argparse-1.2.1.tar.gz
wget https://files.pythonhosted.org/packages/8a/4f/49f801acde031de47223a7541763b2f5ccedf88cb001694b0d3570e9dc15/distribute-0.6.24.tar.gz
wget https://files.pythonhosted.org/packages/5b/7a/a84f94be2c65544ceedaec116e667260b39eae39ca9b8a7eac9793505588/pyasn1-0.1.7.tar.gz
wget https://files.pythonhosted.org/packages/60/db/645aa9af249f059cc3a368b118de33889219e0362141e75d4eaf6f80f163/pycrypto-2.6.1.tar.gz
wget https://files.pythonhosted.org/packages/69/93/be20dedcb68ea15daad042edcc05cd71655c93bd2db9c81cf67e284845a5/pymodbus-1.2.0.tar.gz
wget https://files.pythonhosted.org/packages/20/2f/3cda672816ad399f901a49ecf6f3a038a06c6853e31596b40c0780c00f29/pymunk-4.0.0.zip
wget https://files.pythonhosted.org/packages/df/c9/d9da7fafaf2a2b323d20eee050503ab08237c16b0119c7bbf1597d53f793/pyserial-2.7.tar.gz
wget https://files.pythonhosted.org/packages/41/9e/309259ce8dff8c596e8c26df86dbc4e848b9249fd36797fd60be456f03fc/wsgiref-0.1.2.zip

# Create Python environment
virtualenv --python=python2.7 --system-site-packages venv
source venv/bin/activate
pip install zope.interface-4.1.2.tar.gz
pip install Twisted-15.0.0.tar.bz2
pip install argparse-1.2.1.tar.gz
pip install distribute-0.6.24.tar.gz
pip install pyasn1-0.1.7.tar.gz
pip install pycrypto-2.6.1.tar.gz
pip install pyserial-2.7.tar.gz
pip install pymodbus-1.2.0.tar.gz
pip install pymunk-4.0.0.zip
pip install wsgiref-0.1.2.zip

# Cleanup for app layer
chown -R 1000:0 $HOME
find /usr/share/ -name "icon-theme.cache" -exec rm -f {} \;
if [ -z ${SKIP_CLEAN+x} ]; then
  apt-get autoclean
  rm -rf \
    /var/lib/apt/lists/* \
    /var/tmp/* \
    /tmp/*
  rm -rf $HOME/virtuaplant/.git
  rm -rf $HOME/*.zip $HOME/*.tar.gz $HOME/*.bz2
fi
