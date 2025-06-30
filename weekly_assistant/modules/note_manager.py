#!/usr/bin/env python

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from modules.utils import log_action

def create_weekly_note(weekly_notes_dir):
    """Create a new weekly note with the correct template and return its path."""
    today = datetime.today()
    
    # get the week dates and metadata
    week_dates = get_week_dates(today)
    week_number = get_week_number(today)
    month_name = get_month_name(today)
    
    # generate content
    content = f"""# This Week in {month_name} (Week {week_number}, {today.year})

[[this-week|this week]]
#this-week

### Monday ({week_dates['Monday']})
- [ ] Organizar tarefas semanais

### Tuesday ({week_dates['Tuesday']})

### Wednesday ({week_dates['Wednesday']})

### Thursday ({week_dates['Thursday']})

### Friday ({week_dates['Friday']})

### Saturday ({week_dates['Saturday']})

### Sunday ({week_dates['Sunday']})

"""
    
    # generate filename
    ordinal_week = get_ordinal_week(week_number)
    filename = f"{ordinal_week}-week-{month_name.lower()}-{today.year}.md"
    
    # ensure directory exists
    weekly_notes_dir = Path(weekly_notes_dir)
    weekly_notes_dir.mkdir(parents=True, exist_ok=True)
    
    # write file
    note_path = weekly_notes_dir / filename
    note_path.write_text(content, encoding="utf-8")
    
    log_action(f"Created new weekly note: {note_path}")
    return str(note_path)


def archive_weekly_note(note_path, archive_dir):
    """Move a note from inbox to archive."""
    try:
        # ensure archive directory exists
        Path(archive_dir).mkdir(parents=True, exist_ok=True)
        
        # determine destination path
        source_path = Path(note_path)
        dest_path = Path(archive_dir) / source_path.name
        
        # move the file
        shutil.move(str(source_path), str(dest_path))
        
        log_action(f"Archived note from {source_path} to {dest_path}")
        return str(dest_path)
    except Exception as e:
        log_action(f"Error archiving note: {e}")
        raise


def get_week_dates(today=None):
    """Get dates for each day of the current week."""
    if today is None:
        today = datetime.today()
        
    # find start of week (Monday)
    start_of_week = today - timedelta(days=today.weekday())
    
    # generate dates for each day
    week_dates = {}
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        week_dates[day.strftime("%A")] = day.strftime("%d/%m")
        
    return week_dates


def get_week_number(today=None):
    """
    Calculate the week number within the month (1-5).
    
    Logic:
    - Days 1-7 = Week 1
    - Days 8-14 = Week 2
    - Days 15-21 = Week 3
    - Days 16-28 = Week 4
    - Days 29+ = Week 5 (if exists)

    Returns maximum of 5 weeks, with week 5 only for months that have 29+ days.
    """
    if today is None:
        today = datetime.today()
        
    day = today.day

    # divide day by 7 and round up
    week_number = ((day - 1) // 7) + 1

    # obs: never return more than 5 
    return min(week_number, 5)

def get_month_name(today=None):
    """Get the current month name."""
    if today is None:
        today = datetime.today()
        
    return today.strftime("%B")

def is_last_week_of_month(today=None):
    """
    Check if the current week is the last week of the month.
    
    Returns True if there are no more days in the month that would
    constitute a new week after the current week ends.
    """
    if today is None:
        today = datetime.today()
    
    # get the last day of the month
    last_day = calendar.monthrange(today.year, today.month)[1]
    
    # calculate what week the last day would be in
    last_day_week = ((last_day - 1) // 7) + 1
    current_week = get_week_number(today)
    
    return current_week == last_day_week

def get_ordinal_week(week_number, today=None):
    """
    Convert a week number to an ordinal string (first, second, etc.).
    Uses 'last' for the final week of the month regardless of number.
    """
    if today is None:
        today = datetime.today()
    
    # check if this is the last week of the month
    if is_last_week_of_month(today):
        return "last"
    
    ordinals = {
        1: "first",
        2: "second", 
        3: "third",
        4: "fourth",
        5: "fifth"
    }
    
    return ordinals.get(week_number, f"{week_number}th")

