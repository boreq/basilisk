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
        'Jinja2==3.1.*',
        'Markdown',
        'Click==8.3.*',
        'tqdm',
        'htmlmin2==0.1.13',
        'watchdog',
        'beautifulsoup4',
        'flask==3.1.*',
        'werkzeug==3.1.*',
        'python-slugify',
        'feedgen',
        'pillow',
        'appdirs==1.4',
    ],
    extras_require={
        'dev': [
            'pyflakes',
            'pytest',
            'mypy==1.0',
            'types-appdirs',
            'types-pillow',
            'types-Markdown',
            'types-python-slugify',
            'types-beautifulsoup4',
            'types-tqdm',
            'types-babel',
        ],
    },
    entry_points='''
        [console_scripts]
        basilisk=basilisk.cli:cli
    ''',
)
