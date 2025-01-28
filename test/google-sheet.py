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
          "startRowIndex": 1,  # 0ベースの行番号 (ヘッダーを含める場合は0)
          "startColumnIndex": 4,  # E列の開始 (A=0, B=1, ..., E=4)
          "endColumnIndex": 6   # E列の終了
        },
        "cell": {
          "userEnteredFormat": {
            "numberFormat": {
              "type": "NUMBER",
              "pattern": "#,##0"  # カンマ区切りの整数フォーマット
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
#               "startRowIndex": 0,  # 0ベースで指定（ヘッダーを含む）
#               "startColumnIndex": 0,  # 行全体の開始（A列）
#               "endColumnIndex": worksheet.col_count  # 最終列まで
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
#                 "red": 0.3,   # ピンク色
#                 "green": 0.8,
#                 "blue": 0.4
#               }
#             }
#           }
#         },
#         "index": 0  # ルールの優先順位
#       }
#     }
  ]
}

spreadsheet.batch_update(requests)
