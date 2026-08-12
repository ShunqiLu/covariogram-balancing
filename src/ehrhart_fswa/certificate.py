"""Create and verify SHA-256 manifests for the reproducibility package."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
from typing import Sequence, cast


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def tracked_files(root: Path) -> list[Path]:
    patterns = [
        "src/ehrhart_fswa/*.py",
        "tests/*.py",
        "research/*.md",
        "research/*.bib",
        "research/*.py",
        "research/sources/*.xlsx",
        "research/sources/*.json",
        "results/*.csv",
        "results/*.json",
        "results/*.md",
        "paper/*.py",
        "paper/*.tex",
        "paper/*.pdf",
        "paper/*.bib",
        "paper/*.md",
        "paper/*.cls",
        "paper/*.bst",
        "paper/drawio/*.drawio",
        "README.md",
        "pyproject.toml",
        "scripts/*.ps1",
        "scripts/*.py",
        "scripts/*.sh",
        "requirements-repro.txt",
    ]
    files: set[Path] = set()
    for pattern in patterns:
        files.update(path for path in root.glob(pattern) if path.is_file())
    return sorted(files)


def create_manifest(root: Path, output: Path) -> dict[str, object]:
    # A manifest cannot contain a stable hash of itself.  Exclude the output
    # explicitly so repeated creation behaves exactly like the first run.
    output_resolved = output.resolve()
    files = [path for path in tracked_files(root) if path.resolve() != output_resolved]
    manifest: dict[str, object] = {
        "schema": 1,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "files": {path.relative_to(root).as_posix(): _sha256(path) for path in files},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def verify_manifest(root: Path, manifest_path: Path) -> list[str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = []
    for relative, expected in manifest["files"].items():
        path = root / relative
        if not path.is_file():
            failures.append(f"missing: {relative}")
        else:
            actual = _sha256(path)
            if actual != expected:
                failures.append(f"hash mismatch: {relative}")
    return failures


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["create", "verify"])
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--manifest", type=Path, default=Path("results") / "manifest.json"
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    manifest_path = (
        args.manifest if args.manifest.is_absolute() else root / args.manifest
    )
    if args.action == "create":
        manifest = create_manifest(root, manifest_path)
        file_hashes = cast(dict[str, str], manifest["files"])
        print(f"wrote hashes for {len(file_hashes)} files to {manifest_path}")
        return 0
    failures = verify_manifest(root, manifest_path)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print(f"verified every hash in {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
