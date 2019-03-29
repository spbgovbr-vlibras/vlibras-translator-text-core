#!/usr/bin/env bash

LINUX_PACKAGES="python-dev python-setuptools python3-pip python-flask python-yaml python-numpy python-matplotlib"
HUNPOS_TAG="vlibras-libs/aelius/bin/hunpos-tag"

function install_system_dependencies {
  echo "Installing required system dependencies..."
  (apt --assume-yes install $LINUX_PACKAGES) || return 1
  return 0
}

function install_python_packages {
  echo -e "\nInstalling required python packages..."
  (python3 -m pip install -r translib-requirements.txt --upgrade) || return 1
  return 0
}

chmod 777 $HUNPOS_TAG &&\
install_system_dependencies &&\
install_python_packages &&\

echo -e "\nPreInstallation done!" || echo -e "\nPreInstallation failed!"
