# Analyzer — 外部仕様書

**モジュール:** `gitreporemote.analyzer`

## 概要

YAML レポートのテキストをパースし、`RepoDef` / `RemoteDef` オブジェクトのツリーに変換するクラス。
**YAML ライブラリを使用せず、文字列分割によるオーダー依存パーサーとして実装されている。**

現時点では CLI エントリポイントには接続されておらず、プログラムから直接呼び出す用途を想定している。

---

## クラス: `Analyzer`

コンストラクタは不要（引数なし、インスタンス変数なし）。

---

### メソッド

#### `analyze(text: str) -> dict`

**最上位メソッド。** YAML テキスト全体を受け取り、解析済み辞書を返す。

**引数:**

| 引数 | 型 | 説明 |
|------|----|------|
| `text` | `str` | YAML レポートのテキスト全体 |

**戻り値:**

```python
{
    "base_dir":   "<スキャン基底ディレクトリのテキスト>",
    "repo_count": "<repo_count の値テキスト>",
    "repos":      [RepoDef, ...]
}
```

**処理フロー:**

```
text
 └─ analyze_basic()  → [base_dir, repo_count, repo_count_after]
      └─ analyze_repo(repos_after)  → [RepoDef, ...]
           └─ analyze_remote(path_text)  → [before_text, [Item, ...]]
                └─ analyze_item(line_text)  → RemoteDef.Item
```

---

#### `analyze_basic(text: str) -> list`

テキストを `repo_count:` で分割し、`base_dir`・`repo_count`・後続テキストを抽出する。

**戻り値:** `[base_dir_text, repo_count_text, repos_section_text]`

---

#### `analyze_repo(text: str) -> list[RepoDef]`

`  - path:` マーカーでテキストを分割し、各リポジトリブロックを `RepoDef` に変換する。

- 各ブロックを `analyze_remote()` に渡してアイテムリストを取得する。
- `Item.create_root()` を起点にツリーを構築する。
  - `kind == "other"` → ルートに追加（リモート名ノード）
  - `kind == "fetch"` / `"push"` → 直前の `"other"` ノードに追加
- ツリーを走査して `RemoteDef` を生成し `RepoDef` に追加する。

**戻り値:** `list[RepoDef]`

---

#### `analyze_remote(text: str) -> list`

`    remotes:` マーカーでテキストを分割し、残余テキストから `Item` のリストを順次生成する。

- `before_text` からダブルクォートを除去してリポジトリ・パスとする。
- `analyze_item()` を繰り返し呼び出して `Item` を取り出す（各 `Item.text` が次の入力）。

**戻り値:** `[path_text, [RemoteDef.Item, ...]]`

---

#### `analyze_item(text: str) -> RemoteDef.Item`

`TAG_PATTERN`（`RemoteDef.retag()`）で1行をマッチし、`RemoteDef.Item` を生成する。

| 条件 | `value` | `text`（残余） |
|------|---------|----------------|
| `name == "fetch"` または `"push"` | URL（`"  "` 前まで） | `"  "` 以降の残余テキスト |
| それ以外（リモート名） | `""` | マッチした value テキスト |

マッチしない場合は `ValueError` を送出する。

---

## 入力フォーマット（期待する YAML テキスト構造）

```yaml
base_dir: /some/path
repo_count: 2
repos:
  - path: /some/path/repo1
    remotes:
      origin:
        fetch: git@github.com:user/repo1.git
        push: git@github.com:user/repo1.git
  - path: /some/path/repo2
    remotes:
      origin:
        fetch: git@github.com:user/repo2.git
        push: git@github.com:user/repo2.git
```

---

## 依存関係

| 依存先 | 用途 |
|--------|------|
| `RemoteDef` | `Item` 生成・正規表現パターン取得 |
| `RepoDef` | リポジトリ情報の格納 |

---

## 使用例

```python
from pathlib import Path
from gitreporemote.analyzer import Analyzer

text = Path("report.yaml").read_text(encoding="utf-8")
analyzer = Analyzer()
result = analyzer.analyze(text)

print(result["base_dir"])
print(result["repo_count"])
for repo in result["repos"]:
    print(repo.to_dict())
```

---

## 制約・注意事項

- マーカー文字列（`repo_count:`, `repos:`, `  - path:`, `    remotes:`）の順序と空白に依存する。
- YAML ライブラリを使わないため、値にマーカー文字列が含まれる場合は誤動作する可能性がある。
- CLI エントリポイントには未接続。`gitrepoanalyze` コマンドは `yaml.safe_load()` + `to_dict()` を使用し、このクラスを経由しない。
