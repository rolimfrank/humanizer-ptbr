#!/usr/bin/env python3
"""Extrair o núcleo do SKILL.md sem manter duas fontes de regras."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START = "<!-- runtime:start -->"
END = "<!-- runtime:end -->"


def render(source: str) -> str:
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError("Usar exatamente um par de marcadores do runtime")
    start, end = source.index(START) + len(START), source.index(END)
    if end <= start or not source[start:end].strip():
        raise ValueError("O núcleo conversacional está vazio ou invertido")
    return source[start:end].strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = ROOT / "runtime/humanizer-ptbr.txt"
    result = render((ROOT / "SKILL.md").read_text(encoding="utf-8"))
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != result:
            raise SystemExit("Runtime desatualizado: execute python3 scripts/build-runtime.py")
        print("Runtime corresponde ao núcleo da skill")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result, encoding="utf-8")
        print(f"Runtime gerado: {len(result)} caracteres; tokens dependem do modelo")


if __name__ == "__main__":
    main()
