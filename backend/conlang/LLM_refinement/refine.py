#!/usr/bin/env python3
"""Refinamento linguístico de grammar.md usando Ollama local.

Executar na pasta conlang/LLM_refinement:
    python refine.py teste31-natural-1000 --model qwen3.5:4b
    python refine.py teste31-natural-1000 --limit 2
    python refine.py teste31 --include-dictionary --apply-structural

Nunca modifica grammar.md; gera grammar_refined.md, refinement_report.md
and refinement_changes.json dentro da pasta da língua.

Este módulo edita a documentação Markdown, NÃO os JSONs do gerador.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent

SCHEMA = {
    "type": "object",
    "properties": {
        "resumo": {"type": "string"},
        "alteracoes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "original": {"type": "string"},
                    "novo": {"type": "string"},
                    "motivo": {"type": "string"},
                    "tipo": {"type": "string", "enum": ["editorial", "estrutural"]},
                },
                "required": ["original", "novo", "motivo", "tipo"],
            },
        },
        "pendencias": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["resumo", "alteracoes", "pendencias"],
}

SYSTEM = """Você é linguista especializado em tipologia, fonologia, morfologia,
sintaxe e evolução histórica de línguas naturais. Sua tarefa é REFINAR uma
língua construída, NÃO substituí-la por português, inglês ou um idioma comum.

Critérios:
- Preserve ordem básica, inventário fonêmico, léxico e identidade da língua.
- Distinga erros formais de irregularidades e fenômenos raros, mas naturais.
- NÃO invente supostas leis universais, fontes, estatísticas ou etimologias.
- Não force todas as propriedades a concordarem com uma tendência tipológica.
- Sugira naturalismo real: distribuição contextual, variação plausível,
  alomorfias e exceções justificadas; não acrescente enfeites arbitrários.
- Se uma alteração precisar de mudanças em outras seções, paradigmas, léxico
  ou nos JSONs de origem, classifique-a como 'estrutural' e explique a
  propagação necessária em 'pendencias'.
- Caso só exista documentação insuficiente, indique a dúvida em 'pendencias'
  em vez de criar uma regra como se fosse comprovada.
- Não altere fatos da gramática sem justificativa explícita no trecho.
- Responda em português e APENAS com JSON válido no esquema especificado.
"""


def fetch_json(url: str, payload: dict | None = None, timeout: int = 600) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        info = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama retornou HTTP {exc.code}: {info[:450]}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(
            "Não consegui acessar o Ollama. Inicie-o com 'ollama serve' "
            f"e confira o endereço {url}. Detalhes: {exc}"
        ) from exc


def verify_model(url: str, model: str) -> None:
    available = fetch_json(url + "/api/tags").get("models", [])
    names = [m.get("name", "") for m in available]
    if model not in names:
        raise RuntimeError(
            f"Modelo '{model}' não encontrado. Modelos locais: {', '.join(names) or '(nenhum)'}. "
            f"Baixe com: ollama pull {model}"
        )


def sections_of(text: str) -> tuple[str, list[tuple[str, str]]]:
    matches = list(re.finditer(r"(?m)^## [^\n]+$", text))
    if not matches:
        raise ValueError("Não encontrei títulos '##' em grammar.md")
    intro = text[:matches[0].start()]
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group().removeprefix("## ").strip(), text[match.start():end]))
    return intro, sections


def chunks_of(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]
    result, buf = [], ""
    # Quebra apenas entre linhas, sem destruir nenhuma entrada do dicionário.
    for line in text.splitlines(keepends=True):
        if buf and len(buf) + len(line) > limit:
            result.append(buf)
            buf = ""
        buf += line
    if buf:
        result.append(buf)
    return result


def context_from(sections: list[tuple[str, str]]) -> str:
    # Contexto compacto, pois uma língua evoluída pode ter > 100 KB de gramática.
    pieces = []
    sizes = {"Fonologia": 600, "Morfologia": 1300, "Sintaxe": 650,
             "Paradigmas": 650, "Irregularidades": 500}
    for name, content in sections:
        if name in sizes:
            pieces.append(content[:sizes[name]])
    return "\n\n".join(pieces)[:3500]


def evaluate_chunk(
    url: str, model: str, chunk: str, title: str, context: str, intensity: str,
    timeout: int, num_ctx: int, think: bool,
) -> dict:
    modes = {
        "conservador": "Corrija apenas problemas bem demonstrados; mantenha quase tudo.",
        "moderado": "Além de erros bem demonstrados, sugira pequenos refinamentos naturalistas seguros.",
        "profundo": "Proponha também mudanças linguísticas substanciais, mas marque como estruturais se afetarem outros dados.",
    }
    prompt = (
        f"Intensidade: {intensity}. {modes[intensity]}\n"
        f"Seção avaliada: {title}\n\n"
        f"CONTEXTO DE OUTRAS SEÇÕES (somente referência):\n{context}\n\n"
        f"TRECHO A REFINAR (somente aqui se pode propor substituições):\n{chunk}\n\n"
        "Retorne um objeto JSON com 'resumo', 'alteracoes' (0 a 3) e 'pendencias' (0 a 4). "
        "Cada alteração deve conter 'original' (trecho EXATO e contínuo da seção acima), "
        "'novo' (substituto em Markdown), 'motivo' e 'tipo' ('editorial' ou 'estrutural'). "
        "Não invente um 'original' aproximado. Evite substituir trechos grandes. "
        "Uma alteração editorial melhora explicação/uso sem mudar formas ou regras; "
        "uma estrutural muda formas, paradigmas ou regras do sistema. "
        "Se não houver correção segura, retorne alteracoes=[] e apresente observações em pendencias."
    )
    response = fetch_json(url + "/api/chat", {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": prompt}],
        "format": SCHEMA,
        "stream": False,
        "think": think,
        "options": {"temperature": 0.15, "num_ctx": num_ctx, "num_predict": 1600},
    }, timeout=timeout)
    raw = response.get("message", {}).get("content", "")
    if not raw.strip():
        raise RuntimeError("O modelo devolveu uma resposta vazia.")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Resposta do modelo não é JSON válido: {raw[:300]}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("alteracoes"), list):
        raise RuntimeError(f"Estrutura de resposta inesperada: {raw[:300]}")
    return data


def has_structural_markup(text: str) -> bool:
    # Precaução adicional: tabelas e exemplos linguísticos não podem ser
    # alterados inadvertidamente no modo seguro.
    return any(line.lstrip().startswith(("|", "```", "- **")) for line in text.splitlines())


def apply_edits(text: str, data: dict, allow_structural: bool) -> tuple[str, list[dict]]:
    logs = []
    for item in data.get("alteracoes", [])[:3]:
        if not isinstance(item, dict):
            continue
        original = item.get("original", "")
        new = item.get("novo", "")
        kind = item.get("tipo", "estrutural")
        item_log = {"original": original, "novo": new, "motivo": item.get("motivo", ""),
                    "tipo": kind, "status": "pendente", "razao": ""}
        if not isinstance(original, str) or not isinstance(new, str) or not original or not new:
            item_log["razao"] = "Trecho inválido/vazio"
        elif original.startswith("## "):
            item_log["razao"] = "Título principal não pode ser alterado"
        elif len(new) > max(1400, 3 * len(original)):
            item_log["razao"] = "Substituição longa demais"
        elif text.count(original) != 1:
            item_log["razao"] = f"O trecho original aparece {text.count(original)} vezes, não uma"
        elif (kind != "editorial" or has_structural_markup(original)) and not allow_structural:
            item_log["razao"] = "Mudança estrutural requer --apply-structural"
        else:
            text = text.replace(original, new, 1)
            item_log["status"] = "aplicada"
        logs.append(item_log)
    return text, logs


def markdown_report(language: str, model: str, items: list[dict],
                    source: str, refined: str, intensity: str) -> str:
    applied = sum(x["status"] == "aplicada" for s in items for x in s["alteracoes"])
    pending = sum(x["status"] != "aplicada" for s in items for x in s["alteracoes"])
    lines = [f"# Relatório de refinamento: {language}", "",
             f"- Modelo: `{model}`", f"- Intensidade: `{intensity}`",
             f"- Alterações aplicadas: **{applied}**", f"- Alterações não aplicadas: **{pending}**", "",
             "> O refinamento é uma proposta de um modelo de linguagem: não comprova",
             "> correção tipológica. Apenas o Markdown foi editado; os JSONs originais",
             "> e as regras dos geradores NÃO foram modificados.", "",
             f"- SHA256 original: `{hashlib.sha256(source.encode('utf-8')).hexdigest()}`",
             f"- SHA256 refinado: `{hashlib.sha256(refined.encode('utf-8')).hexdigest()}`", ""]
    for sec in items:
        lines += [f"## {sec['secao']}", "", sec.get("resumo", ""), ""]
        for edit in sec["alteracoes"]:
            status = "Aplicada" if edit["status"] == "aplicada" else "Não aplicada"
            lines += [f"### {status} ({edit['tipo']})", "",
                      f"**Motivo:** {edit['motivo']}", ""]
            if edit["razao"]:
                lines += [f"**Razão de não aplicação:** {edit['razao']}", ""]
            lines += ["**Antes:**", "", "```text", edit["original"], "```", "",
                      "**Depois:**", "", "```text", edit["novo"], "```", ""]
        if sec["pendencias"]:
            lines += ["**Questões para revisão:**", ""]
            lines.extend(f"- {value}" for value in sec["pendencias"])
            lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Refina uma grammar.md com Ollama local sem sobrescrever o original")
    parser.add_argument("language", help="nome de uma pasta em LLM_refinement/ ou caminho para grammar.md")
    parser.add_argument("--model", default="qwen3.5:4b", help="modelo instalado no Ollama")
    parser.add_argument("--url", default="http://127.0.0.1:11434", help="endereço local do Ollama")
    parser.add_argument("--intensity", choices=["conservador", "moderado", "profundo"], default="moderado")
    parser.add_argument("--include-dictionary", action="store_true", help="inspeciona o dicionário inteiro (demorado)")
    parser.add_argument("--apply-structural", action="store_true", help="permite mudar formas/tabelas na CÓPIA Markdown")
    parser.add_argument("--limit", type=int, default=0, help="processa apenas N trechos (teste rápido)")
    parser.add_argument("--chunk-size", type=int, default=4200, help="máximo aproximado de caracteres por trecho")
    parser.add_argument("--num-ctx", type=int, default=8192, help="janela de contexto do modelo")
    parser.add_argument("--timeout", type=int, default=600, help="tempo limite em segundos por chamada")
    parser.add_argument("--think", action="store_true", help="habilita raciocínio, caso modelo suporte")
    args = parser.parse_args()

    path = Path(args.language).expanduser()
    if not path.exists():
        path = HERE / args.language
    if path.is_dir():
        path = path / "grammar.md"
    if not path.is_file():
        parser.error(f"gramática não encontrada: {path}")
    if args.chunk_size < 1000:
        parser.error("--chunk-size deve ser >= 1000")
    if args.limit < 0:
        parser.error("--limit deve ser >= 0")

    source = path.read_text(encoding="utf-8")
    intro, sections = sections_of(source)
    context = context_from(sections)
    url = args.url.rstrip("/")
    verify_model(url, args.model)

    tasks: list[tuple[int, int, str, str]] = []
    output_sections: list[list[str]] = []
    for index, (name, content) in enumerate(sections):
        if name.casefold() == "dicionário" and not args.include_dictionary:
            fragments = [content]
        else:
            fragments = chunks_of(content, args.chunk_size)
        output_sections.append(fragments[:])
        if name.casefold() != "dicionário" or args.include_dictionary:
            for subindex, fragment in enumerate(fragments):
                tasks.append((index, subindex, name, fragment))

    selected = tasks[:args.limit] if args.limit else tasks
    print(f"Língua: {path.parent.name} | modelo: {args.model} | trechos: {len(selected)}/{len(tasks)}", flush=True)
    if not args.include_dictionary:
        print("Dicionário preservado (use --include-dictionary para revisá-lo).", flush=True)
    records = []
    for order, (i, j, name, chunk) in enumerate(selected, start=1):
        label = name if len(output_sections[i]) == 1 else f"{name} [{j+1}/{len(output_sections[i])}]"
        print(f"[{order}/{len(selected)}] Analisando {label}...", flush=True)
        data = evaluate_chunk(url, args.model, chunk, label, context, args.intensity,
                              args.timeout, args.num_ctx, args.think)
        modified, logs = apply_edits(chunk, data, args.apply_structural)
        output_sections[i][j] = modified
        records.append({"secao": label, "resumo": str(data.get("resumo", "")),
                        "alteracoes": logs, "pendencias": [str(x) for x in data.get("pendencias", [])[:4]]})
        print(f"    {sum(x['status'] == 'aplicada' for x in logs)} aplicada(s), "
              f"{sum(x['status'] != 'aplicada' for x in logs)} pendente(s).", flush=True)

    refined = intro + "".join("".join(parts) for parts in output_sections)
    out = path.with_name("grammar_refined.md")
    report = path.with_name("refinement_report.md")
    log = path.with_name("refinement_changes.json")
    out.write_text(refined, encoding="utf-8")
    report.write_text(markdown_report(path.parent.name, args.model, records, source, refined, args.intensity), encoding="utf-8")
    log.write_text(json.dumps({"language": path.parent.name, "model": args.model,
                              "timestamp": datetime.now(timezone.utc).isoformat(),
                              "intensity": args.intensity, "allow_structural": args.apply_structural,
                              "processed": len(selected), "available": len(tasks), "results": records},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nConcluído!\n- {out}\n- {report}\n- {log}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, ValueError) as error:
        sys.exit(f"Erro: {error}")
