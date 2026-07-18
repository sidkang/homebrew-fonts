# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools==4.59.0"]
# ///

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

FAMILY = "Braille Spinner Kitty Term"
POSTSCRIPT_NAME = "BrailleSpinnerKittyTerm-Regular"
VERSION = "1.0.1"
UNITS_PER_EM = 1000
ADVANCE_WIDTH = 500
ASCENDER = 965
DESCENDER = -215
LINE_GAP = 70
TYPO_DESCENDER = -285
DOT_RADIUS = 81
DOT_DIAGONAL = 57
DOT_CONTROL_OFFSET = 34
COLUMNS = (125, 375)
ROWS = (629, 376, 124)
BRAILLE_ALIAS_START = 0xF800
BRAILLE_ALIAS_END = 0xF83F
MAC_EPOCH_OFFSET = 2_082_844_800
SOURCE_DATE_EPOCH = 1_784_006_400  # 2026-07-14T00:00:00Z

# Unicode Braille bits 1-6: left rows 1-3, then right rows 1-3.
DOT_POSITIONS = (
    (COLUMNS[0], ROWS[0]),
    (COLUMNS[0], ROWS[1]),
    (COLUMNS[0], ROWS[2]),
    (COLUMNS[1], ROWS[0]),
    (COLUMNS[1], ROWS[1]),
    (COLUMNS[1], ROWS[2]),
)


def empty_glyph():
    return TTGlyphPen(None).glyph()


def spinner_glyph(pattern: int):
    pen = TTGlyphPen(None)
    for bit, (cx, cy) in enumerate(DOT_POSITIONS):
        if not pattern & (1 << bit):
            continue

        # Eight quadratic curves form one clockwise circular contour.
        pen.moveTo((cx + DOT_RADIUS, cy))
        pen.qCurveTo(
            (cx + DOT_RADIUS, cy - DOT_CONTROL_OFFSET),
            (cx + DOT_DIAGONAL, cy - DOT_DIAGONAL),
        )
        pen.qCurveTo(
            (cx + DOT_CONTROL_OFFSET, cy - DOT_RADIUS),
            (cx, cy - DOT_RADIUS),
        )
        pen.qCurveTo(
            (cx - DOT_CONTROL_OFFSET, cy - DOT_RADIUS),
            (cx - DOT_DIAGONAL, cy - DOT_DIAGONAL),
        )
        pen.qCurveTo(
            (cx - DOT_RADIUS, cy - DOT_CONTROL_OFFSET),
            (cx - DOT_RADIUS, cy),
        )
        pen.qCurveTo(
            (cx - DOT_RADIUS, cy + DOT_CONTROL_OFFSET),
            (cx - DOT_DIAGONAL, cy + DOT_DIAGONAL),
        )
        pen.qCurveTo(
            (cx - DOT_CONTROL_OFFSET, cy + DOT_RADIUS),
            (cx, cy + DOT_RADIUS),
        )
        pen.qCurveTo(
            (cx + DOT_CONTROL_OFFSET, cy + DOT_RADIUS),
            (cx + DOT_DIAGONAL, cy + DOT_DIAGONAL),
        )
        pen.qCurveTo(
            (cx + DOT_RADIUS, cy + DOT_CONTROL_OFFSET),
            (cx + DOT_RADIUS, cy),
        )
        pen.closePath()
    return pen.glyph()


def build_font(output: Path) -> None:
    glyph_order = [".notdef"]
    glyphs = {".notdef": empty_glyph()}
    metrics = {".notdef": (ADVANCE_WIDTH, 0)}
    cmap: dict[int, str] = {}

    for codepoint in range(BRAILLE_ALIAS_START, BRAILLE_ALIAS_END + 1):
        pattern = codepoint - BRAILLE_ALIAS_START
        name = f"brailleAlias{pattern:02X}"
        glyph_order.append(name)
        glyphs[name] = spinner_glyph(pattern)
        active_columns = [
            cx
            for bit, (cx, _cy) in enumerate(DOT_POSITIONS)
            if pattern & (1 << bit)
        ]
        left_side_bearing = min(active_columns) - DOT_RADIUS if active_columns else 0
        metrics[name] = (ADVANCE_WIDTH, left_side_bearing)
        cmap[codepoint] = name

    builder = FontBuilder(UNITS_PER_EM, isTTF=True)
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(
        ascent=ASCENDER,
        descent=DESCENDER,
        lineGap=LINE_GAP,
    )
    builder.setupNameTable(
        {
            "copyright": "Copyright (c) 2026 Sid Kang",
            "familyName": FAMILY,
            "styleName": "Regular",
            "uniqueFontIdentifier": f"Sid Kang: {FAMILY}: {VERSION}",
            "fullName": f"{FAMILY} Regular",
            "version": f"Version {VERSION}",
            "psName": POSTSCRIPT_NAME,
            "typographicFamily": FAMILY,
            "typographicSubfamily": "Regular",
            "designer": "Sid Kang",
            "description": "Fixed-grid private-use Braille spinner glyphs for Kitty terminals",
            "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
            "licenseInfoURL": "https://openfontlicense.org",
        }
    )
    builder.setupOS2(
        sTypoAscender=ASCENDER,
        sTypoDescender=TYPO_DESCENDER,
        sTypoLineGap=0,
        usWinAscent=ASCENDER,
        usWinDescent=-TYPO_DESCENDER,
        usWeightClass=400,
        usWidthClass=5,
        fsSelection=0x40,
        fsType=0,
        sxHeight=530,
        sCapHeight=735,
        achVendID="SIDK",
    )
    builder.setupPost(
        italicAngle=0,
        underlinePosition=-150,
        underlineThickness=50,
        isFixedPitch=1,
        keepGlyphNames=True,
    )
    builder.setupMaxp()

    font = builder.font
    font["head"].created = MAC_EPOCH_OFFSET + SOURCE_DATE_EPOCH
    font["head"].modified = MAC_EPOCH_OFFSET + SOURCE_DATE_EPOCH
    font["head"].flags = 0x0003
    font["head"].macStyle = 0
    font["OS/2"].xAvgCharWidth = ADVANCE_WIDTH
    font.recalcTimestamp = False
    output.parent.mkdir(parents=True, exist_ok=True)
    font.save(output, reorderTables=False)


def verify_font(path: Path) -> None:
    font = TTFont(path, recalcBBoxes=False, recalcTimestamp=False)
    cmap = font.getBestCmap()
    expected_codepoints = set(range(BRAILLE_ALIAS_START, BRAILLE_ALIAS_END + 1))
    if set(cmap) != expected_codepoints:
        raise AssertionError("font cmap is not exactly U+F800-U+F83F")

    family_names = {
        record.toUnicode()
        for record in font["name"].names
        if record.nameID in {1, 16}
    }
    if family_names != {FAMILY}:
        raise AssertionError(f"unexpected family names: {family_names}")

    if font["head"].unitsPerEm != UNITS_PER_EM:
        raise AssertionError("unexpected units per em")
    if font["hhea"].ascent != ASCENDER or font["hhea"].descent != DESCENDER:
        raise AssertionError("unexpected vertical metrics")

    glyf = font["glyf"]
    for codepoint, glyph_name in cmap.items():
        pattern = codepoint - BRAILLE_ALIAS_START
        advance, left_side_bearing = font["hmtx"][glyph_name]
        if advance != ADVANCE_WIDTH:
            raise AssertionError(f"U+{codepoint:04X} has advance {advance}")

        glyph = glyf[glyph_name]
        expected_dots = pattern.bit_count()
        if glyph.numberOfContours != expected_dots:
            raise AssertionError(
                f"U+{codepoint:04X} has {glyph.numberOfContours} contours; expected {expected_dots}"
            )
        if expected_dots == 0:
            if left_side_bearing != 0:
                raise AssertionError("empty alias must have a zero left side bearing")
            continue
        if left_side_bearing != glyph.xMin:
            raise AssertionError(
                f"U+{codepoint:04X} has LSB {left_side_bearing}; expected xMin {glyph.xMin}"
            )

        coordinates, endpoints, _ = glyph.getCoordinates(glyf)
        start = 0
        actual_centers = []
        for endpoint in endpoints:
            contour = coordinates[start : endpoint + 1]
            xs = [point[0] for point in contour]
            ys = [point[1] for point in contour]
            actual_centers.append(((min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2))
            start = endpoint + 1

        expected_centers = [
            DOT_POSITIONS[bit]
            for bit in range(len(DOT_POSITIONS))
            if pattern & (1 << bit)
        ]
        if sorted(actual_centers) != sorted(expected_centers):
            raise AssertionError(
                f"U+{codepoint:04X} uses {actual_centers}; expected {expected_centers}"
            )

    font.close()


def write_release_archive(font_path: Path, module_dir: Path, archive: Path) -> None:
    files = (
        (font_path, font_path.name),
        (module_dir / "README.md", "README.md"),
        (module_dir / "OFL.txt", "OFL.txt"),
    )
    archive.parent.mkdir(parents=True, exist_ok=True)
    timestamp = (2026, 7, 14, 0, 0, 0)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for source, archive_name in files:
            info = zipfile.ZipInfo(archive_name, timestamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, source.read_bytes())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    module_dir = Path(__file__).resolve().parent
    output_dir = repo_root / "dist" / "braille-spinner-kitty-term"
    release_dir = repo_root / "dist" / "releases"
    font_path = output_dir / "BrailleSpinnerKittyTerm-Regular.ttf"
    archive = release_dir / f"BrailleSpinnerKittyTerm-{VERSION}.zip"

    if output_dir.exists():
        shutil.rmtree(output_dir)
    build_font(font_path)
    verify_font(font_path)
    write_release_archive(font_path, module_dir, archive)

    print(f"built {font_path}")
    print(f"verified U+F800-U+F83F on one fixed 2x3 grid")
    print(f"packaged {archive}")


if __name__ == "__main__":
    main()
