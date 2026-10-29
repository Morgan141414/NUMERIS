"""Fail if private specification material is staged or appears in public files."""

from pathlib import Path
import subprocess
import sys


FORBIDDEN_PATH_PARTS = ("private/", "technical_spec", "confidential", "secret")
FORBIDDEN_PHRASES = ("ТЕХНИЧЕСКОЕ ЗАДАНИЕ", "полный внутренний текст спецификации")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    tracked = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, check=True).stdout.splitlines()
    bad_paths = [p for p in tracked if any(part in p.lower() for part in FORBIDDEN_PATH_PARTS)]
    if bad_paths:
        print("Forbidden tracked paths:", *bad_paths, sep="\n", file=sys.stderr)
        return 1
    for path in root.rglob("*"):
        if (not path.is_file() or ".git" in path.parts or "private" in path.parts
                or path == Path(__file__)):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if any(phrase in text for phrase in FORBIDDEN_PHRASES):
            print(f"Forbidden private phrase in public file: {path}", file=sys.stderr)
            return 1
    print("Publication safety check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
