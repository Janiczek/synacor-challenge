class Registers(dict):

    def __init__(self, *args):
        dict.__init__(self, args)

    def __getitem__(self, key):
        if key >= 8:
            raise IndexError
        try:
            return dict.__getitem__(self, key) 
        except KeyError:
            return 0

    def __setitem__(self, key, value):
        if key >= 8:
            raise IndexError
        value_ = value % 2**16
        if value_ >= 2**15 + 8:
            raise ValueError
        dict.__setitem__(self, key, value_)
