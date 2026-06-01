# RemoteDef — 外部仕様書

**モジュール:** `gitreporemote.remotedef`

## 概要

1つのリモート定義（名前 + fetch/push URL の組）を保持するクラス。
`git remote -v` の出力から `Analyzer` が組み立て、`RepoDef` が管理する。
内部ツリー構造を扱う `Item` ネスト・クラスを持つ。

---

## クラス: `RemoteDef`

### コンストラクタ

```python
RemoteDef(name: str)
```

| 引数 | 型 | 説明 |
|------|----|------|
| `name` | `str` | リモート名（例: `"origin"`） |

#### 初期状態

| 属性 | 型 | 初期値 | 説明 |
|------|----|--------|------|
| `name` | `str` | 引数の値 | リモート名 |
| `array` | `list[RemoteDef.Item]` | `[]` | 子 `Item`（fetch/push）のリスト |

---

### メソッド

#### `add_child(child: RemoteDef.Item) -> None`

子 `Item` を `array` に追加する。

| 引数 | 型 | 説明 |
|------|----|------|
| `child` | `RemoteDef.Item` | 追加する Item（通常 fetch または push） |

---

#### `to_dict() -> dict`

YAML 出力用の標準型辞書を返す。

**戻り値:**

```python
{
    "<name>": {
        "fetch": "<url>",   # fetch Item が存在する場合
        "push":  "<url>"    # push Item が存在する場合
    }
}
```

- `Item.name` がキー、`Item.value` が値。
- `value` が `None` の場合は `""` に変換（`name` が `None` の場合はスキップ）。

---

#### `to_yaml() -> dict`

`to_dict()` と同等だが、内部実装が異なる旧形式メソッド。
`{name: {child.name: child.value, ...}}` の内側辞書を返す。

---

#### `rex() -> re.Pattern` *(classmethod)*

`REMOTE_PATTERN`（`r'([^:]+)'`）を返す。

#### `retag() -> re.Pattern` *(classmethod)*

`TAG_PATTERN`（`r'( +)([^:]+):(.*)$'`）を返す。`Analyzer` が使用。

---

### クラス変数（正規表現）

| 変数名 | パターン | 用途 |
|--------|----------|------|
| `REMOTE_PATTERN` | `r'([^:]+)'` | リモート名抽出 |
| `TAG_PATTERN` | `r'( +)([^:]+):(.*)$'` | インデント付きキー: 値行の解析 |
| `PUSH_PATTERN` | `r'( +)push:(.*)$'` | push 行の解析（未使用） |
| `FETCH_PATTERN` | `r'( +)fetch:(.*)$'` | fetch 行の解析（未使用） |
| `OTHER_PATTERN` | `r'( +)([^:]+):(.*)$'` | その他行の解析（未使用） |

---

## ネスト・クラス: `RemoteDef.Item`

YAML テキストの1行を表すツリーノード。

### コンストラクタ

```python
RemoteDef.Item(len_space: int, name: str, value: str, text: str)
```

| 引数 | 型 | 説明 |
|------|----|------|
| `len_space` | `int` | 先頭スペース数（インデント深さ） |
| `name` | `str` | キー名（`"fetch"` / `"push"` / リモート名） |
| `value` | `str` | キーに対応する値（URL など） |
| `text` | `str` | 残余テキスト（次行以降の解析用） |

#### 初期状態

| 属性 | 型 | 説明 |
|------|----|------|
| `len_space` | `int` | インデント長 |
| `name` | `str` | キー名 |
| `kind` | `str` | `"fetch"` / `"push"` / `"other"` / `"root"` |
| `value` | `str` | `kind` が `fetch` / `push` のとき URL、それ以外は `""` |
| `text` | `str` | 残余テキスト |
| `children` | `list[RemoteDef.Item]` | 子ノード |
| `parent` | `RemoteDef.Item \| None` | 親ノード |

**`kind` の決定ルール:**
- `name == "fetch"` → `kind = "fetch"`
- `name == "push"` → `kind = "push"`
- `name == "_none"` → `kind = "other"` (暫定)
- それ以外 → `kind = "other"`（リモート名ノード）

---

### メソッド

#### `create_root() -> RemoteDef.Item` *(classmethod)*

`len_space=-1, name="_root", kind="root"` の合成ルートノードを生成して返す。
`Analyzer.analyze_repo()` 内でツリー構築の起点として使用。

---

#### `add_child(child: RemoteDef.Item) -> None`

子ノードを追加し、`child.parent` を自身に設定する。

---

## 使用例

```python
from gitreporemote.remotedef import RemoteDef

remote = RemoteDef("origin")
fetch_item = RemoteDef.Item(6, "fetch", "git@github.com:user/repo.git", "")
push_item  = RemoteDef.Item(6, "push",  "git@github.com:user/repo.git", "")
remote.add_child(fetch_item)
remote.add_child(push_item)

print(remote.to_dict())
# {'origin': {'fetch': 'git@github.com:user/repo.git',
#             'push':  'git@github.com:user/repo.git'}}
```
