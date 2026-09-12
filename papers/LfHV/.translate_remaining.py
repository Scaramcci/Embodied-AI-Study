import json
import re
import shutil
import time
import urllib.parse
import urllib.request
from pathlib import Path


SOURCE = Path("Robot Learning from Human Videos_中文翻译.md")
BACKUP = Path("Robot Learning from Human Videos_中文翻译_批量翻译前备份.md")

LATEX_ONLY = re.compile(
    r"^\s*(?:\\(?:begin|end|includegraphics|label|vspace|hspace|centering|"
    r"captionsetup|resizebox|setlength|addplot|draw|node|path|coordinate|"
    r"definecolor|toprule|midrule|bottomrule|bibliography|bibliographystyle|"
    r"documentclass|usepackage|newcommand|def|setcounter|runninghead|author|"
    r"affiliation|corrauth|email|maketitle|keywords|usetikzlibrary)|%|\}|\{)"
)
HAS_ENGLISH = re.compile(r"[A-Za-z]{3,}")
HAS_CHINESE = re.compile(r"[\u4e00-\u9fff]")


def google_translate(text: str) -> str:
    params = urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": "zh-CN", "dt": "t", "q": text}
    )
    url = "https://translate.googleapis.com/translate_a/single?" + params
    last_error = None
    for attempt in range(5):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
            return "".join(item[0] for item in data[0] if item[0])
        except Exception as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"translation failed: {last_error}")


def split_long(text: str, limit: int = 3500) -> list[str]:
    if len(text) <= limit:
        return [text]
    pieces = re.split(r"(?<=[.!?。！？])\s+", text)
    chunks, current = [], ""
    for piece in pieces:
        if current and len(current) + len(piece) + 1 > limit:
            chunks.append(current)
            current = piece
        else:
            current = f"{current} {piece}".strip()
    if current:
        chunks.append(current)
    return chunks


def protect(text: str) -> tuple[str, list[str]]:
    saved: list[str] = []

    def hold(match: re.Match) -> str:
        token = f"ZXQ{len(saved):04d}QXZ"
        saved.append(match.group(0))
        return token

    patterns = [
        r"\$[^$]+\$",
        r"\\(?:citep|cite|ref|eqref|label|url)\{[^{}]*\}",
        r"\\(?:includegraphics|vspace|hspace|setlength)\b[^\n]*",
    ]
    for pattern in patterns:
        text = re.sub(pattern, hold, text)
    # Preserve command syntax while allowing emphasized prose to be translated.
    text = re.sub(r"\\(textit|textbf|emph)\{([^{}]*)\}", r"ZXOPEN\1QXZ \2 ZXCLOSEQXZ", text)
    return text, saved


def restore(text: str, saved: list[str]) -> str:
    text = re.sub(r"ZXOPEN(textit|textbf|emph)QXZ\s*", r"\\\1{", text)
    text = re.sub(r"\s*ZXCLOSEQXZ", "}", text)
    for index, value in enumerate(saved):
        text = text.replace(f"ZXQ{index:04d}QXZ", value)
        text = text.replace(f"ZXQ {index:04d} QXZ", value)
    return text


def translate_line(line: str) -> str:
    if not HAS_ENGLISH.search(line) or LATEX_ONLY.match(line):
        return line
    # Existing bilingual/Chinese prose has already been reviewed manually.
    if HAS_CHINESE.search(line) and len(HAS_CHINESE.findall(line)) > 8:
        return line
    prefix = ""
    body = line
    item = re.match(r"^(\s*\\item\s+)(.*)$", line)
    caption = re.match(r"^(\s*\\caption\{)(.*)(\}\s*)$", line)
    if item:
        prefix, body = item.group(1), item.group(2)
    elif caption:
        prefix, body = caption.group(1), caption.group(2)
    elif line.lstrip().startswith("\\"):
        return line
    protected, saved = protect(body)
    translated = "".join(google_translate(chunk) for chunk in split_long(protected))
    translated = restore(translated, saved)
    if caption:
        return prefix + translated + caption.group(3)
    return prefix + translated


def main() -> None:
    if not BACKUP.exists():
        shutil.copy2(SOURCE, BACKUP)
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    output = []
    translated_count = 0
    for number, line in enumerate(lines, 1):
        result = translate_line(line)
        output.append(result)
        if result != line:
            translated_count += 1
        if number % 100 == 0:
            print(f"processed {number}/{len(lines)}, translated {translated_count}", flush=True)
    SOURCE.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"done: translated {translated_count} lines")


if __name__ == "__main__":
    main()
