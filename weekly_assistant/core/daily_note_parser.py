import re
from pathlib import Path
from datetime import datetime

def parse_google_calendar(path: Path):
    """
    Parses a markdown-formatted calendar file into a dictionary.
    Each key is a day (e.g., 'Wednesday (16/04)'), and the value is a list of task strings.
    """
    path = Path(path)
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


def inserir_tarefas_do_dia(day_key, section_lines, google_calendar):
    """
    Inserts new tasks from the calendar into the given section of the markdown,
    avoiding duplication of existing tasks (regardless of checkbox state).
    """
    result_lines = list(section_lines)

    if day_key in google_calendar:
        # Extract just the text of each task, ignoring its checkbox state
        existing_task_texts = [
            line.split("] ", 1)[-1].strip()
            for line in section_lines
            if line.startswith("- [")
        ]

        # Append only tasks not already present
        for task in google_calendar[day_key]:
            if task.strip() not in existing_task_texts:
                result_lines.append(f"- [ ] {task.strip()}")
                now = datetime.now()
                timestamp = now.strftime("%d/%m/%Y - %H:%M:%S")
                print(f"[{timestamp}] Novo evento adicionado para {day_key}: {task}")

                # Add blank line for formatting
                #result_lines.append("")

    # Add blank line in the end block of day
    if result_lines and result_lines[-1].strip() != "":
        result_lines.append("")

    return result_lines


def inserir_calendario_no_markdown(md_lines, google_calendar):
    """
    Inserts tasks from the calendar into the appropriate sections of the markdown file,
    keeping formatting and avoiding duplication.
    """
    updated_lines = []
    current_day_key = None
    section_lines = []

    for line in md_lines:
        # Detect start of new day section
        match = re.match(r"^### (\w+) \((\d{2}/\d{2})\)", line)
        if match:
            # Process previous section before starting new one
            if current_day_key:
                updated_lines.extend(inserir_tarefas_do_dia(current_day_key, section_lines, google_calendar))
                section_lines = []

            weekday, date = match.groups()
            current_day_key = f"{weekday} ({date})"

        section_lines.append(line)

    # Process last section after loop
    if current_day_key:
        updated_lines.extend(inserir_tarefas_do_dia(current_day_key, section_lines, google_calendar))
    else:
        updated_lines.extend(section_lines)

    return updated_lines


def processar_arquivo_semanal(inbox_dir, google_calendar):
    """
    Processes the weekly markdown file from the given directory and inserts tasks
    from the Google Calendar into the file.
    """
    # Find the weekly file with the pattern '*-week-*.md'
    weekly_files = list(Path(inbox_dir).glob("*-week-*.md"))
    if not weekly_files:
        raise FileNotFoundError("Nenhum arquivo semanal encontrado no diretório especificado.")
   
    # Assume there's only one weekly file, select the first match
    input_path = weekly_files[0]
    #print(f"Arquivo semanal selecionado: {input_path}")

    # Read the markdown content
    md_lines = input_path.read_text(encoding="utf-8").splitlines()

    # Insert tasks into the markdown file
    updated_lines = inserir_calendario_no_markdown(md_lines, google_calendar)

    # Save the updated markdown file
    input_path.write_text("\n".join(updated_lines), encoding="utf-8")
    #print(f"Arquivo semanal atualizado: {input_path}")


def main(inbox_dir, google_calendar):
    #"""
    #Main function to update the weekly markdown file with new tasks from a Google Calendar.
    #It reads the existing markdown file and the calendar, updates the file, and saves it back.
    #"""
    # Define path for the inbox directory and the Google Calendar file
    #inbox_dir = "inbox"  # Directory containing .md files
    #calendar_path = Path("../calendar/google_calendar.md")

    # Parse the Google Calendar markdown file
    google_calendar = parse_google_calendar(google_calendar)

    # Process the weekly markdown file in the inbox directory
    processar_arquivo_semanal(inbox_dir, google_calendar)
