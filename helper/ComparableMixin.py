# http://stackoverflow.com/questions/1061283/lt-instead-of-cmp


class ComparableMixin(object):
    def __eq__(self, other):
        return not self < other and not other < self

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return not other < self
