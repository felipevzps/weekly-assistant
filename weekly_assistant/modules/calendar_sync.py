#!/usr/bin/env python

import os
import datetime
import pytz
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

def sync_google_calendar(calendar_path, token_path, credentials_path):
    """
    Syncs Google Calendar events for the current week and returns the events
    organized by day.
    """
    # authenticate and get calendar service
    service = authenticate_google_calendar(token_path, credentials_path)
    
    # get the current week's date range
    tz = pytz.timezone('America/Sao_Paulo')
    today = datetime.datetime.now(tz)
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    
    # get accepted events for the week
    accepted_events = get_accepted_events(
        service, 
        start_of_week.isoformat(), 
        end_of_week.isoformat()
    )
    
    # organize events by day
    events_by_day = organize_events(accepted_events)
    
    # save events to markdown for reference
    save_events_to_markdown(events_by_day, start_of_week, calendar_path)
    
    return events_by_day


def authenticate_google_calendar(token_path, credentials_path):
    """Authenticate with Google Calendar API and return service object."""
    creds = None
    
    # load existing credentials if available
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(
            token_path, ['https://www.googleapis.com/auth/calendar.readonly']
        )
    
    # refresh or acquire new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, ['https://www.googleapis.com/auth/calendar.readonly']
            )
            creds = flow.run_local_server(port=0)
            
        # save credentials for future use
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    # build and return the service
    service = build('calendar', 'v3', credentials=creds)
    return service


def get_accepted_events(service, start_time, end_time):
    """Get events from Google Calendar that the user has accepted."""
    try:
        # query calendar API
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        # filter for accepted events
        accepted_events = [
            event for event in events_result.get('items', [])
            if ('attendees' not in event or  # include events with no attendees
                any(attendee.get('self', False) and 
                    attendee.get('responseStatus') == 'accepted'
                    for attendee in event.get('attendees', [])))
        ]
        
        return accepted_events
    except Exception as error:
        print(f'An error occurred while fetching events: {error}')
        return []


def organize_events(events):
    """Organize events by day of the week."""
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
        # get start and end times
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        end_time = event['end'].get('dateTime', event['end'].get('date'))
        
        # convert to datetime objects in local timezone
        start_time = datetime.datetime.fromisoformat(start_time).astimezone(br_tz)
        end_time = datetime.datetime.fromisoformat(end_time).astimezone(br_tz)
        
        # get day of week and add to appropriate list
        day_of_week = start_time.strftime('%A')
        
        events_by_day[day_of_week].append({
            'summary': event.get('summary', 'No Title'),
            'start': start_time,
            'end': end_time
        })
    
    return events_by_day


def save_events_to_markdown(events_by_day, week_start_date, output_path):
    """Save events to a markdown file for reference."""
    # calculate dates for each day of the week
    week_dates = [
        (week_start_date + datetime.timedelta(days=i)).date() 
        for i in range(7)
    ]
    day_date_map = {d.strftime("%A"): d.strftime("%d/%m") for d in week_dates}
    
    # write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Google Calendar Events ({week_start_date.strftime('%d/%m/%Y')})\n\n")
        
        for day, events in events_by_day.items():
            date_str = day_date_map.get(day, '')
            f.write(f"### {day} ({date_str})\n")
            
            for event in events:
                start_time = event['start'].strftime('%H:%M')
                end_time = event['end'].strftime('%H:%M')
                f.write(f"{event['summary']} | {start_time} - {end_time}\n")
            
            f.write("\n")
    
    return output_path
