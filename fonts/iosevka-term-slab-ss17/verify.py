# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools==4.59.0"]
# ///

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from tomllib import loads

from fontTools.ttLib import TTCollection, TTFont

FAMILY = "Iosevka Term Slab SS17"
PLAN = "IosevkaTermSlabSS17"
VERSION = "34.7.0"
UPSTREAM_REVISION = "6828cb0bd569992bb19565a5e448540de3b50541"
ADVANCE = 500
FACES = {
    "Regular": "Regular",
    "Semibold": "Semibold",
    "Bold": "Bold",
    "Italic": "Italic",
    "SemiboldItalic": "Semibold Italic",
    "BoldItalic": "Bold Italic",
}
ASCII_CODEPOINTS = tuple(range(0x20, 0x7F))
TERMINAL_SYMBOLS = (
    0x2190, 0x2191, 0x2192, 0x2193, 0x2194,
    0x21D0, 0x21D1, 0x21D2, 0x21D3, 0x21D4,
    0x25A0, 0x25A1, 0x25B2, 0x25BC, 0x25C6, 0x25CB, 0x25CF,
)
REQUIRED_TABLES = {
    "OS/2", "GDEF", "GPOS", "GSUB", "cmap", "cvt ", "fpgm", "gasp",
    "glyf", "head", "hhea", "hmtx", "loca", "maxp", "name", "post", "prep",
}


def names(font: TTFont, name_id: int) -> set[str]:
    return {record.toUnicode() for record in font["name"].names if record.nameID == name_id}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_plan(module_dir: Path, upstream_plan_path: Path) -> str:
    plan_path = module_dir / "private-build-plans.toml"
    document = loads(plan_path.read_text())
    plan = document["buildPlans"][PLAN]
    official = loads(upstream_plan_path.read_text())["buildPlans"]["IosevkaTermSS17"]
    expected = {
        "family": FAMILY,
        "spacing": "term",
        "serifs": "slab",
        "snapshotFamily": "Iosevka Slab",
        "snapshotFeature": {"NWID": 1, "ss17": 1},
        "exportGlyphNames": True,
        "noCvSs": True,
    }
    for key, value in expected.items():
        if plan.get(key) != value:
            raise AssertionError(f"build plan {key!r} is {plan.get(key)!r}, expected {value!r}")
    if plan.get("variants", {}).get("inherits") != "ss17":
        raise AssertionError("build plan must inherit SS17 variants")
    if plan.get("weights") != {
        "Regular": {"shape": 400, "menu": 400, "css": 400},
        "Semibold": {"shape": 600, "menu": 600, "css": 600},
        "Bold": {"shape": 700, "menu": 700, "css": 700},
    }:
        raise AssertionError("build plan must emit exactly Regular, Semibold, and Bold weights")
    if plan.get("slopes") != {
        "Upright": {"angle": 0, "shape": "upright", "menu": "upright", "css": "normal"},
        "Italic": {"angle": 9.4, "shape": "italic", "menu": "italic", "css": "italic"},
    }:
        raise AssertionError("build plan must emit only Upright and Italic slopes")
    if plan.get("widths") != {"Normal": {"shape": 500, "menu": 5, "css": "normal"}}:
        raise AssertionError("build plan must emit only Normal width")
    if document.get("collectPlans", {}).get(PLAN) != {"from": [PLAN]}:
        raise AssertionError("TTC collection must contain exactly this font family")

    # Apart from the custom family naming, Slab selection, snapshot family, and
    # intentional six-face output scope, inherit official Term SS17 unchanged.
    allowed_additions = {"desc", "serifs", "weights", "slopes", "widths"}
    if set(plan) - set(official) != allowed_additions:
        raise AssertionError("custom plan has undocumented differences from IosevkaTermSS17")
    for key in {"spacing", "snapshotFeature", "exportGlyphNames", "noCvSs", "variants"}:
        if plan.get(key) != official.get(key):
            raise AssertionError(f"custom plan diverges from official IosevkaTermSS17 at {key!r}")
    return sha256(plan_path)


def require_narrow_glyphs(font: TTFont, label: str, codepoints: tuple[int, ...]) -> None:
    cmap = font.getBestCmap()
    for codepoint in codepoints:
        glyph_name = cmap.get(codepoint)
        if glyph_name is None:
            raise AssertionError(f"{label}: missing U+{codepoint:04X}")
        advance, _ = font["hmtx"][glyph_name]
        if advance != ADVANCE:
            raise AssertionError(
                f"{label}: U+{codepoint:04X} advance is {advance}, expected {ADVANCE}"
            )


def verify_font(font: TTFont, label: str, expected_style: str) -> None:
    missing_tables = REQUIRED_TABLES - set(font.keys())
    if missing_tables:
        raise AssertionError(f"{label}: missing required tables {sorted(missing_tables)}")

    # The legacy family uses style linking. The full Semibold family would
    # exceed the OpenType legacy-name limit of 31 characters, so Iosevka's
    # upstream naming code uses its documented short weight name: "SmBd".
    # Typographic family/subfamily retain the common family and true style.
    is_semibold = expected_style.startswith("Semibold")
    expected_legacy_family = f"{FAMILY} SmBd" if is_semibold else FAMILY
    expected_legacy_style = "Italic" if expected_style == "Semibold Italic" else (
        "Regular" if expected_style == "Semibold" else expected_style
    )
    if names(font, 1) != {expected_legacy_family} or names(font, 16) != {FAMILY}:
        raise AssertionError(f"{label}: unexpected family metadata")
    if names(font, 2) != {expected_legacy_style} or names(font, 17) != {expected_style}:
        raise AssertionError(f"{label}: unexpected style metadata")

    expected_full_name = FAMILY if expected_style == "Regular" else f"{FAMILY} {expected_style}"
    if names(font, 4) != {expected_full_name}:
        raise AssertionError(f"{label}: unexpected full name {names(font, 4)!r}")
    if names(font, 6) != {expected_full_name.replace(' ', '-')}:
        raise AssertionError(f"{label}: unexpected PostScript name {names(font, 6)!r}")
    if font["head"].unitsPerEm != 1000:
        raise AssertionError(f"{label}: units per em is not 1000")
    if font["hhea"].ascent != 965 or font["hhea"].descent != -215 or font["hhea"].lineGap != 70:
        raise AssertionError(f"{label}: unexpected vertical metrics")
    if not any(VERSION in version for version in names(font, 5)):
        raise AssertionError(f"{label}: version does not include {VERSION}")

    require_narrow_glyphs(font, label, ASCII_CODEPOINTS)
    require_narrow_glyphs(font, label, TERMINAL_SYMBOLS)


def verify_collection(path: Path) -> str:
    collection = TTCollection(path, lazy=False)
    try:
        if len(collection.fonts) != len(FACES):
            raise AssertionError(f"{path.name}: has {len(collection.fonts)} faces, expected {len(FACES)}")
        actual_styles: set[str] = set()
        for index, font in enumerate(collection.fonts):
            style_names = names(font, 17)
            if len(style_names) != 1:
                raise AssertionError(f"{path.name} face {index}: ambiguous typographic style")
            style = style_names.pop()
            if style not in FACES.values() or style in actual_styles:
                raise AssertionError(f"{path.name} face {index}: unexpected style {style!r}")
            verify_font(font, f"{path.name} face {index} ({style})", style)
            actual_styles.add(style)
        if actual_styles != set(FACES.values()):
            raise AssertionError(f"{path.name}: styles are {actual_styles!r}")
    finally:
        collection.close()
    return sha256(path)


def write_build_info(font_dir: Path, plan_digest: str, ttc_digest: str, source_date_epoch: int) -> Path:
    build_info = {
        "family": FAMILY,
        "faces": list(FACES.values()),
        "plan_sha256": plan_digest,
        "ttc_sha256": ttc_digest,
        "source": {
            "repository": "https://github.com/be5invis/Iosevka",
            "revision": UPSTREAM_REVISION,
            "version": VERSION,
            "source_date_epoch": source_date_epoch,
        },
    }
    path = font_dir / "BUILD-INFO.json"
    path.write_text(json.dumps(build_info, indent=2, sort_keys=True) + "\n")
    return path


def write_archive(
    ttc_path: Path, module_dir: Path, archive: Path, build_info: Path, source_date_epoch: int
) -> str:
    files = (
        (ttc_path, ttc_path.name),
        (build_info, build_info.name),
        (module_dir / "README.md", "README.md"),
        (module_dir / "OFL.txt", "OFL.txt"),
    )
    archive.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.fromtimestamp(source_date_epoch, UTC).timetuple()[:6]
    expected_names = {archive_name for _, archive_name in files}
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for source, archive_name in files:
            info = zipfile.ZipInfo(archive_name, timestamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, source.read_bytes())
    with zipfile.ZipFile(archive) as bundle:
        if set(bundle.namelist()) != expected_names:
            raise AssertionError("release archive has unexpected contents")
        if bundle.testzip() is not None:
            raise AssertionError("release archive has corrupt contents")
    return sha256(archive)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", type=Path, required=True)
    parser.add_argument("--module-dir", type=Path, required=True)
    parser.add_argument("--upstream-build-plans", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--source-date-epoch", type=int, required=True)
    args = parser.parse_args()

    plan_digest = verify_plan(args.module_dir, args.upstream_build_plans)
    ttc_digest = verify_collection(args.font)
    build_info = write_build_info(args.font.parent, plan_digest, ttc_digest, args.source_date_epoch)
    archive_digest = write_archive(args.font, args.module_dir, args.archive, build_info, args.source_date_epoch)
    print(f"verified {PLAN}: TTC with term + slab + ss17")
    print(f"archive sha256 {archive_digest}")


if __name__ == "__main__":
    main()
