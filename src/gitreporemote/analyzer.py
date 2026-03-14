from __future__ import annotations

import inspect
import re
from typing import Any, Dict

from .remotedef import RemoteDef
from .repodef import RepoDef


class Analyzer:
    def analyze_basic(self, text: Any) -> Any:
        word_repo_count = "repo_count:"
        obj_array = text.split(word_repo_count)

        base_dir = obj_array.pop(0)
        base_dir_after = word_repo_count + obj_array[0]
        word_repos = "repos:"
        array_repos = base_dir_after.split(word_repos)
        repo_count = array_repos.pop(0)
        repo_count_after = array_repos[0]
        return [base_dir, repo_count, repo_count_after]

    def analyze_item(self, text: str) -> RemoteDef.Item:
        rex = RemoteDef.retag()
        match = rex.match(text)
        if match:
            space = match.group(1)
            len_space = len(space)
            name = match.group(2)
            value = match.group(3)
            text = ""
            if name == "fetch" or name == "push":
                value_array = value.split("  ", maxsplit=1)
                value = value_array[0]
                if len(value_array) > 1:
                    text = "  " + value_array[1]
                else:
                    text = ""
            else:
                text = value
                value = ""

            _line_no = inspect.currentframe().f_lineno
            item = RemoteDef.Item(len_space, name, value, text)
            return item

        raise ValueError(f"analyze_item |not match ({text})")

    def analyze_remote(self, text: str) -> Any:
        results = []
        word_remotes = "    remotes:"
        array_remotes = text.split(word_remotes)
        before_text = ""
        if len(array_remotes) > 1:
            before_text0 = array_remotes.pop(0)
            before_text = re.sub(r'"', "", before_text0)

        remotes_after = array_remotes[0]
        text = remotes_after
        while len(text.strip()) > 0:
            item = self.analyze_item(text)
            if item is not None:
                results.append(item)
                text = item.text
            else:
                item = RemoteDef.Item(-1, "_none", "", text)
                results.append(item)
                break

        return [before_text, results]

    def analyze_repo(self, text: str) -> Any:
        repos = []
        word_path = "  - path:"
        array_path = text.split(word_path)
        if len(array_path) > 1:
            array_path.pop(0)
        for path in array_path:
            [before_text, items] = self.analyze_remote(path)
            path = before_text
            repo = RepoDef(path)
            item_root = RemoteDef.Item.create_root()
            item_remote = None
            for item in items:
                if item.kind == "push":
                    item_remote.add_child(item)
                elif item.kind == "fetch":
                    item_remote.add_child(item)
                elif item.kind == "other":
                    item_root.add_child(item)
                    item_remote = item
                else:
                    raise ValueError(f"unknown kind ({item.kind}) of item")

            for item in item_root.children:
                remote = RemoteDef(item.name)
                for child in item.children:
                    remote.add_child(child)
                repo.add_remote(remote)
            repos.append(repo)

        return repos

    def analyze(self, text: str) -> Dict[str, Any]:
        basic = self.analyze_basic(text)
        repo_count_after = basic[2]

        word_repos = "repos:"
        repo_array = repo_count_after.split(word_repos)
        if len(repo_array) > 1:
            repo_array.pop(0)

        repos_after = repo_array[0]
        array8 = self.analyze_repo(repos_after)
        assoc = {}
        assoc["base_dir"] = basic[0]
        assoc["repo_count"] = basic[1]
        assoc["repos"] = array8
        return assoc


