import datetime
import os.path

import pytz # to get Brasil time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# if modifying these scopes, delete the file token.json
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# tutorial from: https://developers.google.com/workspace/calendar/api/quickstart/python

def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # the file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first time
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # define Brasil time
    br_tz = pytz.timezone("America/Sao_Paulo")
    now = datetime.datetime.now(tz=br_tz).isoformat()

    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
            timeZone="America/Sao_Paulo",  # define timezone
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # prints the start and name of the next 10 events
    for event in events:
      start_raw = event["start"].get("dateTime", event["start"].get("date"))
      if "dateTime" in event["start"]:
        # convert google timezone to Brasil timezone
        start_dt = datetime.datetime.fromisoformat(start_raw)
        if start_dt.tzinfo is None:
          start_dt = br_tz.localize(start_dt)
        else:
          start_dt = start_dt.astimezone(br_tz)
        start = start_dt.strftime("%Y-%m-%d %H:%M:%S")
      else:
        start = start_raw
      print(start, event["summary"])

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
