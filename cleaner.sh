#!/usr/bin/env bash

while true
do
echo "Starting cleaner finder"
find /video/translator/* -name "*" -mmin +120 -delete
echo "Sleeping cleanerfinder"
sleep 120000
done

