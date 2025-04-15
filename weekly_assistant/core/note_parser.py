#!/usr/bin/env python

import re
from pathlib import Path

def main(inbox_dir, pending_tasks_path, future_tasks_path):
    weekly_files = list(Path(inbox_dir).glob("*-week-*.md"))
    if not weekly_files:
        raise FileNotFoundError("Nenhum arquivo semanal encontrado no diretório especificado.")
    
    input_path = weekly_files[0]
    print(f"Arquivo semanal selecionado: {input_path}")
    original_content = input_path.read_text(encoding="utf-8")
    block_pattern = r"(?=^### .+?$)(.*?)(?=^### |\Z)"
    task_pattern = r"^- \[ \] .+"
    pending_tasks = []
    future_tasks = []
    cleaned_content = []
    header_match = re.split(r"^### .+", original_content, maxsplit=1, flags=re.MULTILINE)
    if header_match:
        cleaned_content.append(header_match[0].strip())
    blocks = re.findall(block_pattern, original_content, flags=re.DOTALL | re.MULTILINE)
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        title = lines[0].strip()
        body = lines[1:] if len(lines) > 1 else []
        date_match = re.search(r"\((\d{2})/(\d{2})\)", title)
        is_future = False
        if date_match:
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            if month > 4 or (month == 4 and day > 20):
                is_future = True
        if is_future:
            task_lines = [line for line in body if re.match(task_pattern, line)]
            if task_lines or title:
                future_tasks.append((title, task_lines))
            continue
        new_body = []
        for line in body:
            if re.match(task_pattern, line):
                pending_tasks.append(line)
            else:
                new_body.append(line)
        cleaned_block = [title] + new_body
        cleaned_content.append("\n".join(cleaned_block).strip())
    input_path.write_text("\n\n".join(cleaned_content).strip() + "\n", encoding="utf-8")
    Path(pending_tasks_path).write_text(
        "### Tarefas pendentes da semana anterior\n" + "\n".join(pending_tasks) + "\n",
        encoding="utf-8"
    )
    with open(future_tasks_path, "w", encoding="utf-8") as f:
        f.write("### Tarefas do futuro baseado na semana anterior\n")
        for title, tasks in future_tasks:
            f.write(f"{title}\n\n")
            for task in tasks:
                f.write(f"{task}\n")
            f.write("\n")
    print(f"Processamento de nota semanal concluído: {input_path}")
    return(Path(input_path))
