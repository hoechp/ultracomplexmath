"""Check local Markdown links/anchors and executable user-guide examples."""

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # Checkout-only example modules used by research snippets.
GUIDES = (
    "README.md",
    "docs/getting-started.md",
    "docs/exact-arithmetic.md",
    "docs/unified-geometry.md",
    "docs/fields.md",
    "docs/formula-compression.md",
    "docs/research/novelty.md",
)


def without_fences(text):
    return re.sub(r"^```[^\n]*\n.*?^```\s*$", "", text, flags=re.M | re.S)


def anchors(text):
    found = set()
    counts = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", without_fences(text), re.M):
        slug = "".join(c for c in heading.lower() if c.isalnum() or c in "_ -")
        slug = slug.replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        found.add(f"{slug}-{count}" if count else slug)
    return found


def main():
    pages = [ROOT / name for name in ("README.md", "CONTRIBUTING.md", "CHANGELOG.md")]
    pages += sorted((ROOT / "docs").rglob("*.md"))
    checked = 0
    errors = []
    for page in pages:
        text = without_fences(page.read_text())
        for target in re.findall(r"!?\[[^\]\n]*\]\(([^\s)]+)\)", text):
            parts = urlsplit(target)
            if parts.scheme or parts.netloc:
                continue
            dest = (page.parent / unquote(parts.path)).resolve() if parts.path else page
            checked += 1
            if not dest.exists():
                errors.append(f"{page.relative_to(ROOT)}: missing {target}")
            elif parts.fragment and dest.suffix == ".md":
                if unquote(parts.fragment) not in anchors(dest.read_text()):
                    errors.append(f"{page.relative_to(ROOT)}: missing anchor {target}")
    if errors:
        raise SystemExit("\n".join(errors))

    snippets = 0
    for name in GUIDES:
        namespace = {"__name__": "__documentation_example__"}
        for number, source in enumerate(
            re.findall(r"^```python\n(.*?)^```", (ROOT / name).read_text(), re.M | re.S), 1
        ):
            exec(compile(source, f"{name}:example-{number}", "exec"), namespace)
            snippets += 1
    print(f"Checked {checked} local links/anchors in {len(pages)} pages and {snippets} examples")


if __name__ == "__main__":
    main()
