#!/bin/bash

# all access token
INFLUX_TOKEN="6yInsxircPx7vzxZvIyu7thmH5uocacAuWg6ufDcLr5AHNE6RnBtm9aSG9lktaJbUIUlifjxsWK0_nMUAAJepQ=="

influx_dir="/misc/subdata/influxdb2/"
backup_dir="$influx_dir/backup"
backup_file="$influx_dir/influxdb2-backup.tar.gz"

rm -rf $backup_dir
influx backup $backup_dir
tar -czf $backup_file $backup_dir
rm -rf $backup_dir

/misc/software/slow-monitor/script/save-csv-root.py
