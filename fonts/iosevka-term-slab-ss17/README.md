# Iosevka Term Slab SS17

A custom [Iosevka](https://github.com/be5invis/Iosevka) terminal font that combines three independent upstream options:

```text
Term  → terminal-width arrows and geometric symbols
Slab  → slab-serif Latin glyphs
SS17  → Recursive Mono-style character variants
```

## Naming and scope

The family follows Iosevka's official word order:

```text
Iosevka Term Slab
Iosevka Term SS17
Iosevka Term Slab SS17  ← this custom combination
```

The official prebuilt packages provide the first two families but not their combination.

This module intentionally generates the six natural combinations of its practical weights and slopes, not every face in the upstream package:

```text
Regular
Semibold
Bold
Italic
Semibold Italic
Bold Italic
```

They are packaged into one TrueType Collection (TTC), so macOS installs one file while exposing all six faces. A TTC reduces file count; it does not promise a proportional byte-size reduction because fonts only share data where their tables allow it.

For those faces, the build plan matches official `Iosevka Term SS17` settings and adds only the slab-serif configuration. The narrowed output scope is intentional.

## Source and toolchain

The Iosevka source is fixed at `v34.7.0` / `6828cb0bd569992bb19565a5e448540de3b50541`.

The builder uses the current `node:22-bookworm-slim` image and Debian Bookworm's `ttfautohint`; those toolchain packages are intentionally not version-pinned. It records the pinned source commit date, installs dependencies without lifecycle scripts, then builds offline with at most two Iosevka jobs by default.

This makes the source traceable, but does not claim byte-for-byte identical output across future toolchain updates. In particular, Iosevka's TTC assembly may rewrite internal OpenType timestamps. CI verifies the generated TTC's intended contents and metrics on every build.

## Build

GitHub Actions is the only build path. It checks out the exact upstream source commit, builds the TTC in Docker, verifies it, and uploads a CI artifact on relevant pushes and pull requests.

There is intentionally no supported local build command. Download the workflow artifact to test a candidate build, or use a versioned GitHub Release for durable installation.

## Outputs

```text
dist/iosevka-term-slab-ss17/
├── IosevkaTermSlabSS17.ttc
└── BUILD-INFO.json

dist/releases/IosevkaTermSlabSS17-34.7.0.zip
```

The verifier parses the build and collection plans, checks that the TTC has exactly the six intended faces, validates name metadata and required OpenType tables, checks all printable ASCII and selected terminal-symbol advances, and writes SHA-256 provenance to `BUILD-INFO.json`.

## Install on macOS

Download `IosevkaTermSlabSS17-34.7.0.zip` from a successful CI artifact or GitHub Release, extract it, then use this module's installer to copy the single TTC into the per-user font directory:

```bash
fonts/iosevka-term-slab-ss17/install.sh IosevkaTermSlabSS17.ttc
```

The installed file is:

```text
~/Library/Fonts/IosevkaTermSlabSS17.ttc
```

Quit and reopen Kitty after installing or replacing the file.

### Kitty

Use the family normally and let Kitty select the standard linked faces:

```conf
font_family Iosevka Term Slab SS17
bold_font auto
italic_font auto
bold_italic_font auto
```

The collection also provides `Semibold` and `Semibold Italic`. To use Semibold as Kitty's bold weight instead of Bold, set:

```conf
bold_font Iosevka Term Slab SS17 Semibold
bold_italic_font Iosevka Term Slab SS17 Semibold Italic
```

## License

The font is licensed under the SIL Open Font License 1.1. See [`OFL.txt`](OFL.txt). The repository's build orchestration is MIT licensed.
