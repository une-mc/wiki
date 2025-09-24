#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict

DOCS_ROOT_DEFAULT = Path("docs")
IGNORE_DIRS = {"_assets", ".git", "site", "stylesheets"}

CANONICAL = {
    "russia": "russia",
    "rsfsr": "russia",
    "russian-federation": "russia",
    "ukraine": "ukraine",
    "belarus": "belarus",
    "pridnestrovie": "pridnestrovie",
    "austria": "austria",
}
COUNTRY_NAMES = {
    "russia": "Russia",
    "ukraine": "Ukraine",
    "belarus": "Belarus",
    "pridnestrovie": "Pridnestrovie",
    "austria": "Austria",
}
TOP_LEVEL_SECTIONS = {"countries", "people", "politics", "economy", "organisations"}

def is_ignored(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)

def main():
    docs_root = DOCS_ROOT_DEFAULT if DOCS_ROOT_DEFAULT.exists() else Path(".")
    total = defaultdict(int)
    by_section = defaultdict(lambda: defaultdict(int))  # country -> section -> count

    for md in docs_root.rglob("*.md"):
        if is_ignored(md.parent):
            continue

        parts = md.relative_to(docs_root).parts
        if not parts:
            continue

        # Find country slug in any path segment
        canon = None
        for part in parts:
            if part in CANONICAL:
                canon = CANONICAL[part]
                break
        if not canon:
            # special case: direct country page under countries/<slug>.md
            if len(parts) >= 2 and parts[0] == "countries":
                slug = Path(parts[1]).stem
                if slug in CANONICAL:
                    canon = CANONICAL[slug]
        if not canon:
            continue

        total[canon] += 1

        section = parts[0] if parts[0] in TOP_LEVEL_SECTIONS else "_other"
        by_section[canon][section] += 1

    if not total:
        print("No country articles found.")
        return

    rows = sorted(total.items(), key=lambda kv: (-kv[1], COUNTRY_NAMES.get(kv[0], kv[0]).lower()))

    # Console
    print("Country coverage (with section breakdown):\n")
    for canon, cnt in rows:
        name = COUNTRY_NAMES.get(canon, canon)
        print(f"- {name}: {cnt}")
        for sec in sorted(by_section[canon].keys()):
            print(f"    • {sec}: {by_section[canon][sec]}")
    # Markdown
    print("\n\nMarkdown table:\n")
    print("| Country | Articles | countries | people | politics | economy | organisations | other |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for canon, cnt in rows:
        name = COUNTRY_NAMES.get(canon, canon)
        def g(s): return by_section[canon].get(s, 0)
        print(f"| {name} | {cnt} | {g('countries')} | {g('people')} | {g('politics')} | {g('economy')} | {g('organisations')} | {g('_other')} |")

if __name__ == "__main__":
    main()
