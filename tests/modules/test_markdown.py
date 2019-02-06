from basilisk.modules.markdown import MarkdownModule
from basilisk.build import Build


markdown = """
# Header

Text.
"""


def test_add_processor():
    module = MarkdownModule()
    build = Build(None, None)
    assert len(build.processors) == 0
    module.execute(build)
    assert len(build.processors) == 1


def test_processor():
    module = MarkdownModule()
    processor = module.make_processor()
    result = processor(markdown)
    assert '<h1>' in result
