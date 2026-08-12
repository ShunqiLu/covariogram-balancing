from pathlib import Path
from typing import cast

from ehrhart_fswa.certificate import create_manifest, verify_manifest


def test_manifest_detects_changes(tmp_path: Path) -> None:
    (tmp_path / "src" / "ehrhart_fswa").mkdir(parents=True)
    tracked = tmp_path / "src" / "ehrhart_fswa" / "sample.py"
    tracked.write_text("value = 1\n", encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    create_manifest(tmp_path, manifest_path)
    assert verify_manifest(tmp_path, manifest_path) == []
    tracked.write_text("value = 2\n", encoding="utf-8")
    assert verify_manifest(tmp_path, manifest_path) == [
        "hash mismatch: src/ehrhart_fswa/sample.py"
    ]


def test_manifest_excludes_itself_on_repeated_creation(tmp_path: Path) -> None:
    results = tmp_path / "results"
    results.mkdir()
    tracked = results / "sample.csv"
    tracked.write_text("a,b\n1,2\n", encoding="utf-8")
    manifest_path = results / "manifest.json"

    first = create_manifest(tmp_path, manifest_path)
    second = create_manifest(tmp_path, manifest_path)

    assert first == second
    files = cast(dict[str, str], second["files"])
    assert "results/manifest.json" not in files
    assert verify_manifest(tmp_path, manifest_path) == []
