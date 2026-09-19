#!/usr/bin/env python3
"""Preparar casos e conferir respostas offline; não chamar modelos nem julgar estilo."""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILES = ("baseline", "original", "compact", "full")


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except ValueError as error:
            raise ValueError(f"{path.name}:{number}: JSON inválido") from error
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{number}: esperado um objeto")
        rows.append(value)
    return rows


def validate_cases(rows: list[dict]) -> dict[str, dict]:
    cases = {}
    for row in rows:
        case_id = row.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in cases:
            raise ValueError(f"ID ausente ou repetido: {case_id}")
        if row.get("operation") not in ("rewrite", "generate"):
            raise ValueError(f"{case_id}: operação inválida")
        for key in ("category", "instruction"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"{case_id}: {key} obrigatório")
        if not isinstance(row.get("context"), dict):
            raise ValueError(f"{case_id}: contexto obrigatório")
        for key in ("criteria", "protected"):
            if not isinstance(row.get(key), list) or any(not isinstance(x, str) or not x for x in row[key]):
                raise ValueError(f"{case_id}: {key} deve conter textos não vazios")
        if not row["criteria"]:
            raise ValueError(f"{case_id}: definir critérios sem impor uma redação única")
        if row["operation"] == "rewrite" and not isinstance(row.get("draft"), str):
            raise ValueError(f"{case_id}: rascunho obrigatório")
        if "unchanged" in row and not isinstance(row["unchanged"], bool):
            raise ValueError(f"{case_id}: unchanged deve ser booleano")
        if row.get("unchanged") and row["operation"] != "rewrite":
            raise ValueError(f"{case_id}: unchanged exige revisão")
        data = json.dumps({k: row[k] for k in ("context", "draft") if k in row}, ensure_ascii=False)
        if any(token not in data for token in row["protected"]):
            raise ValueError(f"{case_id}: trecho protegido ausente da entrada")
        cases[case_id] = row
    if not cases:
        raise ValueError("Nenhum caso encontrado")
    return cases


def profile_text(profile: str, upstream_file: Path | None = None) -> str:
    if profile == "baseline":
        return ""
    if profile == "original":
        if upstream_file is None:
            raise ValueError("Original exige --upstream-file com a versão fixada em upstream.json")
        return upstream_file.read_text(encoding="utf-8")
    if profile == "compact":
        return (ROOT / "runtime/humanizer-ptbr.txt").read_text(encoding="utf-8")
    if profile != "full":
        raise ValueError("Perfil desconhecido")
    source = (ROOT / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[2]
    return source + "\n" + "\n".join((ROOT / path).read_text(encoding="utf-8") for path in
                                      ("references/pt-br.md", "references/conversas.md"))


def prepare(case: dict, profile: str, text: str) -> dict:
    # Critérios e expectativas ficam fora da entrada do modelo.
    payload = {key: case[key] for key in ("operation", "context", "draft") if key in case}
    system = "Cumpra a tarefa em português brasileiro. Retorne somente o resultado solicitado.\n" + text
    system += "\nTarefa e configuração desta execução:\n" + case["instruction"]
    return {"case_id": case["id"], "variant": profile,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]}


def check_response(case: dict, output: str) -> list[str]:
    errors = [f"Trecho protegido ausente: {token}" for token in case["protected"] if token not in output]
    if case.get("unchanged") and output != case["draft"]:
        errors.append("O texto que deveria permanecer intacto foi alterado")
    if not output.strip() and not case["context"].get("allow_empty", False):
        errors.append("Resposta vazia")
    return errors


def score(cases: dict, rows: list[dict], variants: list[str], allow_partial: bool = False) -> dict:
    if not variants or len(set(variants)) != len(variants) or any(v not in PROFILES for v in variants):
        raise ValueError("Selecionar perfis distintos e conhecidos")
    seen, details = set(), []
    metrics = {variant: {key: [] for key in ("input_tokens", "output_tokens", "latency_ms")}
               for variant in variants}
    for row in rows:
        key = (row.get("case_id"), row.get("variant"))
        if not all(isinstance(x, str) for x in key):
            raise ValueError("case_id e variant devem ser textos")
        case_id, variant = key
        if case_id not in cases or variant not in variants or key in seen:
            raise ValueError(f"Resposta desconhecida ou duplicada: {key}")
        if not isinstance(row.get("output"), str):
            raise ValueError(f"{key}: output deve ser texto")
        if not isinstance(row.get("model"), str) or not row["model"] or not isinstance(row.get("parameters"), dict):
            raise ValueError(f"{key}: registrar model e parameters")
        seen.add(key)
        for name, values in metrics[variant].items():
            value = row.get(name)
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"{key}: métrica inválida: {name}")
            if name.endswith("tokens") and not isinstance(value, int):
                raise ValueError(f"{key}: tokens devem ser inteiros")
            values.append(value)
        details.append({"case_id": case_id, "variant": variant,
                        "mechanical_errors": check_response(cases[case_id], row["output"])})
    missing = sorted(set((case_id, v) for case_id in cases for v in variants) - seen)
    if missing and not allow_partial:
        raise ValueError(f"Faltam {len(missing)} respostas; use --allow-partial somente para resultados parciais")
    return {"scope": "Verificações literais; não demonstram fidelidade semântica nem naturalidade",
            "complete": not missing, "missing": missing, "details": details,
            "metrics": {v: {k: {"measured": len(a), "mean": sum(a) / len(a) if a else None}
                            for k, a in m.items()} for v, m in metrics.items()}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=ROOT / "evals/cases.jsonl")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    prep = sub.add_parser("prepare")
    prep.add_argument("--profile", choices=PROFILES, required=True)
    prep.add_argument("--upstream-file", type=Path)
    prep.add_argument("--output", type=Path, required=True)
    check = sub.add_parser("score")
    check.add_argument("--responses", type=Path, required=True)
    check.add_argument("--variants", nargs="+", choices=PROFILES, required=True)
    check.add_argument("--allow-partial", action="store_true")
    check.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        cases = validate_cases(read_jsonl(args.cases))
        if args.command == "validate":
            print(json.dumps({"cases": len(cases), "categories": Counter(c["category"] for c in cases.values())}, ensure_ascii=False))
        elif args.command == "prepare":
            text = profile_text(args.profile, args.upstream_file)
            args.output.write_text("".join(json.dumps(prepare(c, args.profile, text), ensure_ascii=False) + "\n"
                                          for c in cases.values()), encoding="utf-8")
            print(f"{len(cases)} entradas preparadas; nenhum modelo foi chamado")
        else:
            report = score(cases, read_jsonl(args.responses), args.variants, args.allow_partial)
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Relatório salvo; execução completa: {report['complete']}")
    except (OSError, ValueError) as error:
        parser.exit(2, f"Erro: {error}\n")


if __name__ == "__main__":
    main()
