from __future__ import annotations

import re

class RemoteDef:
    # REMOTE_PATTERN = re.compile(re.escape(r'      ([^:]+):(.*)'))
    # REMOTE_PATTERN = re.compile(re.escape(r'([^:]+):(.*)'))
    # REMOTE_PATTERN = re.compile(re.escape(r'([^:]+)'))
    REMOTE_PATTERN = re.compile(r'([^:]+)')
    TAG_PATTERN = re.compile(r'( +)([^:]+):(.*)$')
    PUSH_PATTERN = re.compile(r'( +)push:(.*)$')
    FETCH_PATTERN = re.compile(r'( +)fetch:(.*)$')
    OTHER_PATTERN = re.compile(r'( +)([^:]+):(.*)$')

    def __init__(self, name: str):
        self.name = name
        self.array = []

    def to_yaml(self) -> str:
      assoc = { self.name: {} }
      for child in self.array:
        assoc[self.name][child.name] = child.value
      return assoc[self.name]

    def add_child(self, child: RemoteDef.Item):
      # print(f'RemoteDef.add_child |child={child}|')
      self.array.append(child)

    def to_dict(self) -> dict:
        # YAMLへ安全に出せるよう、標準型(dict/str)のみへ落とす
        children: dict[str, str] = {}
        for child in self.array:
            # child は通常 RemoteDef.Item で、fetch/push を想定
            key = getattr(child, "name", None)
            val = getattr(child, "value", None)
            if key is None:
                continue
            children[str(key)] = "" if val is None else str(val)

        return {str(self.name): children}

    def __repr__(self):
        return f"RemoteDef(name={self.name}, array={len(self.array)})"

    @classmethod
    def rex(cls) -> re.Pattern:
        return cls.REMOTE_PATTERN

    @classmethod
    def retag(cls) -> re.Pattern:
        return cls.TAG_PATTERN

    class Item:
        @classmethod
        def create_root(cls) -> "RemoteDef.Item":
            item = cls(-1, "_root", 'root', '')
            item.kind = 'root'
            return item

        def __init__(self, len_space: int, name: str,value: str, text: str):
            self.len_space = len_space
            self.name = name
            self.kind = name if name == 'fetch' or name == 'push' or name == '_none' else 'other'
            if self.kind == 'other':
                self.value = ''
            else:
                self.value = value
            self.text = text
            self.children = []
            self.parent = None

        def __repr__(self):
            return f"Item(len_space={self.len_space}, name={self.name}, kind={self.kind}, value={self.value}, text={self.text},children={len(self.children)}, parent={self.parent})"

        def add_child(self, child: RemoteDef.Item):
            # print(f'Item.add_child |self.name={self.name}| child.name={child.name}|')
            # raise ValueError(f"Item.add_child |self.name={self.name}| child.name={child.name}|")
            self.children.append(child)
            child.parent = self

