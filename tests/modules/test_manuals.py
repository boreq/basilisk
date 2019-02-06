import pytest
from basilisk.modules.manuals import ManualsModule
from basilisk.build import Build


def test_add_processor_missing_config(builder):
    module = ManualsModule()
    module.builder = builder
    build = Build(None, None)
    assert len(build.processors) == 0
    with pytest.raises(KeyError):
        module.execute(build)


def test_add_processor(builder):
    builder.config['module_config']['manuals'] = {
            'macros': {
                'man': [
                    '*'
                ]
            }
    }
    module = ManualsModule()
    module.builder = builder
    build = Build('input_path', 'output_path')
    assert len(build.processors) == 0
    module.execute(build)
    assert len(build.processors) == 1
