class Memory(dict):

    def __init__(self, data, _):
        dict.__init__(self)
        self._ = _
        for i, value in enumerate(data):
            self[i] = value

    def __getitem__(self, key):
        return self._(self.get_raw(key))

    def __setitem__(self, key, value):
        if key >= 2**15:
            raise IndexError
        value_ = value % 2**16
        if value_ >= 2**15 + 8:
            raise ValueError
        dict.__setitem__(self, key, value_)

    def get_raw(self, key):
        if key >= 2**15:
            raise IndexError
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return 0

