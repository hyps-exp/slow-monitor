#!/usr/bin/env python

import re
from datetime import datetime

#______________________________________________________________________________
def parse_dhcpd_conf(file_path):
  entries = []
  with open(file_path, 'r') as file:
    content = file.read()
    matches = re.findall(
      r'host\s+(\S+)\s*{\s*hardware\s+ethernet\s+(\S+);\s*fixed-address\s+(\S+);',
      content, re.DOTALL
    )
    for match in matches:
      hostname, mac_address, ip_address = match
      entries.append({
        "hostname": hostname,
        "ip_address": ip_address,
        "mac_address": mac_address,
        "static": True
      })
  return entries

#______________________________________________________________________________
def parse_dhcpd_leases(file_path):
  current_time = datetime.utcnow()
  entries = []
  with open(file_path, 'r') as file:
    content = file.read()
    lease_entries = re.findall(r'lease\s+(\S+)\s+{([^}]*)}',
                               content, re.DOTALL)
    for ip_address, lease_block in lease_entries:
      starts_match = re.search(r'starts\s+\d+\s+(\S+\s+\S+);', lease_block)
      ends_match = re.search(r'ends\s+\d+\s+(\S+\s+\S+);', lease_block)
      mac_match = re.search(r'hardware\s+ethernet\s+(\S+);', lease_block)
      hostname_match = re.search(r'client-hostname\s+"([^"]*)";', lease_block)
      if starts_match and ends_match and mac_match:
        starts = datetime.strptime(starts_match.group(1), "%Y/%m/%d %H:%M:%S")
        ends = datetime.strptime(ends_match.group(1), "%Y/%m/%d %H:%M:%S")
        mac_address = mac_match.group(1)
        hostname = hostname_match.group(1) if hostname_match else "unknown"
        active = starts <= current_time <= ends
        entries.append({
          "hostname": hostname,
          "ip_address": ip_address,
          "mac_address": mac_address,
          "starts": starts,
          "ends": ends,
          "active": active,
          "static": False
        })
  return entries

#______________________________________________________________________________
if __name__ == '__main__':
  dhcpd_conf_path = '/etc/dhcp/dhcpd.conf'
  dhcpd_leases_path = '/var/lib/dhcpd/dhcpd.leases'
  static_entries = parse_dhcpd_conf(dhcpd_conf_path)
  lease_entries = parse_dhcpd_leases(dhcpd_leases_path)

  for entry in static_entries + lease_entries:
    active_status = "true" if entry.get("active", True) else "false"
    static_status = "true" if entry["static"] else "false"
    starts_timestamp = (entry.get("starts", datetime.min) #.timestamp()
                        if "starts" in entry else None)
    ends_timestamp = (entry.get("ends", datetime.min) #.timestamp()
                      if "ends" in entry else None)
    print(f'dhcp,ip_address={entry["ip_address"]} '
          f'hostname="{entry["hostname"]}",'
          f'mac_address="{entry["mac_address"]}",'
          f'active="{active_status}",'
          f'static="{static_status}",'
          f'lease_start="{starts_timestamp}",lease_end="{ends_timestamp}"')
