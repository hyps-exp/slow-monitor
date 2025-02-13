#!/usr/bin/env python

import os

data_dir = '/mnt/raid/rawdata'
misc_dir = os.path.join(data_dir, 'misc')
runno_txt = os.path.join(misc_dir, 'runno.txt')
starttime_txt = os.path.join(misc_dir, 'starttime.txt')
maxevent_txt = os.path.join(misc_dir, 'maxevent.txt')
trig_txt = os.path.join(misc_dir, 'trig.txt')
comment_txt = os.path.join(misc_dir, 'comment.txt')

#______________________________________________________________________________
def read(path):
  with open(path, 'r') as f:
    lines = f.readlines()
    return lines[-1] if lines else None

#______________________________________________________________________________
def read_comment(path=comment_txt):
  last_line = read(path)
  if last_line:
    last_colon_index = last_line.rfind(':')
    if last_colon_index != -1:
      comment = last_line[last_colon_index + 1:].strip()
      mtime_ns = int(os.path.getmtime(path) * 1_000_000_000)
      return (comment.replace(',', '.').replace('"', '_').replace("'", '_'),
              mtime_ns)

#______________________________________________________________________________
if __name__ == '__main__':
  comment, mtime_ns = read_comment()
  print(f'hddaq,data_dir={data_dir} runnumber={read(runno_txt)}i,'+
        f'starttime="{read(starttime_txt)}",'+
        f'maxevent={read(maxevent_txt)}i,'+
        f'trig="{read(trig_txt)}",'+
        f'comment="{comment}" {mtime_ns}')
