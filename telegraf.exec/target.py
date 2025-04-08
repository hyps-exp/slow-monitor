#!/usr/bin/env python3

import os
import re
import time

file_path = '/misc/subdata/H2target/H2tgtPresentStatus.txt'
measurement = 'lh2'
fields = {}

if __name__ == '__main__':
  with open(file_path, 'r') as f:
    for line in f:
      line = line.strip()
      if not line or line.startswith('#'):
        continue
      match = re.match(r'^([A-Za-z0-9_.]+):\s+(-?\d+(?:\.\d+)?(?:e[+-]?\d+)?|\d+)$', line)
      if match:
        key = match.group(1).lower().replace('.', '_')
        val = match.group(2)
        fields[key] = float(val)
  field_str = ",".join(f"{k}={v}" for k, v in fields.items())
  timestamp = int(os.path.getmtime(file_path) * 1e9)
  print(f"{measurement} {field_str} {timestamp}")
