#!/usr/bin/env python

from datetime import datetime, timedelta, timezone
from influxdb_client import InfluxDBClient
import numpy as np
import os
import pandas as pd
import uproot

output_dir = '/misc/subdata/influxdb2'

url = 'http://localhost:8086'
token = '-iT93bQ-4tDWCQVR42vBoRbE58wzxIWsDYB6S4vfgR9BiiRSrfoR90OpaYXtaBuEkAPgfrv0YrFtqQPFFn81Vg=='
org = 'hyps'

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

buckets_api = client.buckets_api()
buckets = buckets_api.find_buckets().buckets
bucket_names = [bucket.name for bucket in buckets]

JST = timezone(timedelta(hours=9))
now_jst = datetime.now(JST)
yesterday_start = (now_jst - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
yesterday_end = (yesterday_start + timedelta(days=1))
yesterday_date = yesterday_start.strftime('%Y-%m%d')

start_iso = yesterday_start.strftime("%Y-%m-%dT%H:%M:%S%z")
end_iso = yesterday_end.strftime("%Y-%m-%dT%H:%M:%S%z")
start_iso = start_iso[:-2] + ":" + start_iso[-2:]
end_iso = end_iso[:-2] + ":" + end_iso[-2:]

print(start_iso)
print(end_iso)

for b in bucket_names:
  print('='*80)
  print(f'Bucket name: {b}')
  query = f"""
from(bucket: "{b}")
  |> range(start: {start_iso}, stop: {end_iso})
//  |> range(start: -1m)
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
//  |> experimental.setTimezone(timezone: "Asia/Tokyo")
  |> sort(columns: ["_time"], desc: false)
"""
  # |> range(start: time(v: today() - 1d), stop: time(v: today()))

  df = query_api.query_data_frame(query)
  if isinstance(df, list):
    df = pd.concat(df, ignore_index=True)
  if len(df) == 0:
    print('Skipped empty bucket')
    continue
  output_file = os.path.join(output_dir, f'{b}-{yesterday_date}.csv.gz')
  for t in ['_start', '_stop', '_time']:
    df[t] = pd.to_datetime(df[t]).dt.tz_convert("Asia/Tokyo")
  df = df.sort_values(by=["_time", 'table'], ascending=[True, True])
  df.to_csv(output_file, index=False, compression='gzip')
  print(df)
  print(f'Saved {output_file}')

  # output_file = f"{b}.root"
  # with uproot.recreate(output_file) as r:
  #   branches = {col: np.array(df[col].values) for col in df.columns}
  #   # r.mktree('tree', {col: np.dtype(branches[col].dtype) for col in branches})
  #   # r['tree'].extend(branches)
  # print(f"Saved {output_file}")
