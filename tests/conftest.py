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


@pytest.fixture
def builder():
    return MockBuilder()
