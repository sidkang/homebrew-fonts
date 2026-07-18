# Fonts

Personal font source, verified GitHub releases, and Homebrew casks in one repository. The tap remains available as `sidkang/fonts` because Homebrew maps that name to this `homebrew-fonts` repository. User-visible release changes are recorded in [`CHANGELOG.md`](CHANGELOG.md).

## Install

Install a released font directly:

```bash
brew install --cask sidkang/fonts/font-braille-spinner-kitty-term
```

Or add the tap first:

```bash
brew tap sidkang/fonts
brew install --cask font-braille-spinner-kitty-term
```

## Available casks

| Cask | Font |
| --- | --- |
| `font-braille-spinner-kitty-term` | Braille Spinner Kitty Term |
| `font-iosevka-term-slab-ss17` | Iosevka Term Slab SS17 |

## Builds and releases

GitHub Actions is the only supported build path. Each font module owns its build implementation, verifier, installer for downloaded artifacts, font license, and documentation.

A version tag is the release signal. Pushing one automatically builds, verifies, creates the GitHub Release, computes the asset SHA-256, and updates the matching cask:

```text
braille-spinner-kitty-term-v1.0.2
iosevka-term-slab-ss17-v34.7.1
```

Normal pushes to `master` only verify; they do not release. A cask always points at an immutable release asset, never an ephemeral CI artifact.

## Repository layout

```text
Casks/                  # Homebrew casks
fonts/<module>/
├── README.md           # font use and installation documentation
├── OFL.txt             # font license
├── build.sh            # internal CI build entry point
├── install.sh          # installs an already-built release artifact
├── verify.py|build.py  # build and verification implementation
└── toolchain/          # optional build environment

.github/workflows/      # module-specific verification and release workflows
LICENSE                 # MIT for repository code and configuration
```

## Licenses

Repository code and configuration are licensed under the [MIT License](LICENSE). Each font is licensed separately under the SIL Open Font License 1.1; see its module's `OFL.txt`.
