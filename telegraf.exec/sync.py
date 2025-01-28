import os
from datetime import datetime

ls_kekcc_path = "/misc/subdata/tmp/ls-kekcc.txt"
local_path = '/misc/rawdata'

def get_latest_dat_file(ls_kekcc_path):
  rsync_kekcc = None
  latest_kekcc = None
  latest_local = None
  with open(ls_kekcc_path, 'r') as f:
    for line in f:
      line = line.strip()
      if line.startswith(".run"):
        rsync_kekcc = int(line.split()[-1].replace('.dat', '').replace('run', ''))
      if line.endswith(".dat"):
        latest_kekcc = int(line.split()[-1].replace('.dat', '').replace('run', ''))
  for file_name in os.listdir(local_path):
    if file_name.endswith(".dat"):
      latest_local = int(line.split()[-1].replace('.dat', '').replace('run', ''))
  return rsync_kekcc, latest_kekcc, latest_local

def generate_line_protocol(rsync_kekcc,
                           latest_kekcc, ls_kekcc_path, latest_local):
  if latest_kekcc is None:
    return None
  ls_kekcc_timestamp = os.path.getmtime(ls_kekcc_path)
  timestamp_ns = int(ls_kekcc_timestamp * 1e9)
  if rsync_kekcc is None:
    rsync = 0
  else:
    rsync = 1
  line_protocol = f'sync rsync={rsync},kekcc={latest_kekcc},local={latest_local} {timestamp_ns}'
  return line_protocol

rsync_kekcc, latest_kekcc, latest_local = get_latest_dat_file(ls_kekcc_path)

line_protocol = generate_line_protocol(rsync_kekcc,
                                       latest_kekcc, ls_kekcc_path, latest_local)

if line_protocol:
  print(line_protocol)
else:
  print("No .dat file found.")
