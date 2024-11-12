import html.parser
import requests
import sys

#______________________________________________________________________________
class DataLogger(html.parser.HTMLParser):
  data_dict = dict()
  ch = None
  val = None
  unit = None

  #____________________________________________________________________________
  def __init__(self, ip_address='localhost', interval=10):
    super().__init__()
    self.ip_address = ip_address
    self.interval = interval
    self.wait = True
    self.will_stop = False

  #____________________________________________________________________________
  def handle_data(self, data):
    data = data.strip().replace(' ', '').replace('+', '')
    if len(data) == 0:
      return
    try:
      float(data)
    except ValueError:
      if 'CH' in data:
        self.ch = int(data[2:])
        self.val = None
        self.unit = None
      else:
        self.unit = data
    else:
      self.val = float(data)
    if (self.ch is not None and
        self.val is not None and
        self.unit is not None):
      self.data_dict[self.ch] = (self.val, self.unit)

  #____________________________________________________________________________
  def get_data(self, ch=None):
    if ch in self.data_dict:
      return self.data_dict[ch]
    else:
      return self.data_dict

  #____________________________________________________________________________
  def parse(self):
    try:
      ret = requests.get(f'http://{self.ip_address}/digital.cgi?chg=0')
      self.feed(ret.text)
    except:
      pass

#______________________________________________________________________________
if __name__ == '__main__':
  if len(sys.argv) < 2:
    exit
  host = sys.argv[1]
  logger = DataLogger(host)
  logger.parse()
  data = logger.get_data()
  for key in data:
    # print(data[key])
    channel = key
    value = data[key][0]
    unit = data[key][1]
    print(f'bgotemp,channel={channel:02d} value={value},unit="{unit}"')

