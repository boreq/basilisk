from basilisk.modules.templates import TemplatesModule
from basilisk.build import Build


def test_add_processor(builder):
    module = TemplatesModule(builder)
    build = Build(None, None)
    assert len(build.processors) == 0
    module.execute(build, None)
    assert len(build.processors) == 1


def test_directory_default(builder):
    module = TemplatesModule(builder)

    directory = module.get_templates_dir(None)
    assert directory == 'source_directory/_templates'

    directory = module.get_templates_dir({})
    assert directory == 'source_directory/_templates'


def test_directory_custom(builder):
    module_config = {
        'templates_directory': 'custom_directory'
    }
    module = TemplatesModule(builder)
    directory = module.get_templates_dir(module_config)
    assert directory == 'source_directory/custom_directory'
