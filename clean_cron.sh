#!/bin/sh
set -a
. /app/.env
set +a
/usr/local/bin/python /app/clean_downloads.py
