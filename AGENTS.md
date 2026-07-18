# Repository scope

This repository is the source, release, and Homebrew tap for personal fonts.

## Layout

- Font modules live in `fonts/<font-slug>/` and own their build implementation, verification, installer, public documentation, and font license.
- Homebrew casks live in `Casks/` and their names MUST start with `font-`.
- Root documentation and workflows apply across modules. Do not add root build/install dispatchers or a central module registry.

## Build and release

- GitHub Actions is the supported build path. Generated files belong under `dist/` and MUST NOT be committed.
- Use `uv` and inline Python script metadata; do not add a repository-wide virtual environment.
- Every build MUST verify family names, codepoints, advances, and font validity before packaging.
- Release archives MUST include the font file, its module README, and its font license.
- Casks MUST reference immutable versioned GitHub release assets in this repository. Generate their SHA-256 from the published asset.
- Test cask changes with `brew style` and `brew audit --cask` before publishing.

## Licenses

- Repository code and configuration use the root MIT `LICENSE`.
- Each font module must include its applicable font license, normally `OFL.txt`.

## Version control

- This is a Jujutsu repository. Use `jj`, not raw Git commands.
- Publish through the `master` bookmark.
