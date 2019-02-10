from basilisk.modules.copy import CopyModule
from basilisk.build import Build


def test_execute(builder):
    module = CopyModule()
    module.builder = builder
    build = Build(None, None)
    module.execute(build)
