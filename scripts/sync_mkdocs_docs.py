from __future__ import annotations

import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DOCS_DIR = REPO_ROOT / ".mkdocs"
INCLUDE_PATHS = [REPO_ROOT / "shared", REPO_ROOT / "projects"]
EXCLUDED_PARTS = {
    "projects/veterinary-medical-records/04-delivery/Backlog",
    "projects/veterinary-medical-records/04-delivery/plans",
}


def reset_generated_docs_dir() -> None:
    if GENERATED_DOCS_DIR.exists():
        shutil.rmtree(GENERATED_DOCS_DIR)
    GENERATED_DOCS_DIR.mkdir(parents=True)


def copy_markdown_tree(source_root: Path) -> None:
    for source_path in source_root.rglob("*.md"):
        relative_path = source_path.relative_to(REPO_ROOT)
        relative_parent = relative_path.parent.as_posix()
        if any(
            relative_parent == excluded_part
            or relative_parent.startswith(f"{excluded_part}/")
            for excluded_part in EXCLUDED_PARTS
        ):
            continue
        target_path = GENERATED_DOCS_DIR / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)


def sync_root_index() -> None:
    root_readme = REPO_ROOT / "README.md"
    shutil.copy2(root_readme, GENERATED_DOCS_DIR / "README.md")
    shutil.copy2(root_readme, GENERATED_DOCS_DIR / "index.md")


def main() -> None:
    reset_generated_docs_dir()
    sync_root_index()
    for source_root in INCLUDE_PATHS:
        copy_markdown_tree(source_root)


if __name__ == "__main__":
    main()
