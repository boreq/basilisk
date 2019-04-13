import os
import datetime
import urllib
from ..module import Module
from ..build import Build
from feedgen.feed import FeedGenerator


class DummyBuild(Build):

    def __init__(self, input_path, output_path, year, month, day):
        super().__init__(input_path, output_path)
        self.additional_context['year'] = year
        self.additional_context['month'] = month
        self.additional_context['day'] = day

    @property
    def year(self):
        return self.additional_context['year']

    @property
    def month(self):
        return self.additional_context['month']

    @property
    def day(self):
        return self.additional_context['day']

    def read(self, path):
        if self.day:
            return ['title: {}'.format(self.day)]
        if self.month:
            return ['title: {}'.format(self.month)]
        if self.year:
            return ['title: {}'.format(self.year)]


class FeedBuild(Build):

    def __init__(self, input_path, output_path, blog_directory, listing):
        super().__init__(input_path, output_path)
        self.blog_directory = blog_directory
        self.listing = listing

    def get_feed(self):
        feed = self.blog_directory['feed']
        url = urllib.parse.urljoin(feed['base_url'], self.blog_directory['directory'])
        self_url = urllib.parse.urljoin(feed['base_url'], self.output_path)

        fg = FeedGenerator()
        fg.id(url)
        fg.title(feed['title'])
        fg.link(href=url, rel='alternate')
        fg.link(href=self_url, rel='self')
        fg.description('An automatically generated feed.')

        for entry in reversed(self.listing):
            entry_url = urllib.parse.urljoin(url, entry['path'])
            fe = fg.add_entry()
            fe.id(entry_url)
            fe.title(entry['parameters'].get('title', 'No title'))
            fe.published(self.get_date(entry))
            fe.link(href=entry_url)

        return fg

    def get_date(self, entry):
        return datetime.datetime(
            int(entry['date']['year']),
            int(entry['date']['month']),
            int(entry['date']['day']),
            tzinfo=datetime.timezone.utc
        )

    def read(self, path):
        return self.get_str().decode('utf-8').splitlines(True)


class RssBuild(FeedBuild):

    def __init__(self, input_path, output_path, blog_directory, listing):
        super().__init__(input_path, output_path, blog_directory, listing)

    def get_str(self):
        return self.get_feed().rss_str(pretty=True)


class AtomBuild(FeedBuild):

    def __init__(self, input_path, output_path, blog_directory, listing):
        super().__init__(input_path, output_path, blog_directory, listing)

    def get_str(self):
        return self.get_feed().atom_str(pretty=True)


class BlogModule(Module):
    """Adds additional context with lists of blog-style articles or posts into
    every build. The articles should be placed under year/month/day the
    specified blog directory, for example my_blog/2018/10/28/my_post/index.html.

    Additional context example:

        {
            'blog': {
                'blog_name': {
                    'listing': [
                        {
                            'path': 'blog_name/2018/10/28/my_post',
                            'relative_path': '2018/10/28/my_post',
                            'date': {
                                'year': 2018,
                                'month': 10,
                                'day': 28
                            },
                            'parameters': {'title': 'My post'}
                        } 
                    ],
                    'tree': {
                        2018: {
                            10: {
                                28: [
                                    {
                                        'path': 'blog_name/2018/10/28/my_post',
                                        'relative_path': '2018/10/28/my_post',
                                        'date': {
                                            'year': 2018,
                                            'month': 10,
                                            'day': 28
                                        },
                                        'parameters': {'title': 'My post'}
                                    } 
                                ]
                            }
                        }
                    },
                }
            }
        }

    Example config:

        {
            "blog_directories": [
                {
                    "name": "thoughts",
                    "directory": "thoughts/",
                    "insert_dummy_builds": true,
                    "feed": {
                        "title": "Thoughts",
                        "base_url": "https://example.com/",
                        "files": {
                            "rss": "thoughts/feed.rss",
                            "atom": "thoughts/feed.atom"
                        }
                    }
                }
            ]
        }

    """

    config_key = 'blog'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_builds = []
        self.created_feed_builds = []

    def blog_directories(self):
        directories = self.config_get('directories', [])
        if len(directories) == 0:
            self.logger.warning('no blog directories defined, did you configure "blog"?')
        return directories

    def create_entry(self, build, blog_directory):
        # Here we have to cheat a little to get the params by reading the
        # file at this point.
        inpath = os.path.join(self.builder.source_directory, build.input_path)
        lines = build.read(inpath)
        content, parameters = build.parse_lines(lines)

        path = self.get_relative_path(build, blog_directory)
        relative_path = self.get_relative_path_tail(build, blog_directory)
        date = self.extract_date(build, blog_directory)
        if not date:
            return None

        entry = {
            'path': self.strip_index(path),
            'relative_path': self.strip_index(relative_path),
            'date': date,
            'parameters': parameters
        }
        return entry

    def extract_date_components(self, build, blog_directory):
        try:
            fmt = '{:02d}'
            path = self.get_relative_directory(build, blog_directory)
            parts = path.split(os.sep)
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            return fmt.format(year), fmt.format(month), fmt.format(day)
        except (ValueError, IndexError):
            return None

    def extract_date(self, build, blog_directory):
        date = self.extract_date_components(build, blog_directory)
        if date is not None:
            year, month, day  = date
            return {
                'year': year,
                'month': month,
                'day': day,
            }
        return None

    def get_relative_path_tail(self, build, blog_directory):
        """Returns path relative to the day directory for this entry."""
        path = self.get_relative_path(build, blog_directory)
        parts = path.split(os.sep)
        return os.path.join('', *parts[3:])

    def get_relative_path(self, build, blog_directory):
        """Returns path relative to blog directory."""
        return build.output_path[len(blog_directory['directory']):]

    def get_relative_directory(self, build, blog_directory):
        """Returns head of the path relative to blog directory."""
        path = self.get_relative_path(build, blog_directory)
        head, tail = os.path.split(path)
        return head

    def strip_index(self, path):
        head, tail = os.path.split(path)
        if tail == 'index.html':
            return head
        return path

    def dummy_build_was_created(self, blog_directory, year, month, day):
        for build_blog_directory, build_year, build_month, build_day in self.created_builds:
            if blog_directory == build_blog_directory and \
                year == build_year and \
                month == build_month and \
                day == build_day:
                    return True
        return False

    def register_dummy_build_creation(self, blog_directory, year, month, day):
        self.created_builds.append((blog_directory, year, month, day))

    def iterate_date_tuples(self, tree_listing):
        for year in tree_listing:
            yield (year, None, None)
            for month in tree_listing[year]:
                yield (year, month, None)
                for day in tree_listing[year][month]:
                    yield (year, month, day)

    def insert_dummy_builds(self, builds, blog_directory, tree_listing):
        """Creates dummy builds so that directory listings could be created in
        the templates.
        """
        for year, month, day in self.iterate_date_tuples(tree_listing):
            if not self.dummy_build_was_created(blog_directory, year, month, day):
                path_elements = [blog_directory['directory'], year]
                if month is not None:
                    path_elements.append(month)
                if day is not None:
                    path_elements.append(day)
                path_elements.append('index.html')
                d = os.path.join(*path_elements)
                build = DummyBuild(d, d, year, month, day)
                self.builder.add_build(build)
                self.register_dummy_build_creation(blog_directory, year, month, day)

    def insert_into_tree_listing(self, tree_listing, entry):
        y = entry['date']['year']
        m = entry['date']['month']
        d = entry['date']['day']

        if not y in tree_listing:
            tree_listing[y] = {}

        if not m in tree_listing[y]:
            tree_listing[y][m] = {}

        if not d in tree_listing[y][m]:
            tree_listing[y][m][d] = []

        tree_listing[y][m][d].append(entry)
        self.sort_by_date(tree_listing[y][m][d])

    def sort_by_date(self, listing):
        """Sorts the listing by the date of the article, newest first."""
        s = lambda entry: '{}-{}-{}'.format(
                entry['date']['year'],
                entry['date']['month'],
                entry['date']['day']
            )
        listing.sort(key=s, reverse=True)

    def add_context(self, build, blog_directory, listing, tree_listing):
        """Inserts listing and tree_listing into the additional context of the
        provided build.
        """
        if not 'blog' in build.additional_context:
            build.additional_context['blog'] = {}
        if not blog_directory['name'] in build.additional_context['blog']:
            build.additional_context['blog'][blog_directory['name']] = {}
        build.additional_context['blog'][blog_directory['name']]['listing'] = listing
        build.additional_context['blog'][blog_directory['name']]['tree'] = tree_listing

    def is_in_blog_directory(self, build, blog_directory):
        """Returns True if the build resides in the blog directory (is part of
        the given blog).
        """
        paths = [build.output_path, blog_directory['directory']]
        prefix = os.path.commonprefix(paths)
        return prefix == blog_directory['directory']

    def insert_feed_builds(self, builds, blog_directory, listing):
        """Creates feed builds."""
        if 'feed' in blog_directory: 
            for feed_type, feed_file in blog_directory['feed'].get('files', {}).items():
                if not self.feed_build_was_created(blog_directory, feed_type):
                    build = self.create_feed_build(feed_type, feed_file, blog_directory, listing)
                    self.builder.add_build(build)
                    self.register_feed_build_creation(blog_directory, feed_type)

    def create_feed_build(self, feed_type, feed_file, blog_directory, listing):
        if feed_type == 'rss':
            return RssBuild(feed_file, feed_file, blog_directory, listing)
        if feed_type == 'atom':
            return AtomBuild(feed_file, feed_file, blog_directory, listing)
        raise ValueError('Invalid feed type {}'.format(feed_type))

    def feed_build_was_created(self, blog_directory, feed_type):
        for build_blog_directory, build_feed_type in self.created_feed_builds:
            if blog_directory['directory'] == build_blog_directory['directory'] \
                and feed_type == build_feed_type:
                return True
        return False

    def register_feed_build_creation(self, blog_directory, build_feed_type):
        self.created_feed_builds.append((blog_directory, build_feed_type))

    def process(self, builds):
        for blog_directory in self.blog_directories():
            self.logger.debug('blog directory %s', blog_directory)

            # Listing is a chronological listing of all blog articles starting
            # with the newest ones.
            listing = []

            # Tree listing is a year/month/day style tree with the lists of
            # articles at the lowest level.
            tree_listing = {}

            for build in builds:
                # Scan for entires that are filed under .../year/month/day/...
                if self.is_in_blog_directory(build, blog_directory):
                    if not isinstance(build, DummyBuild):
                        entry = self.create_entry(build, blog_directory)
                        if entry is not None:
                            build.additional_context['date'] = entry['date']
                            listing.append(entry)
                            self.insert_into_tree_listing(tree_listing, entry)

                # Put the created listing the the additional context of each
                # build.
                self.add_context(build, blog_directory, listing, tree_listing)

            self.insert_dummy_builds(builds, blog_directory, tree_listing)
            self.insert_feed_builds(builds, blog_directory, listing)

            # Sort the entires descending by date.
            self.sort_by_date(listing)
