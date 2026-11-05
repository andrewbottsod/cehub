#!/usr/bin/env python3
"""Stamp the deploy commit onto local CSS and JS URLs.

Committed HTML stays unstamped so a local static server still works.
The Deploy Now build runs this before upload and sets ASSET_REV (or
GITHUB_SHA) so each deploy changes the query string.
"""
import os
import re
import sys
from pathlib import Path

REV_RE = re.compile(r"^[0-9a-f]{7,40}$")
ATTR_RE = re.compile(
    r"""(?P<pre>\b(?:href|src)\s*=\s*)(?P<q>["'])"""
    r"""(?P<url>(?!https?:|//|data:)[^"'?#\s]+\.(?:css|js))"""
    r"""(?P<query>\?[^"']*)?(?P<end>["'])""",
    re.I,
)
SKIP_DIRS = {".git", ".github", "node_modules"}


def revision():
    raw = os.environ.get("ASSET_REV") or os.environ.get("GITHUB_SHA", "")
    rev = raw.strip().lower()
    if not REV_RE.fullmatch(rev):
        sys.exit(f"stamp-assets: need ASSET_REV or GITHUB_SHA, got {raw!r}")
    return rev[:7]


def stamp_query(url, query, rev):
    if query and re.search(r"(?:^|[?&])v=", query):
        query = re.sub(r"((?:^|[?&])v=)[^&]*", lambda m: m.group(1) + rev, query)
        return url + query
    if query:
        return f"{url}{query}&v={rev}"
    return f"{url}?v={rev}"


def stamp_html(text, rev):
    def repl(match):
        return (
            f"{match.group('pre')}{match.group('q')}"
            f"{stamp_query(match.group('url'), match.group('query'), rev)}"
            f"{match.group('end')}"
        )

    text = ATTR_RE.sub(repl, text)
    placeholder = 'const ASSET_V="";'
    stamped = f'const ASSET_V="?v={rev}";'
    if placeholder not in text and stamped not in text:
        return text, False
    if placeholder in text:
        text = text.replace(placeholder, stamped, 1)
    return text, True


def main():
    rev = revision()
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    changed = []
    saw_hub = False
    for path in root.rglob("*.html"):
        if SKIP_DIRS.intersection(path.parts):
            continue
        original = path.read_text(encoding="utf-8")
        updated, _ = stamp_html(original, rev)
        if path.as_posix().endswith("cehub/index.html") or path.name == "index.html" and "cehub" in path.parts:
            saw_hub = True
            if f"?v={rev}" not in updated or f'const ASSET_V="?v={rev}";' not in updated:
                sys.exit(f"stamp-assets: {path} is missing the revision")
            if "fonts.googleapis.com/css2" not in updated or "supabase-js@" not in updated:
                sys.exit(f"stamp-assets: {path} lost an external URL")
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(str(path))
    hub = root / "cehub" / "index.html"
    if not hub.is_file():
        sys.exit("stamp-assets: cehub/index.html not found")
    if str(hub) not in changed and f"?v={rev}" not in hub.read_text(encoding="utf-8"):
        sys.exit("stamp-assets: cehub/index.html was not updated")
    print(f"stamp-assets: {rev} -> {', '.join(changed) if changed else '(already stamped)'}")
    if not saw_hub:
        # path.parts check above uses the path as given; confirm via content
        text = hub.read_text(encoding="utf-8")
        if f'tokens.css?v={rev}' not in text or f'const ASSET_V="?v={rev}";' not in text:
            sys.exit("stamp-assets: cehub/index.html stamp check failed")


if __name__ == "__main__":
    main()
