import gspread
from google.oauth2.service_account import Credentials
import csv

SERVICE_ACCOUNT_FILE = '/misc/software/slow-monitor/key/hyps-project-8c7f1d11b316.json'

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

client = gspread.authorize(credentials)

spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1VBGUxsFfQNpFoOjkS36u_2WvrtppF8zwodLceM9touk/edit'
spreadsheet = client.open_by_url(spreadsheet_url)

worksheet = spreadsheet.sheet1

csv_file = '/misc/subdata/runsummary.csv'
# with open(csv_file, mode='r') as file:
#   reader = csv.reader(file)
#   data = list(reader)
with open(csv_file, mode="r") as file:
  reader = csv.reader(file)
  data = []
  for row in reader:
    processed_row = []
    for cell in row:
      if cell.isdigit():
        processed_row.append(int(cell))
      else:
        try:
          processed_row.append(float(cell))
        except ValueError:
          processed_row.append(cell)
    data.append(processed_row)

# worksheet.clear()
worksheet.update(data, 'A1')

requests = {
  "requests": [
    {
      "repeatCell": {
        "range": {
          "sheetId": worksheet.id,
          "startRowIndex": 1,
          "startColumnIndex": 0,
          "endColumnIndex": 1
        },
        "cell": {
          "userEnteredFormat": {
            "numberFormat": {
              "type": "NUMBER",
              #"pattern": "#,##0.000000"
              "pattern": "0"
            }
          }
        },
        "fields": "userEnteredFormat.numberFormat"
      }
    }
#     {
#       "updateSheetProperties": {
#         "properties": {
#           "sheetId": worksheet.id,
#           "gridProperties": {
#             "frozenRowCount": 1,
#             "frozenColumnCount": 1
#           }
#         },
#         "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"
#       }
#     },
#     {
#       "addConditionalFormatRule": {
#         "rule": {
#           "ranges": [
#             {
#               "sheetId": worksheet.id,
#               "startRowIndex": 0,
#               "startColumnIndex": 0,
#               "endColumnIndex": worksheet.col_count
#             }
#           ],
#           "booleanRule": {
#             "condition": {
#               "type": "CUSTOM_FORMULA",
#               "values": [
#                 {
#                   # "userEnteredValue": '=AND(ISNUMBER(SEARCH("production", $D1)), NOT(ISNUMBER(SEARCH("check", $D1))), NOT(ISNUMBER(SEARCH("test", $D1))))'
#                   # "userEnteredValue": '=AND(ISNUMBER(SEARCH("cosmic", $D1)), NOT(ISNUMBER(SEARCH("check", $D1))), NOT(ISNUMBER(SEARCH("test", $D1))))'
#                   # "userEnteredValue": '=AND(ISNUMBER(SEARCH("pedestal", $D1)), NOT(ISNUMBER(SEARCH("check", $D1))), NOT(ISNUMBER(SEARCH("test", $D1))))'
#                   "userEnteredValue": '=AND(ISNUMBER(SEARCH("study", $D1)), NOT(ISNUMBER(SEARCH("check", $D1))), NOT(ISNUMBER(SEARCH("test", $D1))))'
#                 }
#               ]
#             },
#             "format": {
#               "backgroundColor": {
#                 "red": 0.3,
#                 "green": 0.8,
#                 "blue": 0.4
#               }
#             }
#           }
#         },
#         "index": 0
#       }
#     }
  ]
}

spreadsheet.batch_update(requests)
