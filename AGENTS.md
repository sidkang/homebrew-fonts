# Repository scope

This repository is the Homebrew tap for font releases from `sidkang/fonts`.

- Font casks belong in `Casks/`.
- Cask names MUST start with `font-`.
- Release URLs MUST reference immutable versioned GitHub release assets.
- SHA-256 checksums MUST be generated from the published asset.
- Test changes with `brew style` and `brew audit --cask` before publishing.
- Use Jujutsu and publish through the `master` bookmark.
