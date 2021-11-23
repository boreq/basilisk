import pytest
from basilisk.modules.exec_with import ExecWithModule
from basilisk.build import Build


def test_execute_no_mapping(builder):
    module = ExecWithModule(builder)
    build = Build('input_path/script.py', 'output_path/script.html')
    with pytest.raises(KeyError):
        module.execute(build)


def test_execute(builder):
    builder.config['module_config']['exec_with'] = {
            'mapping': {
                '*.py': 'python %s'
            }
    }
    module = ExecWithModule(builder)
    build = Build('input_path/script.py', 'output_path/script.html')
    module.execute(build)
