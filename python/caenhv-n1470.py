import socket
import re
import sys

host = '127.0.0.1'
port = 5000

module_ids = [0, 1]
metrics = {
  'VSET': 'vset',
  'ISET': 'iset',
  'VMON': 'vmon',
  'IMON': 'imon',
  'STAT': 'status'
}

sock = None

#______________________________________________________________________________
def initialize_socket():
  global sock
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.settimeout(1)
  sock.connect((host, port))

#______________________________________________________________________________
def close_socket():
  global sock
  if sock:
    sock.close()
    sock = None

#______________________________________________________________________________
def send_command(command):
  global sock
  sock.sendall(command.encode())
  response = sock.recv(1024).decode().strip()
  match = re.search(r'VAL:(\S+)', response)
  return match.group(1) if match else 'N/A'

#______________________________________________________________________________
def get_values():
  data_points = []
  for module_id in module_ids:
    for ch in range(4):
      data = {}
      for key, value_name in metrics.items():
        response = send_command(f'$BD:{module_id:02d},CMD:MON,CH:{ch},PAR:{key}')
        try:
          data[value_name] = float(response)
        except ValueError:
          data[value_name] = 0
      stat = int(data['status'])
      power = ('ON' if stat & 0x1 == 1 else 'OFF' if stat & 0x1 == 0 else 'UNKNOWN')
      stat = ('NOCAL' if (stat >> 13) & 0x1 == 1 else
              'ILK' if (stat >> 12) & 0x1 == 1 else
              'KILL' if (stat >> 11) & 0x1 == 1 else
              'DIS' if (stat >> 10) & 0x1 == 1 else
              'OVT' if (stat >> 9) & 0x1 == 1 else
              'OVP' if (stat >> 8) & 0x1 == 1 else
              'TRIP' if (stat >> 7) & 0x1 == 1 else
              'MAXV' if (stat >> 6) & 0x1 == 1 else
              'UNV' if (stat >> 5) & 0x1 == 1 else
              'OVV' if (stat >> 4) & 0x1 == 1 else
              'OVC' if (stat >> 3) & 0x1 == 1 else
              'RDW' if (stat >> 2) & 0x1 == 1 else
              'RUP' if (stat >> 1) & 0x1 == 1 else
              '')
      line_protocol = (f'caenhv.n1470,module_id={module_id},channel={ch} '+
                       f'vset={data["vset"]},iset={data["iset"]},'+
                       f'vmon={data["vmon"]},imon={data["imon"]},'+
                       f'power="{power}",'+
                       f'status="{stat}"')
      data_points.append(line_protocol)
  return data_points

#______________________________________________________________________________
def main():
  try:
    initialize_socket()
    data_points = get_values()
    for point in data_points:
      print(point)
  except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
  finally:
    close_socket()

if __name__ == '__main__':
  main()
