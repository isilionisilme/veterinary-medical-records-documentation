from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / ".mkdocs"

# Keep generated docs focused for evaluators; avoid publishing planning/backlog internals.
EXCLUDED_PARTS = {"plans", "Backlog"}


def copy_tree(source: Path, destination: Path) -> None:
    for path in source.rglob("*"):
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        rel = path.relative_to(source)
        target = destination / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def main() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for filename in ["README.md"]:
        source = REPO_ROOT / filename
        if source.exists():
            shutil.copy2(source, OUTPUT_DIR / filename)

    for folder in ["shared", "projects"]:
        source = REPO_ROOT / folder
        if source.exists():
            copy_tree(source, OUTPUT_DIR / folder)


if __name__ == "__main__":
    main()
