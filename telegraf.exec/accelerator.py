from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

# target_url = 'http://www.spring8.or.jp/ja/users/operation_status/storage_ring/'
storage_ring_url = 'http://www.spring8.or.jp/ext/ja/status/2.html'

#______________________________________________________________________________
def parse(url):
  response = requests.get(url)
  response.encoding = response.apparent_encoding
  html_content = response.text
  soup = BeautifulSoup(html_content, 'html.parser')
  table = soup.find('table')
  if not table:
    print('table not found')
    return
  elements = soup.find_all(attrs={"bgcolor": "#388C66"})
  dt_str = []
  for e in elements:
    dt_str.append(e.text.strip())
  current_year = datetime.now().year
  datetime_obj = datetime.strptime(
    f"{dt_str[0]} {current_year} {dt_str[1]}", "%a %b %d %Y %H:%M:%S")
  iso_format = datetime_obj.isoformat() + "Z"
  unix_ns = int(datetime_obj.timestamp() * 1e9)
  elements = soup.find_all(attrs={"bgcolor": "#B2C1FF"})
  elements += soup.find_all(attrs={"bgcolor": "#99ACFF"})
  beam_str = []
  for e in elements:
    match = re.match(r"([0-9.]+)([a-zA-Z]+)", e.text.strip())
    if match:
      value = float(match.group(1))
      unit = match.group(2)
      beam_str.append((value, unit))
    else:
      match = re.match(r"([0-9.]+) ([a-zA-Z]+)", e.text.strip())
      if match:
        value = float(match.group(1))
        unit = match.group(2)
        beam_str.append((value, unit))
  if len(beam_str) == 3:
    print(f'storage_ring '
          f'current={beam_str[0][0]},current_unit="{beam_str[0][1]}",'
          f'energy={beam_str[1][0]},energy_unit="{beam_str[1][1]}",'
          f'pattern={beam_str[2][0]},pattern_unit="{beam_str[2][1]}" {unix_ns}')

#______________________________________________________________________________
if __name__ == '__main__':
  parse(url=storage_ring_url)
