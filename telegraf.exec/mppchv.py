import os
import time
from datetime import datetime

# Configuration
ip_addresses = {
  "192.168.20.41": ["PHI1(75.50)",
                    "U1(75.50)",
                    "PHI2(73.80)",
                    "V2(73.80)",
                    "PHI3(75.40)",
                    "U3(75.40)",
                    "PHI4(75.40)",
                    "V4(75.40)"],
  "192.168.20.42": ["PiID(76.70)"]
}
top_dir = "/misc/software/mppc-hv-controller"
summary_out = os.path.join(top_dir, "mppcbias_summary.txt")

def read_file_lines(filepath):
  """Read lines from a file."""
  if os.path.exists(filepath):
    with open(filepath, 'r') as file:
      return file.readlines()
  return []

def parse_line(line):
  """Parse a line from the file and split values."""
  return line.strip().split()

def write_to_influx_format(output_file, ip, channel, name, status,
                           date_time, vset, vmon, iset, imon, temp, trip):
  """Write a line in InfluxDB line protocol format."""
  line = f'mppchv,ip={ip},channel={channel},name={name} status={status},vset={vset},vmon={vmon},iset={iset},imon={imon},temp={temp},trip={trip} {int(time.mktime(datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").timetuple()))}000000000'
  print(line)
  # with open(output_file, 'a') as file:
  #   file.write(line)

if __name__ == '__main__':
  present_time = int(time.time())
  for ip, names in ip_addresses.items():
    tmp_file = os.path.join(top_dir, f'tmp/{ip}/Current.txt')
    lines = read_file_lines(tmp_file)
    if not lines:
      print(f"No data for IP: {ip}")
      continue
    # Ping check
    response = os.system(f"ping -c 1 -w 2 {ip} > /dev/null")
    ip_status = response #"ON" if response == 0 else "OFF"
    # print(lines)
    for line in lines:
      data = parse_line(line)
      # print(data)
      if len(data) == 2:
        _, data_time = data
        continue
      if len(data) < 7:
        continue
      channel, vset, vmon, iset, imon, temp, trip = data
      channel = channel.replace(':', '')
      ch = int(channel.replace('CH', ''))
      if ch >= len(names):
        continue
      name = names[ch]
      data_time = int(data_time)
      vset = float(vset)
      vmon = float(vmon)
      iset = float(iset)
      imon = float(imon)
      temp = float(temp)
      trip = int(trip)
      status = 1 if vmon > 39.0 else 0
      if present_time > data_time + 20:
        status = -1
      date_time = datetime.fromtimestamp(data_time).strftime("%Y-%m-%d %H:%M:%S")
      write_to_influx_format(summary_out, ip, channel, name, status, date_time, vset, vmon, iset, imon, temp, trip)
