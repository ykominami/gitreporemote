class Filex:
    def __init__(self, path: str):
        self.path = path
        self.f = open(path, "w")

    def print(self, data: str):
        self.f.write(data)
        print(data)

    def close(self):
        self.f.close()

