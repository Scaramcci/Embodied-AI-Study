#!/usr/bin/env python3
"""Translate visible LaTeX prose through Google while preserving TeX structure."""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator
from pylatexenc.latexwalker import (
    LatexCharsNode, LatexCommentNode, LatexEnvironmentNode, LatexGroupNode,
    LatexMacroNode, LatexMathNode, LatexWalker,
)

from translate_tex import SKIP_ENVS, SKIP_MACROS, collect_chars, expand_inputs, polish, preserve_ws


def split_long(text: str, limit: int = 3800) -> list[str]:
    if len(text) <= limit:
        return [text]
    units = re.split(r"(?<=[.!?;:])\s+|(?<=,)\s+", text)
    out, cur = [], ""
    for unit in units:
        trial = (cur + " " + unit).strip() if cur else unit
        if cur and len(trial) > limit:
            out.append(cur)
            cur = unit
        else:
            cur = trial
    if cur:
        out.append(cur)
    final = []
    for unit in out:
        if len(unit) <= limit:
            final.append(unit)
        else:
            final.extend(unit[i:i + limit] for i in range(0, len(unit), limit))
    return final


def translate_with_retry(translator: GoogleTranslator, text: str) -> str:
    for attempt in range(7):
        try:
            return translator.translate(text)
        except Exception as exc:
            if "No translation was found" in str(exc) and len(text.split()) <= 4:
                return text
            if attempt == 6:
                return text
            print(f"retry {attempt + 1}: {exc}", flush=True)
            time.sleep(2 + attempt * 2)
    raise RuntimeError("unreachable")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--expand-inputs", action="store_true")
    args = ap.parse_args()

    source = args.input.read_text(encoding="utf-8")
    if args.expand_inputs:
        source = expand_inputs(source, args.input.parent)
    inline = re.compile(r"\\(?:textbf|textit|emph|underline)\{([^{}]*)\}")
    while inline.search(source):
        source = inline.sub(r"\1", source)
    source = source.replace("\\noindent", "")

    nodes, _, _ = LatexWalker(source).get_latex_nodes(pos=0)
    spans: list[tuple[int, int, str]] = []
    collect_chars(nodes, source, spans)
    body_pos = source.find("\\begin{document}")
    spans = sorted(x for x in set(spans) if x[0] > body_pos)

    cache = json.loads(args.cache.read_text(encoding="utf-8")) if args.cache.exists() else {}
    # Retry transient cases where the service returned the English source
    # unchanged; keep short proper names and acronyms untouched.
    cache = {
        k: v for k, v in cache.items()
        if not (k == v and len(k.split()) > 4)
    }
    units: list[str] = []
    for _, _, raw in spans:
        for sub in re.split(r"([{}%#_^~])", raw):
            if re.search(r"[A-Za-z]{2,}", sub):
                units.extend(x for x in split_long(sub) if re.search(r"[A-Za-z]{2,}", x))
    missing = [x for x in dict.fromkeys(units) if x not in cache]

    translator = GoogleTranslator(source="en", target="zh-CN")
    for idx, unit in enumerate(missing, 1):
        cache[unit] = polish(translate_with_retry(translator, unit))
        if idx % 10 == 0 or idx == len(missing):
            args.cache.parent.mkdir(parents=True, exist_ok=True)
            args.cache.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"translated {idx}/{len(missing)}", flush=True)

    translated_spans: dict[int, str] = {}
    for idx, (_, _, raw) in enumerate(spans):
        out_parts = []
        for sub in re.split(r"([{}%#_^~])", raw):
            if re.search(r"[A-Za-z]{2,}", sub):
                vals = [cache.get(x, x) for x in split_long(sub)]
                joined = " ".join(v.strip() for v in vals)
                out_parts.append(preserve_ws(sub, joined))
            else:
                out_parts.append(sub)
        translated_spans[idx] = polish("".join(out_parts))

    result = source
    for idx in range(len(spans) - 1, -1, -1):
        start, end, _ = spans[idx]
        result = result[:start] + translated_spans[idx] + result[end:]

    cjk = "\\usepackage{xeCJK}\n\\setCJKmainfont{Noto Serif CJK SC}\n"
    pos = result.find("\\begin{document}")
    result = result[:pos] + cjk + result[pos:]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")


if __name__ == "__main__":
    main()
