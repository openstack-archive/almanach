#!/usr/bin/env bash
set -e

echo "Entering the entrypoint"
if [ "$1" = 'api' ]; then
  echo "Starting the api"
  almanach api /etc/almanach.cfg --host 0.0.0.0
elif [ "$1" = 'collector' ]; then
  echo "Starting the collector"
  almanach collector /etc/almanach.cfg
fi

exec "$@"