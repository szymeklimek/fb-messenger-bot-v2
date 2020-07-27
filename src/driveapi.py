from __future__ import print_function

import io
import pickle
import random
import os.path

from apiclient import http

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class DriveSetup:

    def __init__(self):

        self.SCOPES = ['https://www.googleapis.com/auth/drive.metadata',
                       'https://www.googleapis.com/auth/drive']
        self.drive_service = None
        self.setup_service()

    def setup_service(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'drive_creds.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.drive_service = build('drive', 'v3', credentials=creds)

    def create_random_img(self):

        img_path = "img.jpg"
        result = self.drive_service.files().list(
            q="mimeType = 'image/jpeg' and '1OoTovBUaprMrJeuJ0ZlLq92c-RiOweXN' in parents",
            spaces='drive',
        ).execute()
        imglist = result.get('files', [])
        img_id = random.choice(imglist).get('id')
        file = self.drive_service.files().get_media(fileId=img_id)
        fh = io.FileIO(img_path, 'wb')
        downloader = http.MediaIoBaseDownload(fh, file)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

        return img_path
