import pytest
import subprocess
from basilisk.modules.scripting import ScriptingModule
from basilisk.build import Build


def test_no_config(builder):
    module = ScriptingModule(builder)
    module.process(None)


def test_command(builder):
    builder.config['module_config']['scripting'] = {
        'scripts': ['echo testing']
    }
    module = ScriptingModule(builder)
    module.process(None)


def test_invalid_command(builder):
    builder.config['module_config']['scripting'] = {
        'scripts': ['invalid command']
    }
    module = ScriptingModule(builder)
    with pytest.raises(subprocess.CalledProcessError):
        module.process(None)


def test_replacement(builder):
    text_in = 'command ${source_directory} ${output_directory}'
    text_out = 'command source_directory output_directory'

    module = ScriptingModule(builder)
    out = module.replace_placeholders(text_in)
    assert out == text_out
