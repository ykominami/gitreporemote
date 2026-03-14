#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
from collections import defaultdict
from typing import Dict, List, Tuple, Any
# from bs4 import ResultSet
from pathlib import Path
import yaml


def to_dict(obj: Any) -> Any:
    """YAMLへ安全に保存できるよう、標準型(dict/list/str/int/float/bool/None)へ正規化する。

    独自クラスは to_dict() があればそれを利用し、再帰的に処理する。
    """
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, Path):
        return str(obj)

    if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
        return to_dict(obj.to_dict())

    if isinstance(obj, dict):
        # YAMLのキーは基本 str に寄せる
        return {str(k): to_dict(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [to_dict(item) for item in obj]

    if isinstance(obj, tuple):
        # tuple だと !!python/tuple になり得るので list に落とす
        return [to_dict(item) for item in obj]

    if isinstance(obj, set):
        return [to_dict(item) for item in obj]

    if hasattr(obj, "__dict__"):
        # 基本は to_dict() 実装を推奨。フォールバックは private を除外して落とす。
        return {str(k): to_dict(v) for k, v in obj.__dict__.items() if not str(k).startswith("_")}

    return str(obj)

def read_file(file: str) -> str:
    # 文字コードを固定（環境依存の事故を避ける）
    return Path(file).read_text(encoding="utf-8", errors="replace")

def write_yaml(path: Path, data: Any) -> None:
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

def run_git_remote_v(repo_root: str) -> Tuple[int, str, str]:
    """
    Run: git -C <repo_root> remote -v
    Returns (returncode, stdout, stderr)
    """
    try:
        p = subprocess.run(
            ["git", "-C", repo_root, "remote", "-v"],
            capture_output=True,
            text=True,
            check=False,
        )
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError as e:
        return 127, "", f"git not found: {e}"


def parse_remote_v(output: str) -> Dict[str, Dict[str, str]]:
    """
    Parse lines like:
      origin  git@github.com:user/repo.git (fetch)
      origin  git@github.com:user/repo.git (push)
    into:
      { "origin": { "fetch": "...", "push": "..." }, ... }
    """
    remotes: Dict[str, Dict[str, str]] = defaultdict(dict)
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        name, url, kind = parts[0], parts[1], parts[2]
        kind = kind.strip("()")  # fetch/push
        remotes[name][kind] = url
    return dict(remotes)


def find_git_dirs(base_dir: str) -> List[str]:
    """
    Find '.git' directories under base_dir.
    Returns list of repo roots (the parent dir that contains .git dir).
    """
    repo_roots: List[str] = []

    for root, dirs, files in os.walk(base_dir):
        if ".git" in dirs:
            repo_roots.append(root)
            # その配下は別リポジトリ扱いになることが多いので、
            # ここで .git 配下の探索を抑止（ただし子repoは拾うため、root配下は歩く）
            # os.walk は dirs を書き換えると枝刈りできる
            dirs.remove(".git")

    return repo_roots

def build_report(base_dir: str) -> Dict[str, Any]:
    base_dir = os.path.abspath(base_dir)

    repos = []
    for repo_root in sorted(set(find_git_dirs(base_dir))):
        # print(repo_root)
        rc, out, err = run_git_remote_v(repo_root)
        entry: Dict[str, Any] = {
            "path": repo_root,
        }

        if rc == 0:
            remotes = parse_remote_v(out)
            entry["remotes"] = remotes
        else:
            entry["error"] = {
                "returncode": rc,
                "message": err.strip() or "git command failed",
            }

        repos.append(entry)

    return {
        "base_dir": base_dir,
        "repo_count": len(repos),
        "repos": repos,
    }

def mainx() -> int:
    parser = argparse.ArgumentParser(
        description="Find .git directories under a directory, list remotes for each repo, and output YAML."
    )
    parser.add_argument("-d", "--dir", default=".", help="Base directory to scan")
    parser.add_argument("-o", "--out", default="report.yaml", help="Output YAML path")
    args = parser.parse_args()

    report = build_report(args.dir)
    write_yaml(Path(args.out), report)
    return 0

def main_analyze() -> int:
    parser = argparse.ArgumentParser(
        description="Find .git directories under a directory, list remotes for each repo, and output YAML."
    )
    parser.add_argument("file", help="input file")
    parser.add_argument("-o", "--out", default="report_out.yaml", help="Output YAML path")
    args = parser.parse_args()

    # YAMLとして読み、標準型へ正規化して保存し直す
    text = read_file(args.file)
    assoc = yaml.safe_load(text)
    assoc_plain = to_dict(assoc)
    write_yaml(Path(args.out), assoc_plain)
    return 0

def xt():
    assoc = {}
    assoc['path'] = "/a/b/c"
    assoc['remotes'] = {}
    assoc['remotes']['origin'] = {}
    assoc['remotes']['origin']['fetch'] = "git@github.com:user/repo.git"
    assoc['remotes']['origin']['push'] = "git@github.com:user/repo.git"
    return assoc

def xtb():
    assoc = {}
    assoc['path'] = "/d/e/f"
    assoc['remotes'] = {}
    assoc['remotes']['origin'] = {}
    assoc['remotes']['origin']['fetch'] = "git@github.com:user2/repo.git"
    assoc['remotes']['origin']['push'] = "git@github.com:user2/repo.git"
    return assoc

def xt2():
    array = []
    assoc = xt()
    assoc2 = xtb()
    array.append(assoc)
    array.append(assoc2)
    print(f'array={array}|')
    return array

def xt3():
    array = xt2()
    yaml_str = yaml.dump(array, default_flow_style=True)
    print(f'yaml_str={yaml_str}|')
    return yaml_str

if __name__ == "__main__":
    raise SystemExit(mainx())
