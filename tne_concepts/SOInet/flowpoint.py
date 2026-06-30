class Flowpoint:
    def __init__(self, f):
        self.orig_type = type(f)
        if isinstance(f, bool):
            self.state = (f, not f)
        elif isinstance(f, (int, float, complex)):
            self.state = (f, -f)
        else:
            raise TypeError(f"Unsupported type for flowpoint: {type(f)}")

    def __next__(self):
        val = self.state[0]
        self.state = (self.state[1], self.state[0])
        return val

    def __iter__(self):
        return self
