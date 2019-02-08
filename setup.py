from setuptools import setup

setup(
    name='basilisk',
    version='0.0.0',
    author='boreq',
    author_email='boreq@sourcedrops.com',
    description = ('Static website generator.'),
    license='BSD',
    packages=['basilisk', 'basilisk.modules'],
    install_requires=[
        'Jinja2',
        'Markdown',
        'Click',
        'tqdm',
        'htmlmin',
        'watchdog',
        'beautifulsoup4',
        'flask'
    ],
    entry_points='''
        [console_scripts]
        basilisk=basilisk.cli:cli
    ''',
)
