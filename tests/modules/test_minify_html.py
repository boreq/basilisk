from basilisk.modules.minify_html import MinifyHtmlModule
from basilisk.build import Build


html = """
<h1>Hello</h1>

<p>Text.</p>
"""

minified_html = ' <h1>Hello</h1> <p>Text.</p> '


def test_add_processor():
    module = MinifyHtmlModule()
    build = Build(None, None)
    assert len(build.processors) == 0
    module.execute(build)
    assert len(build.processors) == 1


def test_processor():
    module = MinifyHtmlModule()
    processor = module.make_processor()
    result = processor(html)
    assert result == minified_html
