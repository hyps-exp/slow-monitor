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

def set_protection(start_column, end_column):
  protect_request = {
    "requests": [
      {
        "addProtectedRange": {
          "protectedRange": {
            "range": {
              "sheetId": worksheet.id,
              "startRowIndex": 0,
              "startColumnIndex": start_column,
              "endColumnIndex": end_column
            },
            "description": "Protect entire sheet",
            "warningOnly": False  # uneditable
          }
        }
      }
    ]
  }
  spreadsheet.batch_update(protect_request)

def request_format_number(start_column, end_column, pattern):
  requests = {
    "requests": [
      {
        "repeatCell": {
          "range": {
            "sheetId": worksheet.id,
            "startRowIndex": 1,
            "startColumnIndex": start_column,
            "endColumnIndex": end_column
          },
          "cell": {
            "userEnteredFormat": {
              "numberFormat": {
                "type": "NUMBER",
                "pattern": pattern
              }
            }
          },
          "fields": "userEnteredFormat.numberFormat"
        }
      }
    ]
  }
  spreadsheet.batch_update(requests)

def update():
  csv_file = '/misc/subdata/runsummary.csv'
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
  worksheet.update(data, 'A1')
  request_format_number(start_column=4, end_column=6, pattern='#,##0')
  request_format_number(start_column=6, end_column=7, pattern='0.00')
  request_format_number(start_column=7, end_column=8, pattern='#,##0')
  request_format_number(start_column=8, end_column=9, pattern='0.000000')
  request_format_number(start_column=9, end_column=10, pattern='#,##0')
  request_format_number(start_column=10, end_column=13, pattern='0.000000')
  # set_protection(start_column=0, end_column=32)
