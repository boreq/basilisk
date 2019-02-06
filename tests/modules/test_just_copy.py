from basilisk.modules.just_copy import JustCopyModule
from basilisk.build import Build


def test_execute(builder):
    module = JustCopyModule()
    module.builder = builder
    build = Build(None, None)
    module.execute(build)
