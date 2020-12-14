#!/usr/bin/env bash

if [[ -z "${VIDEOMAKER_TMP_DIR}" ]]; then
  echo "VIDEOMAKER_TMP_DIR environment variable not set."
  exit 1
else
  while true
  do
  echo "Starting File Cleaner Daemon"
  find $VIDEOMAKER_TMP_DIR/* -name "*" -mmin +120 -delete
  echo "File Cleaner Daemon going into hibernation"
  sleep 120000
  done
fi
