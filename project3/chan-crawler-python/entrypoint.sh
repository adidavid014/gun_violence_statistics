#!/usr/bin/sh

sqlx database create
sqlx migrate run

wait-for-it.sh postgres:5432 -- python /chan_app/chan_crawler.py &

tail -f /dev/null