#!/usr/bin/env python

from pathlib import Path
from datetime import datetime, timedelta

def get_week_dates(today=None):
    if today is None:
        today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    week_dates = {}
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        week_dates[day.strftime("%A")] = day.strftime("%d/%m")
    return week_dates

def get_week_number(today=None):
    if today is None:
        today = datetime.today()
    day = today.day
    first_day = datetime(today.year, today.month, 1)
    first_weekday = first_day.weekday()
    return ((day + first_weekday - 1) // 7) + 1

def get_month_name(today=None):
    if today is None:
        today = datetime.today()
    return today.strftime("%B")

def generate_weekly_note_content(today=None):
    if today is None:
        today = datetime.today()
    week_dates = get_week_dates(today)
    week_number = get_week_number(today)
    content = f"""# This Week in {get_month_name(today)} (Week {week_number}, {today.year})

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
    return content

def save_weekly_note(content, weekly_notes_dir):
    today = datetime.today()
    week_number = get_week_number(today)
    month_name = get_month_name(today).lower()
    year = today.year
    ORDINALS = {
        1: "first",
        2: "second",
        3: "third",
        4: "fourth",
        5: "last",
    }
    ordinal_week = ORDINALS.get(week_number, f"{week_number}th")
    final_filename = f"{ordinal_week}-week-{month_name}-{year}.md"
    weekly_notes_dir = Path(weekly_notes_dir)
    weekly_notes_dir.mkdir(parents=True, exist_ok=True)
    full_path = weekly_notes_dir / final_filename
    full_path.write_text(content, encoding="utf-8")
    #print(f"Nota semanal criada em: {full_path}")
    return str(full_path)

def main(weekly_notes_dir):
    note_content = generate_weekly_note_content()
    return save_weekly_note(note_content, weekly_notes_dir)
