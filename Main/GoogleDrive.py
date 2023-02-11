import datetime
import logging
import os
import os.path
import config

from colorama import Fore

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logging.basicConfig(filename=config.APP_LOG_PATH, encoding='utf-8', level=logging.INFO, format="%(asctime)s: [%(levelname)s] [LINE:%(lineno)s] [FILE:%(filename)s] %(message)s")


class GoogleDrive:

    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.appdata'
        ]

    def create_folder(self, parent_id, folder_name):

        try:

            creds = None

            # The file token.json stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
            if os.path.exists(config.GOOGLE_DRIVE_TOKEN_PATH):
                creds = Credentials.from_authorized_user_file(config.GOOGLE_DRIVE_TOKEN_PATH, self.scopes)

            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(config.GOOGLE_DRIVE_CREDENTIAL_PATH, self.scopes)
                    creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(config.GOOGLE_DRIVE_TOKEN_PATH, 'w') as token:
                    token.write(creds.to_json())

            # create drive api client
            service = build('drive', 'v3', credentials=creds)

            folder_id = GoogleDrive().check_if_folder_exist(service, parent_id, folder_name)
            if folder_id:
                print(Fore.YELLOW + '[+]', Fore.GREEN + 'Found on Google Drive', Fore.MAGENTA + '{}'.format(folder_id), Fore.BLUE + '{}'.format(datetime.datetime.now().strftime("%Y %m %d %H:%M:%S")))
                return folder_id

            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }

            # pylint: disable=maybe-no-member
            file = service.files().create(body=file_metadata, fields='id').execute()

            return file.get('id')

        except Exception as exception:
            logging.error(exception)

    def check_if_folder_exist(self, service, parent_id, folder_name):
        try:

            files = []
            page_token = None
            while True:

                # pylint: disable=maybe-no-member
                query = f"parents = '{parent_id}'"

                response = service.files().list(
                    q=query,
                    # q="mimeType = 'application/vnd.google-apps.folder'",
                    fields='nextPageToken, ''files(id, name)',
                    pageToken=page_token).execute()

                for file in response.get('files', []):
                    if folder_name == file.get("name"):
                        return file.get("id")

                files.extend(response.get('files', []))
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break

            return False
        except Exception as exception:
            logging.error(exception)

        return files

    def upload(self, file, folder_id, delete_local=False):

        try:

            creds = None

            # The file token.json stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
            if os.path.exists(config.GOOGLE_DRIVE_TOKEN_PATH):
                creds = Credentials.from_authorized_user_file(config.GOOGLE_DRIVE_TOKEN_PATH, self.scopes)

            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(config.GOOGLE_DRIVE_CREDENTIAL_PATH, self.scopes)
                    creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(config.GOOGLE_DRIVE_TOKEN_PATH, 'w') as token:
                    token.write(creds.to_json())

            service = build('drive', 'v3', credentials=creds)

            file_metadata = {
                'name': os.path.basename(file),
                'parents': [folder_id]
            }
            media = MediaFileUpload(file, resumable=True)
            file_uploaded = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            print(Fore.YELLOW + '[+]', Fore.GREEN + 'Uploaded to Google Drive', Fore.MAGENTA + '{}'.format(file_uploaded.get('id')), Fore.BLUE + '{}'.format(datetime.datetime.now().strftime("%Y %m %d %H:%M:%S")))

            if delete_local:
                os.remove(file)
                print(Fore.YELLOW + '[+]', Fore.GREEN + 'File Deleted', Fore.MAGENTA + '{}'.format(file), Fore.BLUE + '{}'.format(datetime.datetime.now().strftime("%Y %m %d %H:%M:%S")))

            return file_uploaded

        except Exception as exception:
            logging.error(exception)
