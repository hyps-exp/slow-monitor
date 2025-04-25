#!/usr/bin/env python3

import glob
import os
import re
import time
import yaml

register_dir = '/misc/software/vme-easiroc-registers'

#______________________________________________________________________________
def sanitize_key(key):
  return key.lower().replace(' ', '_').replace('.', '_').replace('/', '_').replace(':', '_')

#______________________________________________________________________________
def parse_input_dac(path, timestamp):
  measurement = 'input_dac'
  fields = {}
  try:
    with open(path, 'r') as f:
      data = yaml.safe_load(f)
  except Exception:
    return None

  ch = 0
  for chip in ['EASIROC1', 'EASIROC2']:
    if chip in data and 'Input 8-bit DAC' in data[chip]:
      dac_list = data[chip]['Input 8-bit DAC']
      for i, val in enumerate(dac_list):
        # key = f"{chip.lower()}_ch{str(i).zfill(2)}"
        key = f'ch{ch:02d}'
        ch += 1
        try:
          fields[key] = int(val)
        except ValueError:
          continue

  if not fields:
    return None

  match = re.search(r'InputDAC_([\d.]+)\.ya?ml$', os.path.basename(path))
  module = match.group(1) if match else 'unknown'
  tag_str = f"module={module}"
  field_str = ",".join(f"{k}={v}" for k, v in fields.items())
  return f"{measurement},{tag_str} {field_str} {timestamp}"

#______________________________________________________________________________
def parse_pede_sup(path, timestamp):
  measurement = 'pede_sup'
  fields = {}
  try:
    with open(path, 'r') as f:
      data = yaml.safe_load(f)
  except Exception:
    return None

  for gain_type in ['HG', 'LG']:
    if gain_type in data:
      for i, val in enumerate(data[gain_type]):
        key = f"{gain_type.lower()}_ch{str(i).zfill(2)}"
        try:
          fields[key] = int(val)
        except ValueError:
          continue

  if not fields:
    return None

  match = re.search(r'PedeSup_([\d.]+)\.ya?ml$', os.path.basename(path))
  module = match.group(1) if match else 'unknown'
  tag_str = f"module={module}"
  field_str = ",".join(f"{k}={v}" for k, v in fields.items())
  return f"{measurement},{tag_str} {field_str} {timestamp}"

#______________________________________________________________________________
def parse_register_value(path, timestamp):
  measurement = 'register'
  fields = {}
  try:
    with open(path, 'r') as f:
      data = yaml.safe_load(f)
  except Exception:
    return None

  for chip in ['EASIROC1', 'EASIROC2']:
    if chip in data:
      for k, v in data[chip].items():
        if isinstance(v, str) and ('same' in v.lower() or v.strip().startswith('#')):
          continue
        key = sanitize_key(f"{chip}_{k}")
        try:
          # val = float(str(v).replace('fF', '').replace('ns', '').replace('mV', '').strip())
          val = float(v)
          fields[key] = val
        except ValueError:
          fields[key] = f'"{v}"'

  for k, v in data.items():
    if k not in ['EASIROC1', 'EASIROC2']:
      key = sanitize_key(k)
      try:
        # val = float(str(v).replace('fF', '').replace('ns', '').replace('mV', '').strip())
        val = float(v)
        fields[key] = val
      except ValueError:
        fields[key] = f'"{v}"'
  if not fields:
    return None

  match = re.search(r'RegisterValue_([\d.]+)\.ya?ml$', os.path.basename(path))
  module = match.group(1) if match else 'unknown'
  tag_str = f"module={module}"
  field_str = ",".join(f"{k}={v}" for k, v in fields.items())
  return f"{measurement},{tag_str} {field_str} {timestamp}"

#______________________________________________________________________________
def read_symlink():
  measurement = 'symlink'
  symlinks = {'input_dac': 'InputDAC',
              'pede_sup': 'PedeSup',
              'register': 'RegisterValue'}
  fields = {}
  timestamps = []
  for key, path in symlinks.items():
    path = os.path.join(register_dir, path)
    try:
      target = os.readlink(path)
      abs_target = os.path.abspath(target)
    except OSError:
      abs_target = 'unknown'
    try:
      stat = os.lstat(path)
      timestamps.append(stat.st_mtime)
    except OSError:
      timestamps.append(0)
    fields[key] = f'"{abs_target}"'
  latest_mtime = max(timestamps)
  timestamp_ns = int(latest_mtime * 1e9)
  field_str = ",".join(f"{k}={v}" for k, v in fields.items())
  print(f"{measurement} {field_str} {timestamp_ns}")

#______________________________________________________________________________
def main():
  timestamp = int(time.time() * 1e9)

  read_symlink()

  for file_path in sorted(glob.glob(
      os.path.join(register_dir, 'InputDAC', 'InputDAC_*.yml'))):
    line = parse_input_dac(file_path, timestamp)
    if line:
      print(line)

  for file_path in sorted(glob.glob(
      os.path.join(register_dir, 'PedeSup', 'PedeSup_*.yml'))):
    line = parse_pede_sup(file_path, timestamp)
    if line:
      print(line)

  for file_path in sorted(glob.glob(
      os.path.join(register_dir, 'RegisterValue', 'RegisterValue_*.yml'))):
    line = parse_register_value(file_path, timestamp)
    if line:
      print(line)

#______________________________________________________________________________
if __name__ == '__main__':
  main()
