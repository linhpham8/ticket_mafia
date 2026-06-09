import os
import pandas as pd
import gspread 
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from os import environ

# This will be the scopes that will be set in your token file.
# Modify the scopes you want your token to have, you can use more than one, this needs to be list.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1HbDceXILwDW5EMz6v1-eWzp3IBYmIhsvkMNzDBKcTqs'



def main():
  creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
  credentials_path=environ.get("GOOGLESHEET_CREDENTIALS")
  if os.path.exists('token.pickle'):
      with open('token.pickle', 'rb') as token:
          creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
      else:
          flow = InstalledAppFlow.from_client_secrets_file(
              os.path.abspath('C:\\token\\credentials.json'), SCOPES)
          creds = flow.run_local_server(port=0)
  # Save the credentials for the next run
  with open('token.pickle', 'wb') as token:
      pickle.dump(creds, token)

def load_gsheet_v2(sheet_url:str,
                work_sheet:str,
                row_num:int) -> pd.DataFrame:

    ##Load gsheet
    directory = os.getcwd()

    # gc = gspread.oauth(credentials_filename = directory+'/DataTest/EXCEL/OMC/credentials.json',authorized_user_filename = directory+'/DataTest/EXCEL/OMC/authorized_user.json')
    gc = gspread.oauth(credentials_filename = 'C:\\token\\credentials.json',authorized_user_filename = 'C:\\token\\authorized_user.json')

    
    sh = gc.open_by_url(sheet_url)

    # Select work sheet
    worksheet = sh.worksheet(work_sheet)
    records = worksheet.get_all_records(head=row_num)
    return records
    
  # if __name__ == "__main__":
    # load_gsheet_v2(sheet_url = 'https://docs.google.com/spreadsheets/d/1m8tMnSraU7XwinmaXNNwvm05CO74hZBmY83hDGtAz_A/edit#gid=1874009347',
               # work_sheet = 'placeOrder',
               # row_num = 1
              # )  

if __name__ == '__main__':
  main()
  
  
  