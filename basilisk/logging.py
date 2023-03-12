import logging


root = logging.getLogger('basilisk')


def getLogger(name):
    return root.getChild(name)


class BasiliskFilter(logging.Filter):
    def filter(self, record):
        return record.name.startswith('basilisk')
