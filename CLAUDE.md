# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`gitreporemote` is a CLI tool that recursively scans a directory tree for Git repositories, collects remote URL information from each via `git remote -v`, and outputs the results as YAML. It also includes utilities for parsing and re-serializing those YAML reports.

## Environment

- Python 3.14 (see `.python-version`)
- Dependency manager: `uv`
- Local dependency: `yklibpy` at `../yklibpy` (a sibling directory)
- `ruff` は通常依存（dev ではない）として `pyproject.toml` に含まれる
- `mypy` は `pyproject.toml` に含まれない。必要なら `uv add --dev mypy` で追加

## Commands

```bash
# Install dependencies
uv sync

# Run the main scanner (scans <base_dir>, writes report.yaml)
uv run gitrepo -d <base_dir> -o report.yaml

# Re-serialize a YAML report through to_dict() normalizer
uv run gitrepoanalyze <input.yaml> -o output.yaml

# Load and display a YAML file (uses yklibpy.common.util_yaml)
uv run grr_load_yaml <file.yaml>

# Lint
uv run ruff check ./src

# Type check (mypy を追加済みの場合)
uv run mypy ./src

# Run tests (tests/ ディレクトリは未作成)
uv run pytest
```

## Architecture

### Entry Points (`pyproject.toml` `[project.scripts]`)

スクリプトは `gitreporemote:<func>` 形式で `__init__.py` から公開される。

| Command | Module function | What it does |
|---|---|---|
| `gitrepo` | `main.mainx()` | Scan dirs, write YAML report |
| `gitrepoanalyze` | `main.main_analyze()` | Load YAML → `to_dict()` → write YAML |
| `grr_load_yaml` | `x.load_yaml_main()` | Load YAML via yklibpy and return |
| `xt2`, `xt3` | `main.xt2/xt3()` | Dev stubs that produce hard-coded sample data |

### Module Roles

- **`main.py`** — All core scanning logic: `find_git_dirs()` walks the filesystem (pruning `.git` dirs to avoid recursing into them), `run_git_remote_v()` shells out to `git remote -v`, `parse_remote_v()` parses output into `{name: {fetch: url, push: url}}`. `build_report()` assembles the full dict. `to_dict()` recursively normalizes any object to YAML-safe standard types (delegates to `.to_dict()` if the object has one, falls back to `__dict__`, coerces to `str` as last resort).
- **`analyzer.py` / `Analyzer`** — Text-based parser for YAML report files. Splits raw YAML text by string markers (`repo_count:`, `repos:`, `  - path:`, `    remotes:`) without using a YAML library. Produces `RepoDef` objects. **Not wired to any CLI entry point** — available for programmatic use only.
- **`repodef.py` / `RepoDef`** — Data class: one repository path + list of `RemoteDef`. `to_dict()` returns `{"path": ..., "remotes": {name: {fetch: url, push: url}}}`.
- **`remotedef.py` / `RemoteDef` + `RemoteDef.Item`** — `RemoteDef` holds a remote name and child `Item`s. `Item` is a tree node with `kind` ∈ `{fetch, push, other, root}`: `other` = remote name node, `fetch`/`push` = URL leaf nodes, `root` = synthetic tree root created by `Item.create_root()`.
- **`x.py`** — Thin wrapper around `yklibpy.common.util_yaml.UtilYaml.load_yaml()`.
- **`filex.py` / `Filex`** — File writer that mirrors writes to stdout. Not used by current entry points.

### Data Flow

```
filesystem
   └─ find_git_dirs() ─► repo roots
         └─ git -C <root> remote -v  ─► parse_remote_v()
               └─ build_report() ─► write_yaml() ─► report.yaml

# gitrepoanalyze path (does NOT use Analyzer):
report.yaml ─► yaml.safe_load() ─► to_dict() ─► write_yaml() ─► output.yaml

# Analyzer path (programmatic only):
report.yaml text ─► Analyzer.analyze() ─► {base_dir, repo_count, repos:[RepoDef,...]}
```

### Output / Input Directories

- `_input/` and `_output/` are gitignored scratch directories for I/O files.
- `dist/` holds build artifacts.
