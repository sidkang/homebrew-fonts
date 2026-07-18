# Braille Spinner Kitty Term

A tiny terminal symbol font containing fixed-grid Braille spinner aliases for Kitty.

## Why it exists

Kitty renders standard Braille (`U+2800–U+28FF`) with its internal box renderer before consulting `symbol_map`. A custom font therefore cannot replace those standard glyphs directly.

This font defines equivalent six-dot patterns in the Private Use Area:

```text
standard Braille U+2800–U+283F
                 ↓ same bit pattern
private aliases  U+F800–U+F83F
```

A Kitty tab-bar script can translate a standard spinner frame using:

```python
alias = 0xF800 + ord(frame) - 0x2800
```

Kitty then treats the result as an ordinary font glyph and routes it through `symbol_map`.

## Geometry

Every alias uses one fixed two-column by three-row grid:

```text
columns: 125, 375
rows:    629, 376, 124
```

The em size is 1000 units, the advance is 500 units, and every dot has the same outline. Changing frames only changes which fixed positions are lit.

## Kitty configuration

Use an unmodified Iosevka as the primary font and map only the alias range:

```conf
font_family Iosevka Term SS17
symbol_map U+F800-U+F83F Braille Spinner Kitty Term
narrow_symbols U+F800-U+F83F 1
```

The tab-bar alias conversion is still required. Installing this font alone does not override standard Unicode Braille.

## Build

GitHub Actions is the only supported build path. The verification workflow invokes this module's `build.sh`, which builds from `build.py`; the release workflow publishes the verified ZIP.

Output:

```text
dist/braille-spinner-kitty-term/BrailleSpinnerKittyTerm-Regular.ttf
dist/releases/BrailleSpinnerKittyTerm-1.0.1.zip
```

## Install on macOS

The Homebrew cask is the recommended installation:

```bash
brew install --cask sidkang/fonts/font-braille-spinner-kitty-term
```

For a manually downloaded and extracted release ZIP, use this module's installer:

```bash
fonts/braille-spinner-kitty-term/install.sh BrailleSpinnerKittyTerm-Regular.ttf
```

It installs the font at:

```text
~/Library/Fonts/BrailleSpinnerKittyTerm-Regular.ttf
```

## License

The font is licensed under the SIL Open Font License 1.1. The build script is licensed under the repository's MIT license.
