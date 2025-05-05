#!/usr/bin/env python

import os
import re
from pathlib import Path
from datetime import datetime

def setup_paths():
    """Set up the paths needed for the application."""
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    paths = {
        "base_dir": base_dir,
        "calendar_path": os.path.join(base_dir, "calendar/google_calendar.md"),
        "token_path": os.path.join(base_dir, "config/token.json"),
        "credentials_path": os.path.join(base_dir, "config/credentials.json"),
        #"inbox_dir": os.path.join(base_dir, "inbox/"),                 # debug inbox dir 
        "inbox_dir": "/home/felipevzps/obsidian/workspace/inbox/",      # my vault inbox 
        #"archive_dir": os.path.join(base_dir, "archive/")              # debug archive dir 
        "archive_dir": "/home/felipevzps/obsidian/workspace/archive/"   # my valt archive 
    }
    
    # create directories if they don't exist
    for path_key in ["calendar_path"]:
        os.makedirs(os.path.dirname(paths[path_key]), exist_ok=True)
    
    return paths


def parse_day_sections(content):
    """
    Parse a markdown file into day sections.
    Returns a dictionary mapping day headers to their content.
    """
    day_pattern = r"(### \w+ \(\d{2}/\d{2}\).*?)(?=### |\Z)"
    day_sections = {}
    
    # extract the headers and content before any day section
    header_match = re.split(r"(?=^### .+)", content, maxsplit=1, flags=re.MULTILINE)
    header = header_match[0].strip() if header_match else ""
    
    # extract day sections
    for match in re.finditer(day_pattern, content, re.DOTALL | re.MULTILINE):
        section = match.group(1).strip()
        lines = section.splitlines()
        if not lines:
            continue
            
        day_title = lines[0]
        day_content = "\n".join(lines[1:]) if len(lines) > 1 else ""
        day_sections[day_title] = day_content
    
    return header, day_sections


def is_future_date(date_str):
    """Check if a date string (DD/MM) is in the future."""
    today = datetime.now().date()
    
    # extract day and month from the string
    match = re.search(r"(\d{2})/(\d{2})", date_str)
    if not match:
        return False
        
    day = int(match.group(1))
    month = int(match.group(2))
    
    # assume current year (might need adjustment for dates spanning year boundary)
    year = today.year
    
    try:
        date = datetime(year, month, day).date()
        return date > today
    except ValueError:
        # invalid date
        return False


def extract_day_date(header):
    """Extract weekday and date from a section header."""
    match = re.match(r"### (\w+) \((\d{2}/\d{2})\)", header)
    if match:
        weekday, date = match.groups()
        return weekday, date
    return None, None


def log_action(message):
    """Log an action with timestamp."""
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y - %H:%M:%S")
    print(f"[{timestamp}] {message}")
