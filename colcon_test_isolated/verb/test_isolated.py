from colcon_core.plugin_system import satisfies_version
from colcon_core.verb import VerbExtensionPoint


class TestIsolatedVerb(VerbExtensionPoint):
    """Cleans package workspaces."""

    def __init__(self):  # noqa: D107
        super().__init__()

    def add_arguments(self, *, parser):
        pass

    def main(self, *, context):  # noqa: D102
        print("Hello world")
