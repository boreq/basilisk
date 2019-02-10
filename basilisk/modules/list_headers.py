import slugify
import bs4
import markdown
from ..module import Module


class ListHeadersModule(Module):
    """Scans the content of a build for HTML headers such as <h1> and adds a
    list of those headers to the build's context. That list is then available
    to modules further down the pipeline such as templates.

    The following object will be added to the build's context:

        {
            "headers": {
                "list": [
                    {
                        "name": "h1",
                        "id": "2-a-section-of-my-article",
                        "string": "A section of my article"
                    }
                    ...
                ]
            }
        }

    This module doesn't require any additional configuration.
    """

    header_names = ['h{}'.format(i) for i in range(1, 7)]

    def generate_header_id(self, header_number, header):
        slug = slugify.slugify(header.string)
        return '{}-{}'.format(header_number, slug)

    def set_header_id(self, header_number, header):
        if not 'id' in header or not header['id']:
            header['id'] = self.generate_header_id(header_number, header)

    def create_header_entry(self, header):
        return {
                'name': header.name,
                'id': header['id'],
                'string': header.string
        }

    def extract_and_modify_headers(self, content):
        headers = []
        soup = bs4.BeautifulSoup(content, features='html.parser')
        for child in soup.descendants:
            if child.name in self.header_names:
                self.set_header_id(len(headers), child)
                header_entry = self.create_header_entry(child)
                headers.append(header_entry)
        if len(headers) > 0:
            content = soup.prettify()
        return content, headers

    def make_processor(self, build):
        def processor(content, *args, **kwargs):
            content, headers = self.extract_and_modify_headers(content)
            build.additional_context['headers'] = {
                'list': headers
            } 
            return content
        return processor

    def execute(self, build):
        processor = self.make_processor(build)
        build.processors.append(processor)
