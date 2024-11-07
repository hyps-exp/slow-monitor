from influxdb_client import InfluxDBClient

host = '172.16.205.212'
url = f'http://{host}:8086'
token = '-iT93bQ-4tDWCQVR42vBoRbE58wzxIWsDYB6S4vfgR9BiiRSrfoR90OpaYXtaBuEkAPgfrv0YrFtqQPFFn81Vg=='
org = 'hyps'
bucket = 'caenhv'

client = InfluxDBClient(url=url, token=token, org=org)

def query_api(query):
  return client.query_api().query(query)

if __name__ == '__main__':
  query = f'''
from(bucket: "{bucket}")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "caenhv.n1470")
    |> group(columns: ["module_id", "channel", "_field"])
    |> last()
'''
  for table in query_api(query):
    for record in table.records:
      print(f'Time: {record.get_time()}, Module ID: {record["module_id"]}, Channel: {record["channel"]}, '
            f'Field: {record.get_field()}, Value: {record.get_value()}')

  client.close()
