from colcon_core.verb.test import TestVerb

class TestIsolatedVerb(TestVerb):
    def __init__(self):
        super().__init__()

    def main(self, *, context):
        print("Hello world")
        super().main(context=context)
