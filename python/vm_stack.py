class Stack(list):

    def __init__(self):
        list.__init__(self)

    def append(self, value):
        value_ = value % 2**16
        if value_ >= 2**15 + 8:
            raise ValueError
        list.append(self, value_)

    def pop(self):
        return list.pop(self)
