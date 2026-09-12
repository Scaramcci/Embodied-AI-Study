#!/usr/bin/env python3
"""Low-memory NLLB translation for visible LaTeX prose."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import ctranslate2
from pylatexenc.latexwalker import LatexWalker
from transformers import AutoTokenizer

from translate_tex import collect_chars, expand_inputs, polish, preserve_ws, split_piece


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--hf-model", type=Path, required=True)
    ap.add_argument("--ct2-model", type=Path, required=True)
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--expand-inputs", action="store_true")
    ap.add_argument("--batch-size", type=int, default=12)
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

    tokenizer = AutoTokenizer.from_pretrained(str(args.hf_model), src_lang="eng_Latn")
    translator = ctranslate2.Translator(
        str(args.ct2_model), device="cpu", compute_type="int8",
        inter_threads=2, intra_threads=8,
    )
    cache = json.loads(args.cache.read_text(encoding="utf-8")) if args.cache.exists() else {}

    units: list[str] = []
    for _, _, raw in spans:
        for sub in re.split(r"([{}%#_^~])", raw):
            if re.search(r"[A-Za-z]{2,}", sub):
                units.extend(x for x in split_piece(sub, tokenizer, max_tokens=180)
                             if re.search(r"[A-Za-z]{2,}", x))
    missing = [x for x in dict.fromkeys(units) if x not in cache]

    for start in range(0, len(missing), args.batch_size):
        batch = missing[start:start + args.batch_size]
        src_tokens = [tokenizer.convert_ids_to_tokens(tokenizer.encode(x)) for x in batch]
        results = translator.translate_batch(
            src_tokens,
            target_prefix=[["zho_Hans"] for _ in batch],
            beam_size=2,
            max_decoding_length=320,
        )
        for en, result in zip(batch, results):
            toks = result.hypotheses[0]
            if toks and toks[0] == "zho_Hans":
                toks = toks[1:]
            zh = tokenizer.decode(tokenizer.convert_tokens_to_ids(toks), skip_special_tokens=True)
            cache[en] = polish(zh)
        args.cache.parent.mkdir(parents=True, exist_ok=True)
        args.cache.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"translated {min(start + len(batch), len(missing))}/{len(missing)}", flush=True)

    translated_spans: dict[int, str] = {}
    for idx, (_, _, raw) in enumerate(spans):
        out_parts = []
        for sub in re.split(r"([{}%#_^~])", raw):
            if re.search(r"[A-Za-z]{2,}", sub):
                vals = [cache.get(x, x) for x in split_piece(sub, tokenizer, max_tokens=180)]
                joined = "".join(vals) if "\n" in sub else " ".join(v.strip() for v in vals)
                out_parts.append(preserve_ws(sub, joined))
            else:
                out_parts.append(sub)
        translated_spans[idx] = polish("".join(out_parts))

    result = source
    for idx in range(len(spans) - 1, -1, -1):
        start, end, _ = spans[idx]
        result = result[:start] + translated_spans[idx] + result[end:]
    # Restore structural arguments that a generic LaTeX parser may expose as
    # ordinary text because the corresponding package macro is unknown.
    result = re.sub(r"\\captionsetup\{[^{}]*\}", r"\\captionsetup{type=figure}", result)
    result = re.sub(r"\\captionof\{[^{}]*\}", r"\\captionof{figure}", result)
    result = result.replace("\\Hy@警告", "\\Hy@Warning")
    result = result.replace("\\def\\@类型{桌子}", "\\def\\@captype{table}")
    result = result.replace("\\pdfinfo{", "\\providecommand{\\pdfinfo}[1]{}\n\\pdfinfo{", 1)
    cjk = ("\\usepackage{xeCJK}\n"
           "\\setCJKmainfont{Noto Serif CJK SC}\n")
    pos = result.find("\\begin{document}")
    result = result[:pos] + cjk + result[pos:]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")


if __name__ == "__main__":
    main()
