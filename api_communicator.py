#!usr/bin/env python

""" Handles the part of this algorithm that makes use of Google Sheets API. """

from google.oauth2 import service_account
from googleapiclient.discovery import build

# helper_modules is a self defined module
from helper_modules import helper_functions

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'api_key.json'


# Using the imported service_account module, new creds are generated.
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1kbIYKsooISlbAsKxgHYLQzzWeTKcT6LpE__1ReSzkA4'
READING_RANGE_NAME = 'IMPORT X STAMPA!A:C'
WRITING_RANGE_NAME = 'IMPORT X STAMPA!J'

FILE_RANGE_TO_CLEAR = 'IMPORT X STAMPA!J2:L1000'


def main():
    # Create the service that will be used
    service = build('sheets', 'v4', credentials=creds)

    # Call the Google Sheets API
    sheet = service.spreadsheets()
    sheet_values = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                      range=READING_RANGE_NAME).execute()

    # The returned sheet value will be a nested list
    # The first value in a list is the label's content
    # The second value is the current product ID
    # The third value is the current product producer
    # The fourth value is the current product ordered quantity

    all_values = sheet_values.get('values', [])[1:]

    sorted_values = sorted(all_values, key=lambda x: (x[2], x[1]), reverse=True)

    sorted_values_len = len(sorted_values)

    # Clear existing data in spreadsheet

    # To learn more about this, check Google Sheets API reference docs
    clear_data_request = service.spreadsheets().values().batchClear(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                                    body={'ranges': FILE_RANGE_TO_CLEAR})
    clear_data_request.execute()

    current_row = 2
    final_data = []
    for test in range(sorted_values_len):
        if test == 0:
            final_data.append([sorted_values[0][2]])
            final_data.append(sorted_values[test])

        elif test == sorted_values_len - 1:
            final_data.append(sorted_values[test])
            final_data.append([sorted_values[test][2]])

        elif sorted_values[test][2] != sorted_values[test + 1][2]:
            # First append the current label content
            final_data.append(sorted_values[test])
            # Then append the current producer
            final_data.append([sorted_values[test][2]])
            # Then append the next producer
            final_data.append([sorted_values[test + 1][2]])

        else:
            final_data.append(sorted_values[test])

    request = service.spreadsheets().values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                     range=f'{WRITING_RANGE_NAME}{current_row}',
                                                     valueInputOption='USER_ENTERED',
                                                     insertDataOption='OVERWRITE',
                                                     body={'values': final_data})
    response = request.execute()
    print(response)


if __name__ == '__main__':
    main()
