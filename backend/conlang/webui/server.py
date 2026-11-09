"""
Interface web do Arconte (servidor local).

Serve a página index.html e executa os motores em Python do projeto:
orquestrador (todas as etapas), palavras do usuário, mudanças sonoras,
tradutor, evolução (filhas, leis à mão, empréstimos) e famílias.

Uso, a partir da pasta conlang/:
    python webui/server.py              # abre em http://localhost:8000
    python webui/server.py --port 8080

Só biblioteca padrão (Python ≥ 3.9). Escuta apenas em 127.0.0.1 (este computador).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LANGS = ROOT / "languages"
WORK = LANGS / ".webui"          # arquivos temporários (palavras do usuário, frases)
PY = sys.executable
SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")
LOCK = threading.Lock()          # um motor por vez: os módulos escrevem nas mesmas pastas

for folder in ("translator", "phonotactics", "morphological_engine", "syntax", "orthography", "stress",
               "comparison", "derivation"):
    sys.path.insert(0, str(ROOT / folder))


# ═══════════════════════════════════════════════════════════════════════════
# Execução dos motores
# ═══════════════════════════════════════════════════════════════════════════

def run(cmd: List[str], timeout: int = 1800) -> Dict:
    """Roda um script do projeto e devolve a saída do terminal."""
    with LOCK:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    log = (p.stdout or "") + (("\n" + p.stderr) if p.stderr.strip() else "")
    return {"ok": p.returncode == 0, "log": log.strip(), "returncode": p.returncode}


def safe_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    if not SAFE.match(name):
        raise ValueError(f"nome inválido: {name!r} (use letras, números, ponto, hífen ou _)")
    return name


def write_custom(custom: Dict) -> Optional[Path]:
    """Monta o minha_lingua.txt a partir do formulário (fonemas e palavras)."""
    lines: List[str] = []
    ph = custom.get("phonemes") or {}
    if any((ph.get(k) or "").strip() for k in ("consonants", "vowels", "tones")):
        lines.append("[fonemas]")
        for key, label in (("consonants", "consoantes"), ("vowels", "vogais"), ("tones", "tons")):
            if (ph.get(key) or "").strip():
                lines.append(f"{label}: {ph[key].strip()}")
        lines.append("")
    sections = {"noun": "substantivos", "verb": "verbos", "adjective": "adjetivos", "other": "outras"}
    for pos, title in sections.items():
        words = [w for w in custom.get("words", []) if w.get("pos") == pos and w.get("form") and w.get("meaning")]
        if words:
            lines.append(f"[{title}]")
            for w in words:
                extra = (w.get("extra") or "").strip()
                lines.append(f"{w['form'].strip()} | {w['meaning'].strip()}" + (f" | {extra}" if extra else ""))
            lines.append("")
    if not lines:
        return None
    WORK.mkdir(parents=True, exist_ok=True)
    path = WORK / "minha_lingua.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_sentences(sentences: List[str]) -> Optional[Path]:
    sents = [s.strip() for s in sentences if s and s.strip()]
    if not sents:
        return None
    WORK.mkdir(parents=True, exist_ok=True)
    path = WORK / "frases.txt"
    path.write_text("\n".join(sents), encoding="utf-8")
    return path


FLAG_VALUES = ["seed", "synthesis", "fusion", "affix_position", "locus", "inventory_mode", "consonants",
               "vowels", "complexity", "list", "order", "style", "stress_rule", "number_base", "numbers_upto",
               "people", "places", "derive_per_process", "custom_policy", "family"]
FLAG_BOOLS = ["include_modern", "derive_all", "no_natural_changes", "reflect_spelling", "no_wals",
              "no_evolve_grammar"]


def generate(opts: Dict) -> Dict:
    """Língua completa pelo orquestrador (com palavras do usuário, tradução, filhas e família)."""
    cmd = [PY, "generate_language/generate_language.py"]
    name = safe_name(opts.get("name"))
    if name:
        cmd += ["--name", name]
    for key in FLAG_VALUES:
        v = opts.get(key)
        if v not in (None, "", "random"):
            cmd += ["--" + key.replace("_", "-"), str(v)]
    for key in FLAG_BOOLS:
        if opts.get(key):
            cmd.append("--" + key.replace("_", "-"))
    if opts.get("tones") == "yes":
        cmd.append("--tones")
    elif opts.get("tones") == "no":
        cmd.append("--no-tones")
    for rule in opts.get("sound_change") or []:
        if rule.strip():
            cmd += ["--sound-change", rule.strip()]
    for spec in opts.get("evolve") or []:
        if spec.get("profile"):
            cmd += ["--evolve", f"{spec['profile']}:{int(spec.get('years') or 1000)}"]
    custom = write_custom(opts.get("custom") or {})
    if custom:
        cmd += ["--custom", str(custom)]
    sentences = write_sentences(opts.get("sentences") or [])
    if sentences:
        cmd += ["--translate", str(sentences)]
    r = run(cmd)
    m = re.search(r"Gerando '([^']+)'", r["log"])
    r["name"] = m.group(1) if m else name
    r["command"] = " ".join(c if " " not in c else f'"{c}"' for c in cmd[1:])
    return r


def evolve(opts: Dict) -> Dict:
    """Filha com leis à mão, empréstimos ou perfil (evolution.py + grammar_evolution.py)."""
    parent = safe_name(opts.get("language"))
    if not parent or not (LANGS / parent).is_dir():
        raise ValueError("escolha a língua-mãe")
    cmd = [PY, "evolution/evolution.py", "--language", f"languages/{parent}", "--rebuild"]
    if opts.get("laws"):
        cmd += ["--laws", ",".join(opts["laws"])]
    else:
        cmd += ["--profile", opts.get("profile") or "natural", "--years", str(int(opts.get("years") or 1000))]
    name = safe_name(opts.get("name"))
    if name:
        cmd += ["--name", name]
    donor = safe_name(opts.get("donor"))
    if donor:
        cmd += ["--donor", f"languages/{donor}", "--borrowing", opts.get("borrowing") or "medium"]
    if opts.get("no_lexical"):
        cmd.append("--no-lexical")
    r = run(cmd)
    m = re.search(r"→ (\S+) \(", r["log"])
    daughter = m.group(1) if m else name
    r["name"] = daughter
    if r["ok"] and opts.get("grammar", True) and daughter:
        g = run([PY, "evolution/grammar_evolution.py", "--language", f"languages/{daughter}", "--rebuild"])
        r["log"] += "\n\n" + g["log"]
        r["ok"] = g["ok"]
    return r


def family(opts: Dict) -> Dict:
    parent = safe_name(opts.get("language"))
    if not parent or not (LANGS / parent).is_dir():
        raise ValueError("escolha a protolíngua")
    cmd = [PY, "evolution/family.py", "--language", f"languages/{parent}",
           "--branches", str(int(opts.get("branches") or 3)), "--sub-branches", str(int(opts.get("sub_branches") or 2)),
           "--depth", str(int(opts.get("depth") or 2)), "--years", str(int(opts.get("years") or 1500))]
    if opts.get("profiles"):
        cmd += ["--profiles", ",".join(opts["profiles"])]
    if opts.get("no_grammar"):
        cmd.append("--no-grammar")
    if opts.get("rebuild"):
        cmd.append("--rebuild")
    r = run(cmd)
    r["name"] = f"{parent}-familia"
    return r


def translate(opts: Dict) -> Dict:
    name = safe_name(opts.get("language"))
    if not name or not (LANGS / name).is_dir():
        raise ValueError("escolha a língua")
    import translator as tr  # noqa: E402
    import syntax as syn_mod  # noqa: E402
    with LOCK:
        t = tr.Translator(LANGS / name)
        out = []
        for s in opts.get("sentences") or []:
            for x in re.split(r"(?<=[.!?])\s+", s.strip()):
                if x.strip():
                    r = t.translate(x.strip())
                    out.append({"english": r["english"], "written": r["written"], "ipa": r["ipa"],
                                "interlinear": syn_mod.interlinear(r), "unknown": r["unknown"], "notes": r["notes"]})
    return {"ok": True, "results": out}


# ═══════════════════════════════════════════════════════════════════════════
# Leitura das línguas
# ═══════════════════════════════════════════════════════════════════════════

def load_json(path: Path) -> Optional[Dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def languages() -> List[Dict]:
    out = []
    if not LANGS.exists():
        return out
    for d in LANGS.iterdir():
        if not d.is_dir() or d.name.startswith("."):
            continue
        is_family = (d / "family.md").exists()
        if not is_family and not (d / "lexicon.json").exists():
            continue
        orth = load_json(d / "orthography.json") or {}
        evo = load_json(d / "evolution.json") or {}
        man = load_json(d / "manifest.json") or {}
        out.append({"name": d.name, "family": is_family, "grammar": (d / "grammar.md").exists(),
                    "title": (orth.get("language_name") or {}).get("english"),
                    "evolved_from": evo.get("parent"), "profile": evo.get("profile_name"),
                    "years": evo.get("years"), "seed": man.get("seed"),
                    "mtime": max((f.stat().st_mtime for f in d.iterdir() if f.is_file()), default=0)})
    return sorted(out, key=lambda x: -x["mtime"])


def language(name: str) -> Dict:
    d = LANGS / safe_name(name)
    if not d.is_dir():
        raise ValueError("língua não encontrada")
    docs = {}
    for f in ("grammar.md", "evolution.md", "family.md", "translations.md"):
        if (d / f).exists():
            docs[f] = (d / f).read_text(encoding="utf-8")
    files = sorted(f.name for f in d.iterdir() if f.is_file())
    return {"name": d.name, "docs": docs, "files": files}


# ═══════════════════════════════════════════════════════════════════════════
# HTTP
# ═══════════════════════════════════════════════════════════════════════════

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # terminal limpo: só os erros
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(fmt, *args)

    def send(self, body: bytes, ctype: str, status: int = 200, extra: Optional[Dict] = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def json(self, data, status: int = 200) -> None:
        self.send(json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", status)

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if u.path in ("/", "/index.html"):
                self.send((HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
            elif u.path == "/api/languages":
                self.json(languages())
            elif u.path == "/api/language":
                self.json(language(q.get("name", "")))
            elif u.path == "/api/file":
                d = LANGS / safe_name(q.get("name", ""))
                f = (d / q.get("file", "")).resolve()
                if f.parent != d.resolve() or not f.is_file():
                    raise ValueError("arquivo não encontrado")
                ctype = "application/json" if f.suffix == ".json" else "text/plain; charset=utf-8"
                self.send(f.read_bytes(), ctype, extra={"Content-Disposition": f'attachment; filename="{f.name}"'})
            else:
                self.json({"ok": False, "error": "não encontrado"}, 404)
        except (ValueError, TypeError) as ex:
            self.json({"ok": False, "error": str(ex)}, 400)

    def do_POST(self):
        u = urlparse(self.path)
        try:
            n = int(self.headers.get("Content-Length") or 0)
            opts = json.loads(self.rfile.read(n) or b"{}")
            routes = {"/api/generate": generate, "/api/evolve": evolve, "/api/family": family,
                      "/api/translate": translate}
            if u.path not in routes:
                return self.json({"ok": False, "error": "não encontrado"}, 404)
            self.json(routes[u.path](opts))
        except ValueError as ex:
            self.json({"ok": False, "error": str(ex), "log": ""}, 400)
        except subprocess.TimeoutExpired:
            self.json({"ok": False, "error": "o motor demorou demais (mais de 30 minutos)", "log": ""}, 504)
        except Exception as ex:  # noqa: BLE001
            self.json({"ok": False, "error": f"{type(ex).__name__}: {ex}", "log": ""}, 500)


def main() -> None:
    ap = argparse.ArgumentParser(description="Interface web do Arconte")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-browser", action="store_true", help="não abre o navegador")
    args = ap.parse_args()
    LANGS.mkdir(exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://localhost:{args.port}"
    print(f"Arconte rodando em {url}  (Ctrl+C para parar)")
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")


if __name__ == "__main__":
    main()
