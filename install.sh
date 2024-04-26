#!/usr/bin/env bash

LINUX_PACKAGES="build-essential default-jre libhunspell-dev git-lfs"

function install_system_dependencies {
  echo "Installing required system dependencies..."
  (sudo apt --assume-yes --no-install-recommends install $LINUX_PACKAGES) || return 1
  return 0
}

function install_python_packages {
  echo -e "\nInstalling required python packages..."
  (python -m pip install Cython -r requirements.txt) || return 1
  return 0
}

install_system_dependencies &&\
install_python_packages &&\

echo -e "\nSuccessful installation!" || echo -e "\nInstallation failed!"
