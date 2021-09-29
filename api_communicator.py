#!usr/bin/env python

""" Handles the part of this algorithm that makes use of Google Sheets API. """

from google.oauth2 import service_account
from googleapiclient.discovery import build
import googleapiclient.errors

from PyQt5.QtCore import QObject, pyqtSignal

# helper_modules is a self defined module
from helper_modules import helper_functions

JSON_FILE_NAME = 'g_sheet_info.json'

json_file_content = helper_functions.json_file_loader(file_name=JSON_FILE_NAME)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = json_file_content.get('api_key_file')


# Using the imported service_account module, new creds are generated.
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = json_file_content.get('google_sheet_id')
READING_RANGE = json_file_content.get('wb_range_to_read')
WRITING_RANGE_NAME = json_file_content.get('wb_range_to_write')
FILE_RANGE_TO_CLEAR = json_file_content.get('wb_range_to_clear')


class WorkerThread(QObject):
    # Custom signals
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    unfinished = pyqtSignal()

    def __init__(self):
        super(WorkerThread, self).__init__()

    def api_communicator(self):
        try:
            # Create the service that will be used
            service = build('sheets', 'v4', credentials=creds)

            # Call the Google Sheets API
            sheet = service.spreadsheets()

            # Clear existing data in spreadsheet cells where new data will be written
            # To learn more about this, check Google Sheets API reference docs
            clear_data_request = service.spreadsheets().values().batchClear(spreadsheetId=SPREADSHEET_ID,
                                                                            body={'ranges': FILE_RANGE_TO_CLEAR})
            clear_data_request.execute()

            sheet_values = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                              range=READING_RANGE).execute()

            # The returned sheet value will be a nested list
            # The first value in a list is the label's content
            # The second value is the current product ID
            # The third value is the current product producer
            # The fourth value is the current product ordered quantity

            all_values = sheet_values.get('values', [])[1:]

            sorted_values = sorted(all_values, key=lambda x:  x[2], reverse=True)

            sorted_values_len = len(sorted_values)

            current_row = 2
            final_data = []
            for current_index in range(sorted_values_len):
                if current_index == 0:
                    final_data.append([sorted_values[0][2]])
                    final_data.append(sorted_values[current_index])

                elif current_index == sorted_values_len - 1:
                    final_data.append(sorted_values[current_index])
                    final_data.append([sorted_values[current_index][2]])

                elif sorted_values[current_index][2] != sorted_values[current_index + 1][2]:
                    # First append the current label content
                    final_data.append(sorted_values[current_index])
                    # Then append the current producer
                    final_data.append([sorted_values[current_index][2]])
                    # Then append the next producer
                    final_data.append([sorted_values[current_index + 1][2]])

                else:
                    final_data.append(sorted_values[current_index])

            write_data_request = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID,
                                                                        range=f'{WRITING_RANGE_NAME}{current_row}',
                                                                        valueInputOption='USER_ENTERED',
                                                                        insertDataOption='OVERWRITE',
                                                                        body={'values': final_data})
            response = write_data_request.execute()
            if response:
                self.finished.emit()
            else:
                self.unfinished.emit()

        except googleapiclient.errors.HttpError:
            self.unfinished.emit()


if __name__ == '__main__':
    pass
