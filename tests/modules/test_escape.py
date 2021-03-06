from basilisk.modules.escape import EscapeModule
from basilisk.build import Build


html = '<h1>Test</h1>'


def test_add_processor():
    module = EscapeModule()
    build = Build(None, None)
    assert len(build.processors) == 0
    module.execute(build)
    assert len(build.processors) == 1


def test_processor():
    module = EscapeModule()
    processor = module.make_processor()
    result = processor(html)
    assert '<' not in result
    assert '>' not in result
    assert 'Test' in result
