import collections
from basilisk.modules.blog import BlogModule
from basilisk.build import Build


def test_preprocessing_and_postprocessing(builder):
    build_paths = [
            'blog_name/2019/02/04/article-one.html',
            'blog_name/2019/02/05/article-two.html',
            'blog_name/2019/02/05/article-three.html',

            'blog_name_similar_path/unrelated.html',
            'blog_nam/unrelated.html',
    ]

    ExpectedDummyBuild = collections.namedtuple('ExpectedDummyBuild', ['year', 'month', 'day'])
    expected_dummy_builds = [
        ExpectedDummyBuild('2019', '02', '04'),
        ExpectedDummyBuild('2019', '02', '05'),
        ExpectedDummyBuild('2019', '02', None),
        ExpectedDummyBuild('2019', None, None),
    ]

    builds = [Build(path, path) for path in build_paths]
    for build in builds:
        def read(*args, **kwargs):
            return ''
        build.read = read

    builder.config['module_config']['blog'] = {
        'directories': [
            {
                'name': 'blog_name',
                'directory': 'blog_name/',
                'insert_dummy_builds': True
            }
        ]
    }

    module = BlogModule()
    module.builder = builder
    module.preprocess(builds)
    assert len(builds) == len(build_paths) + len(expected_dummy_builds)

    def find_build(expected_dummy_build, builds):
        for build in builds:
            if hasattr(build, 'year'):
                if build.year == expected_dummy_build.year and \
                    build.month == expected_dummy_build.month and \
                    build.day == expected_dummy_build.day:
                    return build
        return None

    for expected_dummy_build in expected_dummy_builds:
        build = find_build(expected_dummy_build, builds)
        assert build is not None

    module.postprocess(builds)

    ExpectedListing = collections.namedtuple('ExpectedListing', ['path', 'relative_path'])
    expected_listings = [
        ExpectedListing('2019/02/04/article-one.html', 'article-one.html'),
        ExpectedListing('2019/02/05/article-two.html', 'article-two.html'),
        ExpectedListing('2019/02/05/article-three.html', 'article-three.html'),
    ]

    def find_listing(expected_listing, listing):
        for entry in listing:
            if entry['path'] == expected_listing.path and \
                entry['relative_path'] == expected_listing.relative_path:
                return entry
        return None

    listing = builds[0].additional_context['blog']['blog_name']['listing']
    tree = builds[0].additional_context['blog']['blog_name']['tree']

    for element in listing:
        print(element)

    assert len(listing) == len(expected_listings)
    for expected_listing in expected_listings:
        entry = find_listing(expected_listing, listing)
        assert entry is not None
