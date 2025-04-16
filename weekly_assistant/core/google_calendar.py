#!/usr/bin/env python

import os
import datetime
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def authenticate_google_calendar(token_path, credentials_path):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(
            token_path, ['https://www.googleapis.com/auth/calendar.readonly'])
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, ['https://www.googleapis.com/auth/calendar.readonly'])
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_accepted_events(service, start_of_week_str, end_of_week_str):
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_of_week_str,
            timeMax=end_of_week_str,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        accepted_events = [
            event for event in events_result.get('items', [])
            if 'attendees' in event and
               any(attendee.get('self', False) and attendee.get('responseStatus') == 'accepted'
                   for attendee in event['attendees'])
        ]
        return accepted_events

    except Exception as error:
        print(f'An error occurred: {error}')

def organize_events(events):
    br_tz = pytz.timezone('America/Sao_Paulo')
    events_by_day = {
        'Monday': [],
        'Tuesday': [],
        'Wednesday': [],
        'Thursday': [],
        'Friday': [],
        'Saturday': [],
        'Sunday': []
    }
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        end_time = event['end'].get('dateTime', event['end'].get('date'))
        start_time = datetime.datetime.fromisoformat(start_time).astimezone(br_tz)
        end_time = datetime.datetime.fromisoformat(end_time).astimezone(br_tz)
        day_of_week = start_time.strftime('%A')
        events_by_day[day_of_week].append({
            'summary': event.get('summary', 'No Title'),
            'start': start_time,
            'end': end_time
        })
    return events_by_day

def save_events_to_markdown(events_by_day, week_start_date, google_calendar_path):
    week_dates = [(week_start_date + datetime.timedelta(days=i)).date() for i in range(7)]
    day_date_map = {d.strftime("%A"): d.strftime("%d/%m") for d in week_dates}

    with open(google_calendar_path, 'a', encoding='utf-8') as f:
        f.write(f"# Google Calendar Events ({week_start_date.strftime('%d/%m/%Y')})\n\n")
        for day, events in events_by_day.items():
            date_str = day_date_map.get(day, '')
            f.write(f"### {day} ({date_str})\n")
            for event in events:
                start_time = event['start'].strftime('%H:%M')
                end_time = event['end'].strftime('%H:%M')
                f.write(f"{event['summary']} | {start_time} - {end_time}\n")
            f.write("\n")
    #print(f"Eventos do Google Calendar salvos em {google_calendar_path}")

def main(google_calendar_path, token_path, credentials_path):
    service = authenticate_google_calendar(token_path, credentials_path)
    tz = pytz.timezone('America/Sao_Paulo')
    today = datetime.datetime.now(tz)
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    start_of_week_str = start_of_week.isoformat()
    end_of_week_str = end_of_week.isoformat()
    accepted_events = get_accepted_events(service, start_of_week_str, end_of_week_str)
    events_by_day = organize_events(accepted_events)
    save_events_to_markdown(events_by_day, start_of_week, google_calendar_path)
