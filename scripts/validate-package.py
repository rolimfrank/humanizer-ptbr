#!/usr/bin/env python3
"""Validar identidade, referências, runtime e casos sem dependências externas."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from evaluate import read_jsonl, validate_cases

ROOT = Path(__file__).resolve().parent.parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(root: Path = ROOT) -> dict:
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")
    plugin = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    upstream = json.loads((root / "upstream.json").read_text(encoding="utf-8"))
    header = re.match(r"\A---\n(.*?)\n---\n", skill, re.S)
    require(header is not None, "SKILL.md precisa começar com metadados YAML")
    metadata = header.group(1)
    require(re.search(r"(?m)^name: humanizer-ptbr$", metadata) is not None, "Nome incorreto da skill")
    require(re.search(r"(?m)^description: [>|]", metadata) is not None, "Descrição multilinha ausente")
    version = re.findall(r'(?m)^  version: "(\d+\.\d+\.\d+)"$', metadata)
    require(len(version) == 1, "Declarar uma metadata.version com três números")
    require(not re.search(r"(?m)^version:", metadata), "Não usar version no nível superior")
    first_version = re.search(r"(?m)^- \*\*(\d+\.\d+\.\d+)\*\*", readme)
    require(first_version is not None, "Histórico da versão ausente no README")
    require({version[0], plugin.get("version"), upstream.get("fork_version"), first_version.group(1)} == {version[0]},
            "Versões do pacote divergentes")
    require({p.relative_to(root).as_posix() for p in root.rglob("SKILL.md")} == {"SKILL.md"}
            and not (root / "SKILL.md").is_symlink(), "Manter um único SKILL.md regular na raiz")
    require(len(skill.splitlines()) <= 400, "SKILL.md deve ter no máximo 400 linhas")
    require(plugin.get("name") == marketplace.get("name") == "humanizer-ptbr", "Identidade dos manifests divergente")
    require(plugin.get("skills") == ["./"], "Loader deve usar a raiz")
    entries = marketplace.get("plugins", [])
    require(len(entries) == 1 and entries[0].get("name") == "humanizer-ptbr" and entries[0].get("source") == "./",
            "Entrada inválida no marketplace")
    require(plugin.get("repository") == "https://github.com/frankrolim/humanizer-ptbr", "Repository deve apontar ao fork")
    require(re.fullmatch(r"[0-9a-f]{40}", upstream.get("reviewed_commit", "")) is not None, "Commit upstream inválido")
    require(upstream.get("development_branch") == "dexter-ptbr" and upstream.get("tracking_branch") == "main",
            "Branches de desenvolvimento e upstream inválidas")
    ui = (root / "agents/openai.yaml").read_text(encoding="utf-8")
    require("$humanizer-ptbr" in ui, "Invocação OpenAI incorreta")
    short = re.search(r'(?m)^  short_description: "(.+)"$', ui)
    require(short is not None and 25 <= len(short.group(1)) <= 64, "Descrição curta deve ter 25–64 caracteres")
    rules = (root / "references/pt-br.md").read_text(encoding="utf-8")
    require([int(x) for x in re.findall(r"(?m)^### (\d+)\. ", rules)] == list(range(1,26)),
            "Manter mapeamento dos 25 critérios do upstream")
    for document in [root / "SKILL.md", root / "README.md", *sorted((root / "references").glob("*.md"))]:
        for link in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = (document.parent / link.split("#")[0]).resolve()
            require(target.is_relative_to(root.resolve()) and target.is_file(), f"Referência local inválida: {link}")
    cases = validate_cases(read_jsonl(root / "evals/cases.jsonl"))
    require(len(cases) >= 60, "Manter pelo menos 60 casos de avaliação")
    require("Copyright (c) 2025 Siqi Chen" in (root / "LICENSE").read_text(), "Preservar atribuição original")
    return {"version": version[0], "cases": len(cases), "patterns": 25}


def main() -> None:
    try:
        result = validate()
        subprocess.run([sys.executable, str(ROOT / "scripts/build-runtime.py"), "--check"], check=True)
        print(json.dumps(result, ensure_ascii=False))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Pacote inválido: {error}") from error


if __name__ == "__main__":
    main()
