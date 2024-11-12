import curses
import serial
import re
import socket
import time
import threading

import influxdb

HOST = '127.0.0.1'
PORT = 5000

class CaenN1470Controller:
  n_channel = 4

  def __init__(self, module_id_list):
    self.module_id_list = module_id_list
    self.selected_module = 0
    self.selected_channel = 0
    self.current_field = 0

controller = CaenN1470Controller(module_id_list=[0, 1])

fields = ["ISET", "VSET", "Power"]
power_state = {(module_id, ch): "OFF" for module_id in controller.module_id_list for ch in range(CaenN1470Controller.n_channel)}
status = {(module_id, ch): '   ' for module_id in controller.module_id_list for ch in range(CaenN1470Controller.n_channel)}
vset_values = {(module_id, ch): 0 for module_id in controller.module_id_list for ch in range(CaenN1470Controller.n_channel)}
iset_values = {(module_id, ch): 0 for module_id in controller.module_id_list for ch in range(CaenN1470Controller.n_channel)}
vmon_values = {(module_id, ch): 0 for module_id in controller.module_id_list for ch in range(CaenN1470Controller.n_channel)}
imon_values = {(module_id, ch): 0 for module_id in controller.module_id_list for ch in range(CaenN1470Controller.n_channel)}

sock = None
lock = threading.Lock()

def initialize_socket():
  global sock
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.settimeout(1)
  sock.connect((HOST, PORT))

def close_socket():
  global sock
  if sock:
    sock.close()
    sock = None

def send_command(command):
  global sock
  with lock:
    sock.sendall(command.encode())
    response = sock.recv(1024).decode().strip()
  match = re.search(r'VAL:(\S+)', response)
  return match.group(1) if match else "N/A"

def update_values():
  global power_state, status, vset_values, iset_values, vmon_values, imon_values
  while True:
    bucket = 'caenhv'
    query = f'''
from(bucket: "{bucket}")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "n1470")
    |> group(columns: ["module_id", "channel", "_field"])
    |> last()
'''
    for table in influxdb.query_api(query):
      for record in table.records:
        # print(f'Time: {record.get_time()}, Module ID: {record["module_id"]}, Channel: {record["channel"]}, '
        #       f'Field: {record.get_field()}, Value: {record.get_value()}')
        module_id = int(record['module_id'])
        ch = int(record['channel'])
        field = record.get_field()
        value = record.get_value()
        if field == 'power':
          power_state[(module_id, ch)] = value
        elif field == 'status':
          status[(module_id, ch)] = '' if value is None else value
        elif field == 'vset':
          vset_values[(module_id, ch)] = float(value)
        elif field == 'iset':
          iset_values[(module_id, ch)] = float(value)
        elif field == 'vmon':
          vmon_values[(module_id, ch)] = float(value)
        elif field == 'imon':
          imon_values[(module_id, ch)] = float(value)
        else:
          raise Exception
    time.sleep(0.1)

def display_table(stdscr):
  stdscr.clear()
  stdscr.addstr(0, 0, "Use ARROW keys to navigate, ENTER to edit, SPACE to toggle Power, 'q' to quit")
  stdscr.addstr(2, 0, '           I0Set       V0Set        IMon        VMon     Pw   Status')
  row_idx = 3
  for module_id in controller.module_id_list:
    for channel in range(CaenN1470Controller.n_channel):
      highlight_row = (module_id == controller.selected_module and channel == controller.selected_channel)
      row_style = curses.A_REVERSE if highlight_row else curses.A_NORMAL
      stdscr.addstr(row_idx, 0, f"{module_id:02d}-{channel:03d} | ", curses.A_NORMAL)
      for field_idx, field in enumerate(['iset', 'vset', #'imon', 'vmon',
                    'power', #'status'
                    ]):
        if field == 'power':
          field_value = f'{power_state[(module_id, channel)]:3s}'
        elif field == 'vset':
          field_value = f"{vset_values[(module_id, channel)]:06.1f} V"
        elif field == 'iset':
          field_value = f"{iset_values[(module_id, channel)]:07.2f} uA"
        # elif field == 'vmon':
        #   field_value = f"{vmon_values[(module_id, channel)]} V"
        # elif field == 'imon':
        #   field_value = f"{imon_values[(module_id, channel)]} uA"
        field_style = curses.A_REVERSE if highlight_row and field_idx == controller.current_field else curses.A_NORMAL
        stdscr.addstr(row_idx, stdscr.getyx()[1], field_value, field_style)
        stdscr.addstr(row_idx, stdscr.getyx()[1], ' | ', curses.A_NORMAL)
        if field == "vset":
          stdscr.addstr(row_idx, stdscr.getyx()[1],
                        f'{imon_values[(module_id, channel)]:07.2f} uA | '+
                        f'{vmon_values[(module_id, channel)]:06.1f} V | ', curses.A_NORMAL)
        if field == 'power':
          stdscr.addstr(row_idx, stdscr.getyx()[1], f"{status[(module_id, channel)]:3s} |", curses.A_NORMAL)
      row_idx += 1
  stdscr.refresh()

def toggle_power():
  key = (controller.selected_module, controller.selected_channel)
  power_state[key] = "OFF" if power_state[key] == 'ON' else "ON"
  send_command(f"$BD:{controller.selected_module:02d},CMD:SET,CH:{controller.selected_channel},PAR:{power_state[key]}")

def set_value(stdscr, field):
  global editing
  key = (controller.selected_module, controller.selected_channel)
  editing = True
  curses.echo()
  new_value = input_value(stdscr, f"Enter new {field}: ")
  if new_value:
    if field == "VSET":
      vset_values[key] = float(new_value)
      send_command(f"$BD:{controller.selected_module:02d},CMD:SET,CH:{controller.selected_channel},PAR:VSET,VAL:{vset_values[key]:.1f}")
    elif field == "ISET":
      try:
        iset_values[key] = float(new_value)
        send_command(f"$BD:{controller.selected_module:02d},CMD:SET,CH:{controller.selected_channel},PAR:ISET,VAL:{iset_values[key]:.1f}")
      except:
        pass
  curses.noecho()
  editing = False

def input_value(stdscr, prompt):
  stdscr.addstr(1, 0, prompt)
  stdscr.clrtoeol()
  stdscr.refresh()
  stdscr.nodelay(0)
  curses.echo()
  ret = stdscr.getstr().decode("utf-8")
  curses.noecho()
  stdscr.nodelay(1)
  stdscr.timeout(100)
  return ret

def main(stdscr):
  try:
    curses.curs_set(0)
  except curses.error:
    pass
  stdscr.nodelay(1)
  stdscr.timeout(100)

  initialize_socket()
  threading.Thread(target=update_values, daemon=True).start()

  # global current_field, controller.selected_module, controller.selected_channel, editing
  editing = False
  while True:
    if editing:
      continue
    display_table(stdscr)
    key = stdscr.getch()
    if key == curses.KEY_UP:
      controller.selected_channel = (controller.selected_channel - 1) % CaenN1470Controller.n_channel
      if controller.selected_channel == 3:
        controller.selected_module = (controller.selected_module - 1) % len(controller.module_id_list)
    elif key == curses.KEY_DOWN:
      controller.selected_channel = (controller.selected_channel + 1) % CaenN1470Controller.n_channel
      if controller.selected_channel == 0:
        controller.selected_module = (controller.selected_module + 1) % len(controller.module_id_list)
    elif key == curses.KEY_LEFT:
      controller.current_field = (controller.current_field - 1) % len(fields)
    elif key == curses.KEY_RIGHT:
      controller.current_field = (controller.current_field + 1) % len(fields)
    elif key == curses.KEY_ENTER or key == 10:
      if fields[controller.current_field] == "Power":
        toggle_power()
      else:
        set_value(stdscr, fields[controller.current_field])
    elif key == ord(' '):
      if fields[controller.current_field] == "Power":
        toggle_power()
    elif key == ord('q'):
      break

  close_socket()

curses.wrapper(main)
