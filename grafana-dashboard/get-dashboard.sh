#!/bin/bash

set -e

api_key=$(<api-token)
grafana_host=db-hyps
port=3000

dashboard_list=$(curl -s -H "Authorization: Bearer $api_key" "http://$grafana_host:$port/api/search?type=dash-db")

for uid in $(echo "$dashboard_list" | jq -r '.[].uid'); do
    dashboard_json=$(curl -s -H "Authorization: Bearer $api_key" \
                          -H "Content-Type: application/json" \
                          "http://$grafana_host:$port/api/dashboards/uid/$uid")
    dashboard_title=$(echo "$dashboard_json" | jq -r '.dashboard.title')
    safe_title=$(echo "$dashboard_title" | tr -cd '[:alnum:]-_')
    output_file="${safe_title}.json"
    echo "$dashboard_json" > "$output_file"
    echo "Saved dashboard UID: $uid as $output_file"
done
