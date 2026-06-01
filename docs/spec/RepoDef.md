# RepoDef — 外部仕様書

**モジュール:** `gitreporemote.repodef`

## 概要

1つの Git リポジトリを表すデータクラス。
リポジトリのパスと、そのリポジトリが持つリモート定義（`RemoteDef`）のリストを保持する。
`Analyzer` が生成し、`to_dict()` で YAML 出力用の標準型辞書に変換する。

---

## クラス: `RepoDef`

### コンストラクタ

```python
RepoDef(path: str)
```

| 引数 | 型 | 説明 |
|------|----|------|
| `path` | `str` | リポジトリのルート・パス |

#### 初期状態

| 属性 | 型 | 初期値 | 説明 |
|------|----|--------|------|
| `path` | `str` | 引数の値 | リポジトリ・パス |
| `remotes` | `list[RemoteDef]` | `[]` | リモート定義のリスト |

---

### メソッド

#### `add_remote(remote: RemoteDef) -> None`

`RemoteDef` インスタンスを `remotes` に追加する。

| 引数 | 型 | 説明 |
|------|----|------|
| `remote` | `RemoteDef` | 追加するリモート定義 |

---

#### `to_dict() -> dict`

YAML 出力用の標準型辞書を返す。

**戻り値:**

```python
{
    "path": "<リポジトリ・パス>",
    "remotes": {
        "<remote_name>": {
            "fetch": "<url>",
            "push":  "<url>"
        },
        ...
    }
}
```

- 各 `RemoteDef.to_dict()` の結果を `remotes` に `update` でマージする。

---

#### `to_yaml() -> dict`

`to_dict()` と同等だが、内部実装が異なる旧形式メソッド（※実装の型注釈は `-> str` だが、実際には同じ構造の辞書を返す）。
同じ構造の辞書を返す。

---

## 依存関係

| 依存先 | 用途 |
|--------|------|
| `RemoteDef` | リモート定義の保持・`to_dict()` 委譲 |

---

## 使用例

```python
from gitreporemote.repodef import RepoDef
from gitreporemote.remotedef import RemoteDef

repo = RepoDef("/home/user/projects/myrepo")

remote = RemoteDef("origin")
remote.add_child(RemoteDef.Item(6, "fetch", "git@github.com:user/repo.git", ""))
remote.add_child(RemoteDef.Item(6, "push",  "git@github.com:user/repo.git", ""))
repo.add_remote(remote)

print(repo.to_dict())
# {
#   'path': '/home/user/projects/myrepo',
#   'remotes': {
#     'origin': {
#       'fetch': 'git@github.com:user/repo.git',
#       'push':  'git@github.com:user/repo.git'
#     }
#   }
# }
```
