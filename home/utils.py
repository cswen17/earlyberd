import os

from django.conf import settings
from google_auth_oauthlib.flow import InstalledAppFlow


# todo: move
CREDENTIALS_PATH =  os.path.join(settings.BASE_DIR, 'credentials.json')
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
]


def gmail_credentials():
    """
    Loads Google API credentials from file system and returns a
    credentials dict.
    """
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_PATH,
        GMAIL_SCOPES,
    )
    return flow.run_local_server()
