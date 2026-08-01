# Formulae

This directory contains Homebrew formulae for released non-font command-line tools. Do not add a placeholder formula: a formula belongs here only when its package and immutable, versioned source or release archive exist.

Each formula must:

- use a filename and Ruby class name that match its formula name;
- not reuse a cask name or shadow a formula in `homebrew/core`;
- declare the archive SHA-256 and install its executable into `bin`; and
- have package-owned build, release, verification, and `brew style` / `brew audit --formula` checks.

Fonts remain Casks in [`../Casks`](../Casks).
