from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote, urlparse

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import sync_mkdocs_docs


REQUIRED_FRONTMATTER_KEYS = {
    "title",
    "type",
    "status",
    "audience",
    "last-updated",
}
ALLOWED_TYPE_VALUES = {"reference", "explanation", "plan", "adr", "how-to"}
ALLOWED_STATUS_VALUES = {"active", "draft", "archived"}
ALLOWED_AUDIENCE_VALUES = {
    "all",
    "contributor",
    "developer",
    "evaluator",
    "staff-engineer",
}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FENCED_CODE_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)
BROKEN_LINK_CHECK_EXCLUDED_PATHS = {
    # Temporary exclusions: these files currently contain known historical link debt.
    # Keep excluded until links are normalized, then remove from this set.
    Path("projects/veterinary-medical-records/04-delivery/implementation-history.md"),
    Path("projects/veterinary-medical-records/04-delivery/implementation-plan.md"),
}


def load_frontmatter(markdown_path: Path) -> dict[str, object]:
    content = markdown_path.read_text(encoding="utf-8")
    normalized_content = content.replace("\r\n", "\n")
    if not normalized_content.startswith("---\n"):
        return {}

    _, _, remainder = normalized_content.partition("---\n")
    frontmatter_block, separator, _ = remainder.partition("\n---\n")
    if not separator:
        return {}

    loaded = yaml.safe_load(frontmatter_block) or {}
    return loaded if isinstance(loaded, dict) else {}


def iter_published_source_docs() -> list[Path]:
    return sync_mkdocs_docs.iter_included_source_docs()


def iter_link_validated_docs() -> list[Path]:
    validated_docs: list[Path] = []
    for markdown_path in iter_published_source_docs():
        relative_path = markdown_path.relative_to(REPO_ROOT)
        if relative_path in BROKEN_LINK_CHECK_EXCLUDED_PATHS:
            continue
        validated_docs.append(markdown_path)
    return validated_docs


def iter_markdown_links(markdown_path: Path) -> list[str]:
    content = markdown_path.read_text(encoding="utf-8")
    content_without_code_blocks = re.sub(FENCED_CODE_BLOCK_PATTERN, "", content)
    return MARKDOWN_LINK_PATTERN.findall(content_without_code_blocks)


def is_external_link(target: str) -> bool:
    parsed = urlparse(target)
    return parsed.scheme in {"http", "https", "mailto"}


def resolve_repo_target(source_path: Path, target: str) -> Path | None:
    if not target or target.startswith("#") or is_external_link(target):
        return None

    clean_target = unquote(target.split("#", 1)[0].split("?", 1)[0]).strip()
    if not clean_target:
        return None

    return (source_path.parent / clean_target).resolve()


def is_within_repo(target_path: Path) -> bool:
    try:
        target_path.relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


def iter_nav_targets(nav_config: object) -> list[str]:
    targets: list[str] = []
    if isinstance(nav_config, list):
        for item in nav_config:
            targets.extend(iter_nav_targets(item))
    elif isinstance(nav_config, dict):
        for value in nav_config.values():
            targets.extend(iter_nav_targets(value))
    elif isinstance(nav_config, str):
        targets.append(nav_config)
    return targets


class DocsContractsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sync_mkdocs_docs.main()

    def test_sync_and_mkdocs_build(self) -> None:
        completed_process = subprocess.run(
            ["mkdocs", "build", "--clean"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            completed_process.returncode,
            0,
            msg=(completed_process.stdout + "\n" + completed_process.stderr).strip(),
        )

    def test_links_resolve_to_existing_repository_files(self) -> None:
        failures: list[str] = []
        for markdown_path in iter_link_validated_docs():
            for target in iter_markdown_links(markdown_path):
                resolved_target = resolve_repo_target(markdown_path, target)
                if resolved_target is None:
                    continue
                if not is_within_repo(resolved_target):
                    failures.append(
                        f"{markdown_path.relative_to(REPO_ROOT)} -> {target} -> outside repository"
                    )
                    continue
                if resolved_target.exists():
                    continue
                failures.append(
                    f"{markdown_path.relative_to(REPO_ROOT)} -> {target} -> {resolved_target.relative_to(REPO_ROOT.parent)}"
                )

        self.assertFalse(failures, msg="Broken file links:\n" + "\n".join(sorted(failures)))

    def test_published_docs_have_required_frontmatter(self) -> None:
        failures: list[str] = []
        for markdown_path in iter_published_source_docs():
            frontmatter = load_frontmatter(markdown_path)
            missing_keys = sorted(REQUIRED_FRONTMATTER_KEYS - set(frontmatter.keys()))
            if missing_keys:
                failures.append(f"{markdown_path.relative_to(REPO_ROOT)} missing {', '.join(missing_keys)}")

        self.assertFalse(failures, msg="Missing frontmatter keys:\n" + "\n".join(failures))

    def test_published_docs_have_valid_frontmatter_values(self) -> None:
        failures: list[str] = []
        for markdown_path in iter_published_source_docs():
            frontmatter = load_frontmatter(markdown_path)
            if not frontmatter:
                continue

            if frontmatter.get("type") not in ALLOWED_TYPE_VALUES:
                failures.append(
                    f"{markdown_path.relative_to(REPO_ROOT)} has invalid type={frontmatter.get('type')!r}"
                )
            if frontmatter.get("status") not in ALLOWED_STATUS_VALUES:
                failures.append(
                    f"{markdown_path.relative_to(REPO_ROOT)} has invalid status={frontmatter.get('status')!r}"
                )
            if frontmatter.get("audience") not in ALLOWED_AUDIENCE_VALUES:
                failures.append(
                    f"{markdown_path.relative_to(REPO_ROOT)} has invalid audience={frontmatter.get('audience')!r}"
                )

            last_updated = str(frontmatter.get("last-updated", ""))
            if not DATE_PATTERN.match(last_updated):
                failures.append(
                    f"{markdown_path.relative_to(REPO_ROOT)} has invalid last-updated={last_updated!r}"
                )

        self.assertFalse(failures, msg="Invalid frontmatter values:\n" + "\n".join(failures))

    def test_mkdocs_nav_targets_exist(self) -> None:
        mkdocs_config = yaml.safe_load((REPO_ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
        nav_targets = iter_nav_targets(mkdocs_config.get("nav", []))

        failures: list[str] = []
        for nav_target in nav_targets:
            generated_path = sync_mkdocs_docs.GENERATED_DOCS_DIR / nav_target
            if not generated_path.exists():
                failures.append(nav_target)

        self.assertFalse(failures, msg="MkDocs nav targets missing:\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
