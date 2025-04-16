#!/usr/bin/env python

import re
from pathlib import Path

def parse_tarefas_pendentes(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    tarefas = [line for line in lines if line.startswith("- [ ]")]
    return tarefas

def parse_tarefas_futuras(path):
    content = path.read_text(encoding="utf-8")
    blocos = re.split(r"^### ", content, flags=re.MULTILINE)[1:]
    tarefas_por_data = {}
    for bloco in blocos:
        header, *tarefas = bloco.strip().splitlines()
        match = re.match(r"(\w+) \((\d{2}/\d{2})\)", header)
        if match:
            dia_semana, data = match.groups()
            tarefas_limpas = [t for t in tarefas if t.strip().startswith("- [ ]")]
            if tarefas_limpas:
                tarefas_por_data[data] = {
                    "header": f"{dia_semana} ({data})",
                    "tarefas": tarefas_limpas
                }
    return tarefas_por_data

def inserir_tarefas_no_markdown(md_lines, tarefas_pendentes, tarefas_futuras):
    nova_linha = []
    for line in md_lines:
        nova_linha.append(line)
        # add tarefas pendentes logo após a linha "Organizar tarefas semanais"
        if line.strip() == "- [ ] Organizar tarefas semanais":
            for t in tarefas_pendentes:
                nova_linha.append(t)
        # procura blocos de data para inserir tarefas futuras -> blocos aqui são os "tópicos" diários... tentei evitar regex mas assim ficou mais fácil
        match = re.match(r"^### (\w+) \((\d{2}/\d{2})\)", line)
        if match:
            _, data = match.groups()
            if data in tarefas_futuras:
                for tarefa in tarefas_futuras[data]["tarefas"]:
                    nova_linha.append(tarefa)
                nova_linha.append("")
                tarefas_futuras.pop(data)

    # add tarefas futuras que não foram inseridas em nenhum bloco já existente
    # essas tarefas são adicionadas ao final das tarefas semanais já planejadas
    if tarefas_futuras:
        nova_linha.append("")
        nova_linha.append("")
        for data, info in tarefas_futuras.items():
            nova_linha.append(f"### {info['header']}")
            for tarefa in info["tarefas"]:
                nova_linha.append(tarefa)
    return nova_linha

def main(inbox_dir, pending_tasks_path, future_tasks_path, weekly_note_path):
    weekly_note_path = Path(weekly_note_path)
    original_md = weekly_note_path.read_text(encoding="utf-8").splitlines()
    tarefas_pendentes = parse_tarefas_pendentes(Path(pending_tasks_path))
    tarefas_futuras = parse_tarefas_futuras(Path(future_tasks_path))
    novo_md = inserir_tarefas_no_markdown(original_md, tarefas_pendentes, tarefas_futuras)
    weekly_note_path.write_text("\n".join(novo_md), encoding="utf-8")
    #print(f"Tarefas pendentes e futuras adicionadas a {weekly_note_path}")
