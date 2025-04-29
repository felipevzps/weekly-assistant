#!/usr/bin/env python

import os
import argparse
from pathlib import Path
from datetime import datetime
from modules.calendar_sync import sync_google_calendar
from modules.note_manager import create_weekly_note, archive_weekly_note
from modules.task_processor import process_weekly_tasks, update_daily_tasks
from modules.utils import setup_paths

def main():
    """Main entry point for my weekly assistant."""
    parser = argparse.ArgumentParser(prog="weekly-assistant", description="Weekly note management assistant.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--weekly", action="store_true", help="Process weekly notes - create new and archive old")
    group.add_argument("--daily", action="store_true", help="Update current weekly note with today's events")
    args = parser.parse_args()

    # setup paths
    paths = setup_paths()
    
    # log execution start
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y - %H:%M:%S")
    print(f"[{timestamp}] running weekly assistant...")

    try:
        if args.weekly:
            run_weekly_process(paths)
        elif args.daily:
            run_daily_process(paths)
    except Exception as e:
        print(f"[{timestamp}] Error: {e}")
        return 1
    
    print(f"[{timestamp}] weekly assistant completed successfully")
    return 0

def run_weekly_process(paths):
    """Run the weekly process to create a new note and archive the old one."""
    # find the current weekly note
    current_weekly_note = find_current_weekly_note(paths["inbox_dir"])
    
    # create a new weekly note
    new_note_path = create_weekly_note(paths["inbox_dir"])
    
    # process tasks from old note to new note (handles pending and future tasks)
    process_weekly_tasks(current_weekly_note, new_note_path)
    
    # archive the old weekly note
    archive_weekly_note(current_weekly_note, paths["archive_dir"])

def run_daily_process(paths):
    """Run the daily process to update the current weekly note with calendar events."""
    # sync calendar events
    calendar_events = sync_google_calendar(
        paths["calendar_path"], 
        paths["token_path"], 
        paths["credentials_path"]
    )
    
    # find current weekly note
    weekly_note_path = find_current_weekly_note(paths["inbox_dir"])
    
    # update the weekly note with calendar events
    update_daily_tasks(weekly_note_path, calendar_events)
    
    # clean up temporary files
    if os.path.exists(paths["calendar_path"]):
        os.remove(paths["calendar_path"])

def find_current_weekly_note(inbox_dir):
    """Find the current weekly note in the inbox directory."""
    weekly_files = list(Path(inbox_dir).glob("*-week-*.md"))
    if not weekly_files:
        raise FileNotFoundError("No weekly note found in the specified directory.")
    
    # return the most recent weekly note
    return sorted(weekly_files)[-1]
