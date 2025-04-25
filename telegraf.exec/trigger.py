#!/usr/bin/env python3

import argparse
import os
import time

last_log = f'/home/sks/software/trig-control/last.log'

NumOfRegion2 = 6
BeamDetectors = ['BH1', 'T0', 'UVETO', 'HTOF', 'Other1', 'Other2']
ScatDetectors = ['BEAM', 'SAC', 'EVETO', 'TOF-unused',
                 'TOF', 'Clock1k', 'L1ACC', 'TAG',
                 'M3D', 'BGO', 'CFT']

#______________________________________________________________________________
def is_updated(path, threshold):
  if not os.path.exists(path):
    return 0
  mtime = os.path.getmtime(path)
  # current_time = time.time()
  # if current_time - mtime <= threshold:
  return mtime
  # else:
  #   return 0

#______________________________________________________________________________
def bps(ctrl, coin):
  if ctrl == 0:
    return 'OFF'
  if coin == 0:
    return 'VETO'
  return 'ON'

#______________________________________________________________________________
def beam_bps(ctrl, coin):
  buf = ''
  for i, d in enumerate(BeamDetectors):
    b = bps((ctrl>>(len(BeamDetectors)-1-i))&1,
            (coin>>(len(BeamDetectors)-1-i))&1)
    if 'OFF' in b:
      continue
    elif 'VETO' in b:
      buf += '/'
    buf += d + 'x'
  if buf[-1:] == 'x':
    buf = buf[:-1]
  return buf

#______________________________________________________________________________
def scat_bps(ctrl, coin, beam):
  buf = ''
  for i, d in enumerate(ScatDetectors):
    b = bps((ctrl>>(len(ScatDetectors)-1-i))&1,
            (coin>>(len(ScatDetectors)-1-i))&1)
    if 'OFF' in b:
      continue
    elif 'VETO' in b:
      buf += '/'
    if i == 0:
      buf += beam + 'x'
    else:
      buf += d + 'x'
  if buf[-1:] == 'x':
    buf = buf[:-1]
  if len(buf) == 0:
    buf = ''
  return buf


#______________________________________________________________________________
def gate(val):
  if val == 0:
    return '-'
  elif val == 1:
    return 'on'
  elif val == 2:
    return 'off'
  elif val == 3:
    return 'on/off'
  else:
    return '-'

#______________________________________________________________________________
def onoff(val, char=False):
  on = '!' if char else 'on'
  off = '.' if char else 'off'
  if val == 0:
    return f'{off}'
  elif val == 1:
    return f'{on}'
  else:
    return ''

#______________________________________________________________________________
if __name__ == '__main__':
    mtime = is_updated(last_log, threshold=9)
  # if mtime > 0:
    param = {}
    with open(last_log, 'r') as f:
      for line in f.readlines():
        line = line.split()
        if len(line) == 1 and line[0][0] != '#':
          param['param_file'] = f'"{line[0]}"'
        if len(line) == 2 and line[0][0] != '#':
          param[line[0]] = f'{line[1]}i'
    if len(param) > 0:
      print('register ', end='')
      for key, val in param.items():
        key = key.replace('::', '_')
        print(f'{key}={val}', end=(f' {int(mtime*1e9)}\n' if key == 'RGN4_GATE' else ','))

      print('trigger ', end='')
      for key, val in param.items():
        if key != 'param_file':
          param[key] = int(val.replace('i', ''))
      print(f'param_file={param["param_file"]},'
            f'sel_tof="{param["RGN1::SEL_TOF"]}",', end='')
      sel_psor = int(param['RGN3::SEL_PSOR'])
      for i in range(NumOfRegion2):
        abc = chr(65+i)
        sel = onoff((sel_psor >> i) & 1)
        ps = param[f'RGN3::PS_R2{abc}'] + 1
        g = gate(param[f'RGN3::GATE_R2{abc}'])
        if sel == 'off':
          g = ''
        ctrl = param[f'RGN2{abc}::BPS_CTRL_BEAM']
        coin = param[f'RGN2{abc}::BPS_COIN_BEAM']
        beam = beam_bps(ctrl, coin)
        ctrl = param[f'RGN2{abc}::BPS_CTRL_SCAT']
        coin = param[f'RGN2{abc}::BPS_COIN_SCAT']
        scat = scat_bps(ctrl, coin, beam)
        print(f'trig_{abc.lower()}="{scat}",'
              f'trig_{abc.lower()}_ps="{ps}",'
              f'trig_{abc.lower()}_gate="{g}"',
              end = ',' if i != NumOfRegion2 - 1 else f' {int(mtime*1e9)}\n')
