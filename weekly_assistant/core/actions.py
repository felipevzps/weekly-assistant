#!/usr/bin/env python

import os 
import shutil
from datetime import datetime
from core import google_calendar, note_generator, note_parser, organize_weekly_tasks, organize_google_calendar_weekly_tasks

def remove_temporary_files(paths):
    for path in paths:
        try:
            os.remove(path)
            #print(f"Arquivo temporário removido: {path}")
        except OSError as e:
            print(f"Erro ao remover {path}: {e}")

def move_note_to_archive(inbox, archive):
    try:
        shutil.move(inbox, archive)
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y - %H:%M:%S")
        print(f"[{timestamp}] Nota movida de {inbox} para {archive}")
    except Exception as e:
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y - %H:%M:%S")
        print(f"[{timestamp}] Erro ao mover arquivo: {e}")

def main():
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    
    calendar_path = os.path.join(BASE_DIR, "../calendar/google_calendar.md")
    token_path = os.path.join(BASE_DIR, "../config/token.json")
    credentials_path = os.path.join(BASE_DIR, "../config/credentials.json")
    #inbox_dir = os.path.join(BASE_DIR, "inbox")                    # just for debugging inside core directory
    #archive_dir = os.path.join(BASE_DIR, "archive")
    inbox_dir = "/home/felipevzps/obsidian/workspace/inbox"         # obsidian inbox 
    archive_dir = "/home/felipevzps/obsidian/workspace/archive"     # obsidian archive
    weekly_notes_dir = inbox_dir
    pending_tasks_path = os.path.join(BASE_DIR, "../tasks/tarefas_pendentes.md")
    future_tasks_path = os.path.join(BASE_DIR, "../tasks/tarefas_futuras.md")
    
    #print("Executando google_calendar.py...")
    google_calendar.main(calendar_path, token_path, credentials_path)
    
    #print("Executando note_parser.py...")
    last_week_path = note_parser.main(inbox_dir, pending_tasks_path, future_tasks_path)
    
    #print("Executando note_generator.py...")
    new_note_path = note_generator.main(weekly_notes_dir)
    
    #print("Executando organize_weekly_tasks.py...")
    organize_weekly_tasks.main(inbox_dir, pending_tasks_path, future_tasks_path, weekly_note_path=new_note_path)
    
    #print("Executando organize_google_calendar_weekly_tasks.py...")
    organize_google_calendar_weekly_tasks.main(inbox_dir, calendar_path, weekly_note_path=new_note_path)
    
    #print("Removendo arquivos temporários...")
    remove_temporary_files([calendar_path, pending_tasks_path, future_tasks_path])

    #print("Movendo nota da semana passada para archive...")
    move_note_to_archive(last_week_path, archive_dir)
