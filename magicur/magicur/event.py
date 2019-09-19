'''
Eventing
'''


class MagicEvent:
    pass


class HookEvent(MagicEvent):

    def __init__(self, method, *args):
        self.method = method
        self.args = args


class KeyEvent(MagicEvent):

    def __init__(self, key):
        self.key = key
