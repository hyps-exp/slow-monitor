import csv
from datetime import datetime, timezone, timedelta
import re
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

host = 'db-hyps'
influxdb_url = f'http://{host}:8086'
token = '-iT93bQ-4tDWCQVR42vBoRbE58wzxIWsDYB6S4vfgR9BiiRSrfoR90OpaYXtaBuEkAPgfrv0YrFtqQPFFn81Vg=='
org = 'hyps'

#______________________________________________________________________________
def parse_comment(comment_path, recorder_log_path):
  with open(comment_path, 'r') as f:
    comment_lines = f.readlines()

  with open(recorder_log_path, 'r') as f:
    recorder_log_lines = f.readlines()

  run_summary = []

  recorder_data = {}
  for line in recorder_log_lines:
    match = re.match(r"RUN\s+(\d+)\s+:\s+(.*?)\s+-\s+(.*?)\s+:\s+(\d+) events\s+:\s+(\d+) bytes", line)
    if match:
      run_number = match.group(1)
      events = int(match.group(4))
      size = int(match.group(5))
      recorder_data[run_number] = {
        "Events": events,
        "Data Size (bytes)": size
      }

  current_run = None
  for line in comment_lines:
    parts = line.strip().split(' ', 5)
    if len(parts) < 6:
      continue

    date = f"{parts[0]}-{parts[1]}"
    time = parts[2]
    run_number = str(int(parts[4][1:].replace(']', '')))
    status = parts[5].split(':', 1)[0].strip()
    comment = parts[5].split(':', 1)[1].strip() if ':' in parts[5] else ''
    if status.startswith("START"):
      current_run = {
        "Run Number": run_number,
        "Start Time": f"{date}-{time}",
        "Stop Time": "",
        "Comment": comment,
        "Events": recorder_data.get(run_number, {}).get("Events", ""),
        "Data Size (bytes)": recorder_data.get(run_number, {}).get("Data Size (bytes)", ""),
        "Storage Ring Current": "",
        "Tagger Rate (Hz)": "",
        "T0/Tagger Ratio": "",
        "L1 Req. (Hz)": "",
        "DAQ Efficiency": "",
        "LiveTime/RealTime": "",
        "Duty": "",
        "Trigger Param": "",
        "TrigA": "",
        "TrigA-PS": "",
        "TrigA-Gate": "",
        "TrigB": "",
        "TrigB-PS": "",
        "TrigB-Gate": "",
        "TrigC": "",
        "TrigC-PS": "",
        "TrigC-Gate": "",
        "TrigD": "",
        "TrigD-PS": "",
        "TrigD-Gate": "",
        "TrigE": "",
        "TrigE-PS": "",
        "TrigE-Gate": "",
        "TrigF": "",
        "TrigF-PS": "",
        "TrigF-Gate": "",
      }
      run_summary.append(current_run)

    elif status.startswith("STOP"):
      if current_run and current_run["Run Number"] == run_number:
        current_run["Stop Time"] = f"{date}-{time}"

  # if current_run:
  #   run_summary.append(current_run)
  # print(run_summary)
  return run_summary

#______________________________________________________________________________
def query_api(query):
  return client.query_api().query(query)

#______________________________________________________________________________
def query_influxdb(run_summary):
  tz_jst = timezone(timedelta(hours=9))
  for run in run_summary:
    start_time = run["Start Time"]
    stop_time = run["Stop Time"]
    if stop_time is None or stop_time == '':
      continue
    start_time = datetime.strptime(
      start_time, "%Y-%m/%d-%H:%M:%S").astimezone(timezone.utc).isoformat()
    stop_time = datetime.strptime(
      stop_time, "%Y-%m/%d-%H:%M:%S").astimezone(timezone.utc).isoformat()
    if start_time and stop_time:
      # accelerator
      query = f'''
      from(bucket: "accelerator")
        |> range(start: {start_time}, stop: {stop_time})
        |> filter(fn: (r) => r._field == "current")
        |> mean()
      '''
      result = query_api(query=query)
      for table in result:
        for record in table.records:
          if record.get_field() == "current":
            run["Storage Ring Current"] = float(record.get_value())
      # scaler
      query = f'''
      from(bucket: "scaler")
        |> range(start: {start_time}, stop: {stop_time})
        |> filter(fn: (r) => r._field == "TAG_All_Hz" or r._field == "L1_Req_Hz" or r._field == "T0_TAG_All" or r._field == "DAQ_Eff" or r._field == "Live_Real" or r._field == "Duty")
        |> mean()
      '''
      result = query_api(query=query)
      for table in result:
        for record in table.records:
          if record.get_field() == "TAG_All_Hz":
            run["Tagger Rate (Hz)"] = int(record.get_value())
          elif record.get_field() == "L1_Req_Hz":
            run["L1 Req. (Hz)"] = int(record.get_value())
          elif record.get_field() == "T0_TAG_All":
            run["T0/Tagger Ratio"] = float(record.get_value())
          elif record.get_field() == "DAQ_Eff":
            run["DAQ Efficiency"] = float(record.get_value())
          elif record.get_field() == "Live_Real":
            run["LiveTime/RealTime"] = float(record.get_value())
          elif record.get_field() == "Duty":
            run["Duty"] = float(record.get_value())
      # accelerator
      query = f'''
      from(bucket: "trigger")
        |> range(start: 0, stop: {stop_time})
        |> filter(fn: (r) => r._measurement == "trigger")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n: 1)
      '''
      result = query_api(query=query)
      for table in result:
        for record in table.records:
          if record.get_field() == "param_file":
            run["Trigger Param"] = record.get_value()
          for i in range(6):
            abc = chr(97 + i)
            if record.get_field() == ('trig_' + abc):
              run["Trig" + abc.upper()] = record.get_value()
            if record.get_field() == ('trig_' + abc + '_ps'):
              if run["Trig" + abc.upper() + '-Gate'] != '':
                run["Trig" + abc.upper() + '-PS'] = record.get_value()
            if record.get_field() == ('trig_' + abc + '_gate'):
              if record.get_value() is None:
                run["Trig" + abc.upper()] = ''
              else:
                run["Trig" + abc.upper() + '-Gate'] = record.get_value()
  return run_summary

#______________________________________________________________________________
def save_to_csv(run_summary, output_csv):
  with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
      "Run Number", "Start Time", "Stop Time", "Comment",
      "Events", "Data Size (bytes)",
      "Storage Ring Current",
      "Tagger Rate (Hz)",
      "T0/Tagger Ratio",
      "L1 Req. (Hz)",
      "DAQ Efficiency",
      "LiveTime/RealTime",
      "Duty",
      "Trigger Param",
      "TrigA",
      "TrigA-PS",
      "TrigA-Gate",
      "TrigB",
      "TrigB-PS",
      "TrigB-Gate",
      "TrigC",
      "TrigC-PS",
      "TrigC-Gate",
      "TrigD",
      "TrigD-PS",
      "TrigD-Gate",
      "TrigE",
      "TrigE-PS",
      "TrigE-Gate",
      "TrigF",
      "TrigF-PS",
      "TrigF-Gate",
    ])
    writer.writeheader()
    writer.writerows(run_summary)
  # print(f"Run summary saved to {output_csv}")

#______________________________________________________________________________
def send_to_influxdb(run_summary):
  # write_api = client.write_api(write_options=SYNCHRONOUS)
  for run in run_summary:
    # run_number = run["Run Number"]
    # query = f'''
    #     from(bucket: "runsummary")
    #       |> range(start: 0)
    #       |> filter(fn: (r) => r._measurement == "runsummary")
    #       |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
    #       |> filter(fn: (r) => r.run_number == "{run_number}")
    #       |> filter(fn: (r) => r.stop_time != "")
    #       |> limit(n: 1)
    #     '''
    # result = query_api(query=query)
    # print(result)
    # if result:
    #   print(f'skip {run_number}')
    #   continue
    # print(run)
    jst_time = datetime.strptime(run["Start Time"], "%Y-%m/%d-%H:%M:%S").replace(tzinfo=timezone(timedelta(hours=9)))
    utc_time = jst_time.astimezone(timezone.utc)
    # point = Point("runsummary") \
    #   .tag("run_number", f'{int(run["Run Number"]):05d}') \
    #   .tag("start_time", run["Start Time"]) \
    #   .field("stop_time", run["Stop Time"]) \
    #   .field("comment", run["Comment"]) \
    #   .field("events", str(run["Events"]) if run["Events"] else '') \
    #   .field("datasize", str(run["Data Size (bytes)"]) if run["Data Size (bytes)"] else '') \
    #   .field("storage_ring_current", str(run["Storage Ring Current"]) if run["Storage Ring Current"] else '') \
    #   .field("tagger_rate", str(run["Tagger Rate (Hz)"]) if run["Tagger Rate (Hz)"] else '') \
    #   .field("t0_tagger", str(run["T0/Tagger Ratio"]) if run["T0/Tagger Ratio"] else '') \
    #   .field("l1_req", str(run["L1 Req. (Hz)"]) if run["L1 Req. (Hz)"] else '') \
    #   .field("daq_eff", str(run["DAQ Efficiency"]) if run["DAQ Efficiency"] else '') \
    #   .field("live_real", str(run["LiveTime/RealTime"]) if run["LiveTime/RealTime"] else '') \
    #   .field("duty", str(run["Duty"]) if run["Duty"] else '') \
    #   .field("trig_param", str(run["Trigger Param"]) if run["Trigger Param"] else '') \
    #   .field("trig_a", str(run["TrigA"]) if run["TrigA"] else '') \
    #   .field("trig_a_ps", str(run["TrigA-PS"]) if run["TrigA-PS"] else '') \
    #   .field("trig_a_gate", str(run["TrigA-Gate"]) if run["TrigA-Gate"] else '') \
    #   .field("trig_b", str(run["TrigB"]) if run["TrigB"] else '') \
    #   .field("trig_b_ps", str(run["TrigB-PS"]) if run["TrigB-PS"] else '') \
    #   .field("trig_b_gate", str(run["TrigB-Gate"]) if run["TrigB-Gate"] else '') \
    #   .field("trig_c", str(run["TrigC"]) if run["TrigC"] else '') \
    #   .field("trig_c_ps", str(run["TrigC-PS"]) if run["TrigC-PS"] else '') \
    #   .field("trig_c_gate", str(run["TrigC-Gate"]) if run["TrigC-Gate"] else '') \
    #   .field("trig_d", str(run["TrigD"]) if run["TrigD"] else '') \
    #   .field("trig_d_ps", str(run["TrigD-PS"]) if run["TrigD-PS"] else '') \
    #   .field("trig_d_gate", str(run["TrigD-Gate"]) if run["TrigD-Gate"] else '') \
    #   .field("trig_e", str(run["TrigE"]) if run["TrigE"] else '') \
    #   .field("trig_e_ps", str(run["TrigE-PS"]) if run["TrigE-PS"] else '') \
    #   .field("trig_e_gate", str(run["TrigE-Gate"]) if run["TrigE-Gate"] else '') \
    #   .field("trig_f", str(run["TrigF"]) if run["TrigF"] else '') \
    #   .field("trig_f_ps", str(run["TrigF-PS"]) if run["TrigF-PS"] else '') \
    #   .field("trig_f_gate", str(run["TrigF-Gate"]) if run["TrigF-Gate"] else '') \
    #   .time(utc_time, WritePrecision.S)

    # write_api.write(bucket='runsummary', org=org, record=point)

    # jst_time = datetime.strptime(run["Start Time"], "%Y %m/%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=9)))
    # utc_time = jst_time.astimezone(timezone.utc)
    line_protocol = (f'runsummary,'
                     f'run_number={int(run["Run Number"]):05d},'
                     f'start_time="{run["Start Time"]}" '
                     f'stop_time="{run["Stop Time"]}",'
                     f'comment="{run["Comment"]}",'
                     f'events="{run["Events"] if run["Events"] else ""}",'
                     f'datasize="{run["Data Size (bytes)"] if run["Data Size (bytes)"] else ""}",'
                     f'storage_ring_current="{run["Storage Ring Current"] if run["Storage Ring Current"] else ""}",'
                     f'tagger_rate="{run["Tagger Rate (Hz)"] if run["Tagger Rate (Hz)"] else ""}",'
                     f't0_tagger="{run["T0/Tagger Ratio"] if run["T0/Tagger Ratio"] else ""}",'
                     f'l1_req="{run["L1 Req. (Hz)"] if run["L1 Req. (Hz)"] else ""}",'
                     f'daq_eff="{run["DAQ Efficiency"] if run["DAQ Efficiency"] else ""}",'
                     f'live_real="{run["LiveTime/RealTime"] if run["LiveTime/RealTime"] else ""}",'
                     f'duty="{run["Duty"] if run["Duty"] else ""}",'
                     f'trig_param="{run["Trigger Param"] if run["Trigger Param"] else ""}",'
                     f'trig_a="{run["TrigA"] if run["TrigA"] else ""}",'
                     f'trig_a_ps="{run["TrigA-PS"] if run["TrigA-PS"] else ""}",'
                     f'trig_a_gate="{run["TrigA-Gate"] if run["TrigA-Gate"] else ""}",'
                     f'trig_b="{run["TrigB"] if run["TrigB"] else ""}",'
                     f'trig_b_ps="{run["TrigB-PS"] if run["TrigB-PS"] else ""}",'
                     f'trig_b_gate="{run["TrigB-Gate"] if run["TrigB-Gate"] else ""}",'
                     f'trig_c="{run["TrigC"] if run["TrigC"] else ""}",'
                     f'trig_c_ps="{run["TrigC-PS"] if run["TrigC-PS"] else ""}",'
                     f'trig_c_gate="{run["TrigC-Gate"] if run["TrigC-Gate"] else ""}",'
                     f'trig_d="{run["TrigD"] if run["TrigD"] else ""}",'
                     f'trig_d_ps="{run["TrigD-PS"] if run["TrigD-PS"] else ""}",'
                     f'trig_d_gate="{run["TrigD-Gate"] if run["TrigD-Gate"] else ""}",'
                     f'trig_e="{run["TrigE"] if run["TrigE"] else ""}",'
                     f'trig_e_ps="{run["TrigE-PS"] if run["TrigE-PS"] else ""}",'
                     f'trig_e_gate="{run["TrigE-Gate"] if run["TrigE-Gate"] else ""}",'
                     f'trig_f="{run["TrigF"] if run["TrigF"] else ""}",'
                     f'trig_f_ps="{run["TrigF-PS"] if run["TrigF-PS"] else ""}",'
                     f'trig_f_gate="{run["TrigF-Gate"] if run["TrigF-Gate"] else ""}" '
                     f'{int(utc_time.timestamp() * 1e9)}')
    print(line_protocol)
  # print("Run summary has been written to InfluxDB.")

if __name__ == '__main__':
  comment_path = "/misc/rawdata/misc/comment.txt"
  recorder_log_path = "/misc/rawdata/recorder.log"
  output_csv = "/misc/subdata/runsummary.csv"
  run_summary = parse_comment(comment_path, recorder_log_path)

  client = InfluxDBClient(url=influxdb_url, token=token, org=org)
  run_summary = query_influxdb(run_summary)
  save_to_csv(run_summary, output_csv)
  send_to_influxdb(run_summary)
  client.close()
