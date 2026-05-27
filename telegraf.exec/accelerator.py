from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

# target_url = 'http://www.spring8.or.jp/ja/users/operation_status/storage_ring/'
storage_ring_url = 'http://www.spring8.or.jp/ext/ja/status/2.html'

#______________________________________________________________________________
def parse(url):

  #--- Local functions ---#
  def parse_numeric(e):
    """Parse a string with a numeric value and unit (e.g. "99.50mA" → (99.50, "mA", "99.50mA"))"""
    original = e.text.strip()
    match = re.match(r"([0-9.]+)([a-zA-Z]+)", original) or \
            re.match(r"([0-9.]+) ([a-zA-Z]+)", original)
    if match:
      value = float(match.group(1))
      unit = match.group(2)
    else:
      value = None
      unit = None
    return (value, unit, original)

  def parse_pattern(e):
    """
    Extract the numeric value and original string of the filling pattern.
    Handles both integer-leading (e.g. "406 x 11/29-bunches + 1 bunch")
    and fraction-leading (e.g. "1/14-filling + 12 bunches") patterns.
    Returns None for the numeric value if conversion is not possible,
    in which case the pattern Field is omitted from the output.

    Returns:
      (float | None, str, str)
      e.g. (406.0, '', "406 x 11/29-bunches + 1 bunch")
           (None,  '', "1/14-filling + 12 bunches")
    """
    original = e.text.strip()
    match = re.match(r"([0-9.]+) ", original)
    value = float(match.group(1)) if match else None
    return (value, '', original)

  def parse_mode(e):
    """Extract the mode string as-is (e.g. "実験中" → ("実験中", '', "実験中"))"""
    original = e.text.strip()
    return (original, '', original)

  #--- main logic ---#
  response = requests.get(url)
  response.encoding = response.apparent_encoding
  html_content = response.text
  soup = BeautifulSoup(html_content, 'html.parser')

  table = soup.find('table')
  if not table:
    print('table not found')
    return

  # datetime
  elements = soup.find_all(attrs={"bgcolor": "#388C66"})
  dt_str = []
  for e in elements:
    dt_str.append(e.text.strip())
  current_year = datetime.now().year
  datetime_obj = datetime.strptime(
    f"{dt_str[0]} {current_year} {dt_str[1]}", "%a %b %d %Y %H:%M:%S")
  iso_format = datetime_obj.isoformat() + "Z"
  unix_ns = int(datetime_obj.timestamp() * 1e9)

  # accelerator info
  current_energy = soup.find_all(attrs={"bgcolor": "#B2C1FF"})
  pattern = soup.find_all(attrs={"bgcolor": "#99ACFF"})
  mode = soup.find_all(attrs={"bgcolor": "#E5EAFF"})

  beam_str = [
    parse_numeric(current_energy[0]),
    parse_numeric(current_energy[1]),
    parse_pattern(pattern[0]),
    parse_mode(mode[0],)
  ]

  if len(beam_str) == 4:
    # Omit 'pattern' / 'patter_unit' field if numeric conversion failed
    # (e.g. fraction-leading pattern: 1/14-filling + 12 bunches [F-mode])
    pattern_field = (f'pattern={beam_str[2][0]},pattern_unit="{beam_str[2][1]}",'
                     if beam_str[2][0] is not None else '')
    print(f'storage_ring '
          f'current={beam_str[0][0]},current_unit="{beam_str[0][1]}",'
          f'energy={beam_str[1][0]},energy_unit="{beam_str[1][1]}",'
          f'{pattern_field}'
          f'pattern_str="{beam_str[2][2]}",'
          f'mode="{beam_str[3][0]}" {unix_ns}')

#______________________________________________________________________________
if __name__ == '__main__':
  parse(url=storage_ring_url)
