from datetime import datetime
import os

scaler_txt = '/misc/subdata/scaler/spill.txt'

#______________________________________________________________________________
def read(scaler_txt=scaler_txt):
  ts_dt = None
  scaler = {}
  with open(scaler_txt, 'r') as f:
    spill_fields = []
    freq_fields = []
    for line in f.readlines():
      if ts_dt is None:
        ts_dt = datetime.strptime(line.strip(), '%Y-%m-%d %H:%M:%S')
        ts_ns = int(ts_dt.timestamp() * 1e9)
        continue
      columns = line.split()
      if len(columns) != 2:
        continue
      key = columns[0].replace('-', '_').replace('/', '_')#.lower()
      if '_Hz' in key:
        freq_fields.append(f'{key}={float(columns[1])}')
      else:
        spill_fields.append(f'{key}={float(columns[1])}')
    spill_fields = ','.join(spill_fields)
    print(f'spill {spill_fields} {ts_ns}')
    freq_fields = ','.join(freq_fields)
    print(f'freq {freq_fields} {ts_ns}')

#______________________________________________________________________________
if __name__ == '__main__':
  read()
