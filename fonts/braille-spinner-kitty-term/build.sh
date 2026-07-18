#!/usr/bin/env bash
set -euo pipefail

MODULE_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$MODULE_DIR/../.." && pwd)

uv run "$MODULE_DIR/build.py" --repo-root "$REPO_ROOT"
