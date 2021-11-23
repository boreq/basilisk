from basilisk.modules.markdown import MarkdownModule
from basilisk.build import Build


markdown = b"""
# Header

Text.
"""


def test_add_processor(builder):
    module = MarkdownModule(builder)
    build = Build(None, 'some/path/file.md')
    assert len(build.processors) == 0
    module.execute(build, None)
    assert len(build.processors) == 1
    assert build.output_path == 'some/path/file.html'


def test_processor(builder):
    module = MarkdownModule(builder)
    processor = module.make_processor()
    result = processor(markdown)
    assert b'<h1>' in result
