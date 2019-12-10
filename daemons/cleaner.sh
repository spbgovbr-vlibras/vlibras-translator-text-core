#!/usr/bin/env bash

if [[ ! -v "${VIDEOMAKER_TMP_DIR}" ]]; then
  echo "VIDEOMAKER_TMP_DIR environment variable not set."
  exit 1
else
  while true
  do
  echo "Starting garbage cleaner"
  find $VIDEOMAKER_TMP_DIR/* -name "*" -mmin +120 -delete
  echo "Garbage cleaner going into hibernation"
  sleep 120000
  done
fi
