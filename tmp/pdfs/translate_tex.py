#!/usr/bin/env python3
"""Translate visible LaTeX prose while preserving commands, math, and references."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import torch
from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexMathNode,
    LatexWalker,
)
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


SKIP_MACROS = {
    "affilnum", "bibliography", "bibliographystyle", "cite", "citealp",
    "captionsetup", "citeauthor", "citep", "citet", "citeyearpar", "documentclass", "email",
    "href", "includegraphics", "label", "pageref", "ref", "resizebox",
    "url", "usepackage", "vref",
}
SKIP_ENVS = {
    "align", "align*", "equation", "equation*", "gather", "gather*",
    "multline", "multline*", "tikzpicture",
}


def expand_inputs(text: str, root: Path) -> str:
    pat = re.compile(r"\\input\{([^}]+)\}")

    def repl(match: re.Match[str]) -> str:
        rel = match.group(1)
        path = root / (rel if rel.endswith(".tex") else rel + ".tex")
        if not path.exists():
            return match.group(0)
        return expand_inputs(path.read_text(encoding="utf-8"), root)

    return pat.sub(repl, text)


def split_piece(text: str, tokenizer, max_tokens: int = 80) -> list[str]:
    if not text.strip():
        return [text]
    if len(tokenizer(text, add_special_tokens=False).input_ids) <= max_tokens:
        return [text]
    units = re.split(r"(?<=[.!?;:])\s+|(?<=,)\s+", text)
    out: list[str] = []
    cur = ""
    for unit in units:
        trial = (cur + " " + unit).strip() if cur else unit
        if cur and len(tokenizer(trial, add_special_tokens=False).input_ids) > max_tokens:
            out.append(cur)
            cur = unit
        else:
            cur = trial
    if cur:
        out.append(cur)
    final: list[str] = []
    for unit in out:
        if len(tokenizer(unit, add_special_tokens=False).input_ids) <= max_tokens:
            final.append(unit)
        else:
            # Last-resort word split for very long table cells or captions.
            words = unit.split()
            cur = ""
            for word in words:
                trial = (cur + " " + word).strip()
                if cur and len(tokenizer(trial, add_special_tokens=False).input_ids) > max_tokens:
                    final.append(cur)
                    cur = word
                else:
                    cur = trial
            if cur:
                final.append(cur)
    return final


def collect_chars(node, source: str, spans: list[tuple[int, int, str]], skip=False):
    if isinstance(node, (LatexCommentNode, LatexMathNode)):
        return
    if isinstance(node, LatexCharsNode):
        raw = source[node.pos:node.pos + node.len]
        if not skip and re.search(r"[A-Za-z]{2,}", raw):
            # Preserve table delimiters and paragraph boundaries as independent units.
            offset = node.pos
            for part in re.split(r"(&|\n\s*\n)", raw):
                if re.search(r"[A-Za-z]{2,}", part):
                    spans.append((offset, offset + len(part), part))
                offset += len(part)
        return
    if isinstance(node, LatexMacroNode):
        if node.macroname in SKIP_MACROS:
            return
        if node.nodeargd:
            for arg in node.nodeargd.argnlist:
                if arg is not None:
                    collect_chars(arg, source, spans, skip)
        return
    if isinstance(node, LatexEnvironmentNode):
        if node.environmentname in SKIP_ENVS:
            return
        for child in node.nodelist or []:
            collect_chars(child, source, spans, skip)
        return
    if isinstance(node, LatexGroupNode):
        for child in node.nodelist or []:
            collect_chars(child, source, spans, skip)
        return
    if isinstance(node, list):
        for child in node:
            collect_chars(child, source, spans, skip)


def preserve_ws(original: str, translated: str) -> str:
    lead = re.match(r"^\s*", original).group(0)
    trail = re.search(r"\s*$", original).group(0)
    body = translated.strip()
    return lead + body + trail


def polish(text: str) -> str:
    replacements = {
        "任何点轨迹": "任意点轨迹",
        "任意点轨迹模型化": "任意点轨迹建模",
        "任意点轨迹模型": "任意点轨迹模型",
        "视觉-运动": "视觉运动",
        "视觉运动政策": "视觉运动策略",
        "政策学习": "策略学习",
        "政策模型": "策略模型",
        "政策": "策略",
        "行动标签": "动作标签",
        "无行动": "无动作标签",
        "机器人操纵": "机器人操作",
        "操纵任务": "操作任务",
        "人-机器人": "人类-机器人",
        "人类-机械人": "人类-机器人",
        "机械人": "机器人",
        "体现差距": "具身差距",
        "化身差距": "具身差距",
        "体现": "具身",
        "可负担性": "可供性",
        "提供示范": "示范",
        "加强学习": "强化学习",
        "模仿培训": "模仿学习",
        "跟踪变压器": "轨迹 Transformer",
        "轨道变压器": "轨迹 Transformer",
        "轨道指导": "轨迹引导",
        "跟踪指导": "轨迹引导",
        "点跟踪": "点轨迹",
        "视频预培训": "视频预训练",
        "预先培训": "预训练",
        "下游政策": "下游策略",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace("。.", "。").replace("，,", "，")
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--expand-inputs", action="store_true")
    ap.add_argument("--batch-size", type=int, default=12)
    ap.add_argument("--cpu", action="store_true")
    args = ap.parse_args()

    source = args.input.read_text(encoding="utf-8")
    if args.expand_inputs:
        source = expand_inputs(source, args.input.parent)

    # Inline typography often splits one sentence into tiny parser nodes (for
    # example, ``\textbf{A}ny-point``).  Removing these wrappers gives the
    # translation model full sentence context; section hierarchy, math,
    # citations, tables, and figure environments remain intact.
    inline = re.compile(r"\\(?:textbf|textit|emph|underline)\{([^{}]*)\}")
    while inline.search(source):
        source = inline.sub(r"\1", source)
    source = source.replace("\\noindent", "")

    walker = LatexWalker(source)
    nodes, _, _ = walker.get_latex_nodes(pos=0)
    spans: list[tuple[int, int, str]] = []
    collect_chars(nodes, source, spans)
    spans = sorted(set(spans))

    tokenizer = AutoTokenizer.from_pretrained(str(args.model), src_lang="eng_Latn")
    use_cuda = torch.cuda.is_available() and not args.cpu
    model = AutoModelForSeq2SeqLM.from_pretrained(
        str(args.model), dtype=torch.float16 if use_cuda else torch.float32
    )
    device = torch.device("cuda" if use_cuda else "cpu")
    model.to(device).eval()
    bos = tokenizer.convert_tokens_to_ids("zho_Hans")

    cache = json.loads(args.cache.read_text(encoding="utf-8")) if args.cache.exists() else {}
    pieces: list[str] = []
    owners: list[tuple[int, int]] = []
    for idx, (_, _, raw) in enumerate(spans):
        # Do not feed raw TeX control characters to the model.
        for sub in re.split(r"([{}%#_^~])", raw):
            if re.search(r"[A-Za-z]{2,}", sub):
                for chunk in split_piece(sub, tokenizer):
                    if re.search(r"[A-Za-z]{2,}", chunk):
                        owners.append((idx, len(pieces)))
                        pieces.append(chunk)

    missing = [p for p in pieces if p not in cache]
    # Stable de-duplication saves time on repeated headings and table labels.
    missing = list(dict.fromkeys(missing))
    for start in range(0, len(missing), args.batch_size):
        batch = missing[start:start + args.batch_size]
        print("batch:", repr(batch[0][:220]), flush=True)
        enc = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
        enc = {k: v.to(device) for k, v in enc.items()}
        with torch.inference_mode():
            out = model.generate(
                **enc, forced_bos_token_id=bos, max_new_tokens=140,
                num_beams=1,
            )
        translated = tokenizer.batch_decode(out, skip_special_tokens=True)
        for en, zh in zip(batch, translated):
            cache[en] = polish(zh)
        args.cache.parent.mkdir(parents=True, exist_ok=True)
        args.cache.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"translated {min(start + len(batch), len(missing))}/{len(missing)}", flush=True)

    translated_spans: dict[int, str] = {}
    for idx, (_, _, raw) in enumerate(spans):
        out_parts: list[str] = []
        for sub in re.split(r"([{}%#_^~])", raw):
            if re.search(r"[A-Za-z]{2,}", sub):
                chunks = split_piece(sub, tokenizer)
                vals = [cache.get(c, c) if re.search(r"[A-Za-z]{2,}", c) else c for c in chunks]
                joined = "".join(vals) if "\n" in sub else " ".join(v.strip() for v in vals)
                out_parts.append(preserve_ws(sub, joined))
            else:
                out_parts.append(sub)
        translated_spans[idx] = polish("".join(out_parts))

    result = source
    for idx in range(len(spans) - 1, -1, -1):
        start, end, _ = spans[idx]
        result = result[:start] + translated_spans[idx] + result[end:]

    # Add Chinese font support while keeping each source's original layout.
    insert = "\\usepackage{xeCJK}\n\\setCJKmainfont{Noto Serif CJK SC}\n"
    pos = result.find("\\begin{document}")
    result = result[:pos] + insert + result[pos:]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")


if __name__ == "__main__":
    main()
