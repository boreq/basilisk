from basilisk.modules.pretty_urls import PrettyUrlsModule
from basilisk.build import Build


test_parameters = [
        ['index.extension', 'index.extension'],
        ['index', 'index'],

        ['article.extension', 'article/index.extension'],
        ['article', 'article/index'],

        ['subdirectory/article.extension', 'subdirectory/article/index.extension'],
        ['subdirectory/article', 'subdirectory/article/index'],
]


def test_change_output_path(builder):
    module = PrettyUrlsModule(builder)
    for parameter in test_parameters:
        input_path = None
        output_path = parameter[0]
        changed_output_path = parameter[1]
        build = Build(input_path, output_path)
        module.execute(build)
        assert build.output_path == changed_output_path
