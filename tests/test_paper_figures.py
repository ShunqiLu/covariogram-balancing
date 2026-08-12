from __future__ import annotations

from pathlib import Path
import re
import xml.etree.ElementTree as ET

import pytest


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
DRAWIO = PAPER / "drawio"

# \textwidth of sn-jnl.cls in the used class options, in PostScript points.
TEXTWIDTH_PT = 5.147 * 72.0

INCLUDE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")


def figures_of(document: str) -> set[str]:
    source = (PAPER / document).read_text(encoding="utf-8")
    return {Path(name).stem for name in INCLUDE.findall(source)}


def test_every_main_figure_is_produced_by_the_generator_script() -> None:
    script = (PAPER / "makefigs.py").read_text(encoding="utf-8")
    defaults = dict(
        re.findall(r"def (fig_\w+)\(path=\"([^\"]+)\"\)", script)
    )
    driver = script.split("__main__", 1)[1]
    called = re.findall(r"^    (fig_\w+)\(\)$", driver, flags=re.MULTILINE)
    assert set(called) == set(defaults)
    assert {Path(defaults[name]).stem for name in called} == figures_of("focus.tex")


def test_delivery_export_order_matches_the_manuscript_numbering() -> None:
    source = (PAPER / "focus.tex").read_text(encoding="utf-8")
    declared = [Path(name).stem for name in INCLUDE.findall(source)]
    driver = (ROOT / "scripts" / "reproduce.py").read_text(encoding="utf-8")
    exported = re.findall(
        r'^        "(fig-[\w-]+)",$',
        driver.split("main_figures = [", 1)[1].split("]", 1)[0],
        flags=re.MULTILINE,
    )
    assert exported == declared

    readme = (PAPER / "submission_figures" / "README.md").read_text(encoding="utf-8")
    for index, stem in enumerate(declared, start=1):
        row = next(line for line in readme.splitlines() if f"`Fig{index}.eps`" in line)
        assert stem.replace("fig-", "fig_").replace("-", "_") in row


def test_every_included_figure_exists_and_fits_the_text_block() -> None:
    pypdf = pytest.importorskip("pypdf")
    stems = figures_of("focus.tex") | figures_of("online_resource_crypto.tex")
    for stem in sorted(stems):
        path = PAPER / f"{stem}.pdf"
        assert path.is_file()
        pages = pypdf.PdfReader(str(path)).pages
        assert len(pages) == 1
        box = pages[0].mediabox
        assert 0 < float(box.width) <= TEXTWIDTH_PT + 0.5
        assert 0 < float(box.height) <= 8.0 * 72.0


def test_every_figure_is_labelled_and_referenced() -> None:
    source = (PAPER / "focus.tex").read_text(encoding="utf-8")
    blocks = re.findall(r"\\begin\{figure\}(.*?)\\end\{figure\}", source, flags=re.S)
    assert len(blocks) == len(figures_of("focus.tex"))
    for block in blocks:
        labels = re.findall(r"\\label\{(fig:[^}]+)\}", block)
        assert len(labels) == 1
        assert "\\caption{" in block
        assert len(re.findall(rf"\\ref\{{{re.escape(labels[0])}\}}", source)) >= 1


def test_online_resource_drawio_source_is_editable_and_within_its_page() -> None:
    paths = sorted(DRAWIO.glob("*.drawio"))
    assert {path.stem for path in paths} == figures_of("online_resource_crypto.tex")
    for path in paths:
        root = ET.parse(path).getroot()
        assert root.tag == "mxfile"
        assert root.attrib["compressed"] == "false"
        pages = root.findall("diagram")
        assert len(pages) == 1
        model = pages[0].find("mxGraphModel")
        assert model is not None
        width, height = 1450, 700
        assert (int(model.attrib["pageWidth"]), int(model.attrib["pageHeight"])) == (
            width,
            height,
        )
        assert len(model.findall(".//mxCell")) >= 23

        # Every editable box stays inside its declared page, so exports cannot
        # silently crop labels or borders.
        for cell in model.findall(".//mxCell[@vertex='1']"):
            geometry = cell.find("mxGeometry")
            assert geometry is not None
            x = float(geometry.attrib.get("x", 0))
            y = float(geometry.attrib.get("y", 0))
            box_width = float(geometry.attrib.get("width", 0))
            box_height = float(geometry.attrib.get("height", 0))
            assert 0 <= x <= x + box_width <= width
            assert 0 <= y <= y + box_height <= height

            font = re.search(r"(?:^|;)fontSize=(\d+)(?:;|$)", cell.attrib.get("style", ""))
            if font:
                assert int(font.group(1)) >= 16
