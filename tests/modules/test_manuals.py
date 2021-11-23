import pytest
from basilisk.modules.manuals import ManualsModule
from basilisk.build import Build


def test_add_processor_missing_config(builder):
    module = ManualsModule(builder)
    build = Build(None, None)
    assert len(build.processors) == 0
    with pytest.raises(KeyError):
        module.execute(build, None)


def test_add_processor(builder):
    module_config = {
            'macros': {
                'man': [
                    '*'
                ]
            }
    }
    module = ManualsModule(builder)
    build = Build('input_path', 'output_path')
    assert len(build.processors) == 0
    module.execute(build, module_config)
    assert len(build.processors) == 1
