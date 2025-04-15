#!/usr/bin/env python

import re
from pathlib import Path

def parse_google_calendar(path):
    content = path.read_text(encoding="utf-8")
    calendar = {}
    current_day_key = None
    lines = content.splitlines()
    for line in lines:
        match = re.match(r"^### (\w+) \((\d{2}/\d{2})\)", line)
        if match:
            weekday, date = match.groups()
            current_day_key = f"{weekday} ({date})"
            calendar[current_day_key] = []
        elif current_day_key and line.strip():
            calendar[current_day_key].append(line.strip())
    return calendar

def inserir_calendario_no_markdown(md_lines, google_calendar):
    nova_linha = []
    for line in md_lines:
        nova_linha.append(line)
        match = re.match(r"^### (\w+) \((\d{2}/\d{2})\)", line)
        if match:
            weekday, date = match.groups()
            key = f"{weekday} ({date})"
            if key in google_calendar:
                for tarefa in google_calendar[key]:
                    nova_linha.append(f"- [ ] {tarefa}")
                nova_linha.append("")
    return nova_linha

def main(inbox_dir, google_calendar_path, weekly_note_path):
    weekly_note_path = Path(weekly_note_path)
    original_md = weekly_note_path.read_text(encoding="utf-8").splitlines()
    google_calendar = parse_google_calendar(Path(google_calendar_path))
    novo_md = inserir_calendario_no_markdown(original_md, google_calendar)
    weekly_note_path.write_text("\n".join(novo_md), encoding="utf-8")
    print(f"Atividades do Google Calendar adicionadas a {weekly_note_path}")
