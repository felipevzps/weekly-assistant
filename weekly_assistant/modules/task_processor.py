#!/usr/bin/env python

import re
from pathlib import Path
from datetime import datetime
from modules.utils import parse_day_sections, extract_day_date, is_future_date, log_action

def process_weekly_tasks(current_note_path, new_note_path):
    """
    Process tasks from the current weekly note to the new one.
    This handles pending tasks and future tasks, and removes them from the current note.
    """
    current_note_path = Path(current_note_path)
    new_note_path = Path(new_note_path)
    
    # read the content of both notes
    current_content = current_note_path.read_text(encoding="utf-8")
    new_content = new_note_path.read_text(encoding="utf-8")
    
    # parse the current note into sections
    header, day_sections = parse_day_sections(current_content)
    
    # extract pending tasks (uncompleted tasks from past or present days)
    pending_tasks = extract_pending_tasks(day_sections)
    
    # extract future tasks (tasks scheduled for future days)
    future_tasks = extract_future_tasks(day_sections)
    
    # update new note with the pending and future tasks
    updated_new_content = update_note_with_tasks(new_content, pending_tasks, future_tasks)
    
    # remove pending and future tasks from the current note
    updated_current_content = remove_tasks_from_note(current_content, pending_tasks, future_tasks)
    
    # write the updated content to both notes
    new_note_path.write_text(updated_new_content, encoding="utf-8")
    current_note_path.write_text(updated_current_content, encoding="utf-8")
    
    log_action(f"Processed tasks from {current_note_path} to {new_note_path}")
    return str(new_note_path)


def remove_tasks_from_note(content, pending_tasks, future_tasks):
    """
    Remove pending tasks and complete future day sections from the note content.
    """
    # parse the note into sections
    header, day_sections = parse_day_sections(content)
    
    # create a set of task texts for easy lookup
    task_texts = set()
    for task_block in pending_tasks:
        for task_line in task_block:
            task_texts.add(task_line.strip())
    
    # track which day sections are for future days
    future_day_sections = set()
    for date, info in future_tasks.items():
        # add the section header to our list of future days
        for section_header in day_sections.keys():
            if date in section_header:
                future_day_sections.add(section_header)
                break
        
        # add all task texts from future days to the removal set
        for task_block in info["tasks"]:
            for task_line in task_block:
                task_texts.add(task_line.strip())
    
    # remove pending tasks from each day's content
    for day_header, day_content in list(day_sections.items()):
        # if this is a future day section, remove it completely
        if day_header in future_day_sections or is_future_date(day_header):
            del day_sections[day_header]
            continue
            
        if not day_content:
            continue
            
        lines = day_content.splitlines()
        updated_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # check if this line is in the task_texts set
            if line in task_texts:
                # skip this line and any indented lines that follow
                i += 1
                while i < len(lines) and (lines[i].startswith('    ') or 
                                         lines[i].strip().startswith('  - ') or 
                                         lines[i].strip().startswith('    * ')):
                    i += 1
            else:
                updated_lines.append(lines[i])
                i += 1
                
        day_sections[day_header] = "\n".join(updated_lines)
    
    # reconstruct the note content
    new_content = header + "\n\n"
    for section_header, section_content in day_sections.items():
        new_content += section_header + "\n" + section_content.strip() + "\n\n"
    
    return new_content


def extract_pending_tasks(day_sections):
    """
    Extract pending (uncompleted) tasks from day sections.
    Returns a list of tasks with their hierarchies preserved.
    """
    pending_tasks = []
    today = datetime.now().date()
    
    for header, content in day_sections.items():
        # skip future days
        if is_future_date(header):
            continue
            
        # find all tasks in this section
        task_blocks = extract_task_blocks(content)
        
        # add incomplete tasks to pending list
        for task_block in task_blocks:
            if "- [x]" not in task_block[0]:  # only if parent task is not completed
                pending_tasks.append(task_block)
                
    return pending_tasks


def extract_future_tasks(day_sections):
    """
    Extract tasks scheduled for future days.
    Returns a dictionary mapping day dates to tasks.
    """
    future_tasks = {}
    
    for header, content in day_sections.items():
        # only process future days
        if not is_future_date(header):
            continue
            
        # extract weekday and date
        weekday, date = extract_day_date(header)
        if not date:
            continue
            
        # find all tasks in this section
        task_blocks = extract_task_blocks(content)
        
        # add tasks to future tasks dictionary
        if task_blocks:
            future_tasks[date] = {
                "header": f"{weekday} ({date})",  # without "###" prefix
                "tasks": task_blocks
            }
                
    return future_tasks


def extract_task_blocks(content):
    """
    Extract task blocks (tasks with their subtasks) from content.
    A task block is a list where the first element is the parent task
    and subsequent elements are indented subtasks.
    """
    task_blocks = []
    lines = content.splitlines()
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # check if this is a task line
        if line.startswith('- ['):
            # start a new task block
            task_block = [line]
            i += 1
            
            # look for subtasks (indented lines)
            while i < len(lines):
                next_line = lines[i].strip()
                
                # if line is indented or starts with a bullet point, it's a subtask
                if (lines[i].startswith('    ') or 
                    next_line.startswith('  - ') or 
                    next_line.startswith('    * ')):
                    task_block.append(lines[i])
                    i += 1
                else:
                    break
                    
            task_blocks.append(task_block)
        else:
            i += 1
            
    return task_blocks


def update_daily_tasks(weekly_note_path, calendar_events):
    """
    Update the weekly note with daily events from Google Calendar.
    """
    weekly_note_path = Path(weekly_note_path)
    content = weekly_note_path.read_text(encoding="utf-8")
    
    # parse the note into sections
    header, day_sections = parse_day_sections(content)
    
    # for each day section, add calendar events as tasks
    for day_header, day_content in day_sections.items():
        weekday, date = extract_day_date(day_header)
        
        if not weekday:
            continue
            
        # look for calendar events for this day
        if weekday in calendar_events:
            events = calendar_events[weekday]
            
            # check if events already exist in the day content
            updated_content = add_calendar_events_to_day(day_content, events)
            
            # update the section with new content
            day_sections[day_header] = updated_content
    
    # reconstruct the note content
    new_content = header + "\n\n"
    for section_header, section_content in day_sections.items():
        new_content += section_header + "\n" + section_content + "\n\n"
    
    # write the updated content back to the file
    weekly_note_path.write_text(new_content, encoding="utf-8")
    
    log_action(f"Updated daily tasks in {weekly_note_path}")
    return str(weekly_note_path)


def add_calendar_events_to_day(day_content, events):
    """
    Add calendar events to a day section, avoiding duplicates.
    """
    lines = day_content.splitlines()
    
    # extract existing event texts to avoid duplicates
    existing_events = []
    for line in lines:
        if line.strip().startswith("- ["):
            # extract text part after checkbox
            event_text = line.split("] ", 1)[-1].strip()
            existing_events.append(event_text)
    
    # add new events if they don't already exist
    for event in events:
        summary = event['summary']
        start_time = event['start'].strftime('%H:%M')
        end_time = event['end'].strftime('%H:%M')
        
        event_text = f"{summary} | {start_time} - {end_time}"
        
        if event_text not in existing_events:
            lines.append(f"- [ ] {event_text}")
            log_action(f"Added new event: {event_text}")
    
    return "\n".join(lines)


def update_note_with_tasks(content, pending_tasks, future_tasks):
    """
    Update the weekly note content with pending and future tasks.
    """
    # parse the note into sections
    header, day_sections = parse_day_sections(content)
    
    # find the Monday section to add pending tasks
    monday_section = None
    for section_header in day_sections.keys():
        if "Monday" in section_header:
            monday_section = section_header
            break
    
    if monday_section:
        # add pending tasks after "Organizar tarefas semanais"
        lines = day_sections[monday_section].splitlines()
        new_lines = []
        
        for line in lines:
            new_lines.append(line)
            if "Organizar tarefas semanais" in line:
                # add pending tasks right after this line
                for task_block in pending_tasks:
                    new_lines.extend(task_block)
                
        day_sections[monday_section] = "\n".join(new_lines)
    
    # add future tasks to their corresponding days
    for date, info in future_tasks.items():
        target_section = None
        
        # find the section with matching date
        for section_header in day_sections.keys():
            if date in section_header:
                target_section = section_header
                break
        
        if target_section:
            # add tasks to existing section
            current_content = day_sections[target_section]
            task_content = "\n".join(["\n".join(task_block) for task_block in info["tasks"]])
            day_sections[target_section] = current_content + "\n" + task_content
        else:
            # create new section with proper header formatting
            header_text = f"### {info['header']}"
            day_sections[header_text] = "\n".join(["\n".join(task_block) for task_block in info["tasks"]])
    
    # reconstruct the note content
    new_content = header + "\n\n"
    for section_header, section_content in day_sections.items():
        new_content += section_header + "\n" + section_content + "\n\n"
    
    return new_content
