from .remotedef import RemoteDef

class RepoDef:
    def __init__(self, path: str):
        self.path = path
        self.remotes = []

    def add_remote(self, remote: RemoteDef):
        # print(f'RepoDef.add_remote |remote={remote}|')
        self.remotes.append(remote)

    def to_dict(self) -> dict:
        # YAMLへ安全に出せるよう、標準型(dict/list/str)のみへ落とす
        remotes: dict[str, dict[str, str]] = {}
        for remote in self.remotes:
            remotes.update(remote.to_dict())

        return {"path": self.path, "remotes": remotes}

    def to_yaml(self) -> str:
      assoc = {'path': self.path}
      assoc['remotes'] = {}
      for remote in self.remotes:
        assoc['remotes'][remote.name] = remote.to_yaml()
      return assoc
