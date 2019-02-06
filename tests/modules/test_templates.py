from basilisk.modules.templates import TemplatesModule
from basilisk.build import Build


def test_add_processor(builder):
    module = TemplatesModule()
    module.builder = builder
    build = Build(None, None)
    assert len(build.processors) == 0
    module.execute(build)
    assert len(build.processors) == 1


def test_directory_default(builder):
    module = TemplatesModule()
    module.builder = builder
    directory = module.get_templates_dir()
    assert directory == 'source_directory/_templates'


def test_directory_custom(builder):
    builder.config['module_config']['templates'] = {
        'templates_directory': 'custom_directory'
    }
    module = TemplatesModule()
    module.builder = builder
    directory = module.get_templates_dir()
    assert directory == 'source_directory/custom_directory'
