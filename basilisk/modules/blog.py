import os
from . import Module
from ..build import Build


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
                    "insert_dummy_builds": true
                }
            ]
        }

    """

    priority = -4

    def blog_directories(self):
        return self.builder.config.get('blog_directories', [])

    def create_entry(self, build, blog_directory):
        # Here we have to cheat a little to get the params by reading the
        # file at this point.
        if not getattr(build, 'just_copy', False):
            inpath = os.path.join(self.builder.source_directory, build.input_path)
            lines = build.read(inpath)
            content, parameters = build.parse_lines(lines)
        else:
            parameters = []

        path = os.path.dirname(build.output_path)
        date = self.extract_date(build, blog_directory)
        if not date:
            return None

        entry = {
            'path': path,
            'directory': self.get_final_directory(build, blog_directory),
            'date': date,
            'parameters': parameters
        }
        return entry

    def extract_date(self, build, blog_directory):
        try:
            fmt = '{:02d}'
            path = self.get_relative_path(build, blog_directory)
            parts = path.split(os.sep)
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            return {
                'year': fmt.format(year),
                'month': fmt.format(month),
                'day': fmt.format(day)
            }
        except ValueError:
            return None

    def get_relative_path(self, build, blog_directory):
        path = os.path.dirname(build.output_path)
        return path[len(blog_directory['directory']):]

    def get_final_directory(self, build, blog_directory):
        path = self.get_relative_path(build, blog_directory)
        parts = path.split(os.sep)
        return parts[3]

    def insert_dummy_builds(self, builds, blog_directory, listing, tree_listing):
        """Creates dummy builds so that directory listings could be created in
        the templates.
        """
        for year in tree_listing:
            d = os.path.join(blog_directory['directory'], year, 'index.html')
            build = DummyBuild(d, d, year, None, None)
            self.add_context(build, blog_directory, listing, tree_listing)
            builds.append(build)
            for month in tree_listing[year]:
                d = os.path.join(blog_directory['directory'], year, month, 'index.html')
                build = DummyBuild(d, d, year, month, None)
                self.add_context(build, blog_directory, listing, tree_listing)
                builds.append(build)
                for day in tree_listing[year][month]:
                    d = os.path.join(blog_directory['directory'], year, month, day, 'index.html')
                    build = DummyBuild(d, d, year, month, day)
                    self.add_context(build, blog_directory, listing, tree_listing)
                    builds.append(build)

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

    def execute(self, builds):
        for blog_directory in self.blog_directories():
            # Listing is a chronological listing of all blog articles starting
            # with the newest ones.
            listing = []

            # Tree listing is a year/month/day style tree with the lists of
            # articles at the lowest level.
            tree_listing = {}

            for build in builds:
                # Scan for entires that are filed under .../year/month/day/...
                if build.output_path.startswith(blog_directory['directory']):
                    entry = self.create_entry(build, blog_directory)
                    if entry:
                        build.additional_context['date'] = entry['date']
                        listing.append(entry)
                        self.insert_into_tree_listing(tree_listing, entry)

                # Put the created listing the the additional context of each
                # build.
                self.add_context(build, blog_directory, listing, tree_listing)

            # Sort the entires descending by date.
            self.sort_by_date(listing)

            # Insert dummy builds to create directory listings under
            # .../year, .../year/month, and .../year/month/day.
            if blog_directory.get('insert_dummy_builds', False):
                self.insert_dummy_builds(builds, blog_directory, listing, tree_listing)
