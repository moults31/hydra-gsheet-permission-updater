# SPDX-FileCopyrightText: 2022 Zac Moulton
#
# SPDX-License-Identifier: MIT

import os
import argparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDS_PATH = '/secrets/cred.json'
USER_EMAILS_PATH = '/secrets/user_emails.txt'
NAME_FILTERS_PATH = '/secrets/name_filters.txt'

def main(delete):
    """
    Updates permissions for filtered spreadsheets owned by the authenticated user.
    Or, if delete is specified, deletes them instead.
    Useful in cases where the spreadsheet is currently only visible to the service account that created it.
    Gives "writer" permissions to all users in user_emails.txt
    """

    for path in [CREDS_PATH, USER_EMAILS_PATH, NAME_FILTERS_PATH]:
        if not os.path.isfile(path):
            raise RuntimeError(f"No such file {path}")

    creds = service_account.Credentials.from_service_account_file(
            CREDS_PATH, scopes=SCOPES)

    # create drive api clients
    service = build('drive', 'v3', credentials=creds)
    service_v2 = build('drive', 'v2', credentials=creds)

    # Read secret files
    name_filters = []
    with open(NAME_FILTERS_PATH, 'r') as name_filters_file:
        for line in name_filters_file.readlines():
            name = line.replace('\n', '')
            name_filters.append(name)

    user_emails = []
    with open(USER_EMAILS_PATH, 'r') as user_emails_file:
        for line in user_emails_file.readlines():
            user_email = line.replace('\n', '')
            user_emails.append(user_email)

    # Loop through all discovered files
    files = []
    page_token = None
    while True:
        response = service.files().list(q="",
                                        spaces='drive',
                                        fields='nextPageToken, '
                                                'files(id, name)',
                                        pageToken=page_token).execute()
        for file in response.get('files', []):
            name = file.get("name")
            print(F'Found file: {name}, {file.get("id")}')

            for name_filter in name_filters:
                if name_filter in name:
                    if delete:
                        print(f"Deleting {name}, matched filter {name_filter}")
                        service_v2.files().delete(fileId=file.get("id")).execute()

                    else:
                        existing_permissions = service_v2.permissions().list(fileId=file.get("id")).execute()
                        existing_permitted_emails = []
                        for permission in existing_permissions['items']:
                            existing_permitted_emails.append(permission['emailAddress'])

                        for user_email in user_emails:
                            if user_email in existing_permitted_emails:
                                continue
                            print(f"Adding {user_email} to {file.get('name')}")
                            new_permission = {
                                'value': user_email,
                                'type': 'user',
                                'role': 'writer'
                            }
                            service_v2.permissions().insert(fileId=file.get("id"), body=new_permission).execute()

        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--delete", action="store_true", dest="delete", default=False)
    args = parser.parse_args()

    main(args.delete)