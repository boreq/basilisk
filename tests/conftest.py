import pytest


source_directory = 'source_directory'
output_directory = 'output_directory'


class MockBuilder(object):

    def __init__(self):
        self.config = {
            'ignore_prefix': '_',
            'module_config': {},
        }
        self.source_directory = source_directory
        self.output_directory = output_directory
        self.builds = []
        self.builds_modified = False

    def add_build(self, build):
        self.builds_modified = True
        self.builds.append(build)


@pytest.fixture
def builder():
    return MockBuilder()
