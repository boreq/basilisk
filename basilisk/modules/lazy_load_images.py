import htmlmin
from ..module import Module
from bs4 import BeautifulSoup


class LazyLoadImagesModule(Module):
    """Adds an attribute `loading="lazy"` to all `<img>` tags.

    Example module definition:

        {
            "name": "lazy_load_images"
        }

    """

    def make_processor(self):
        def processor(content, *args, **kwargs):
            soup = BeautifulSoup(content.decode(), 'html.parser')
            for img in soup.find_all("img"):
                img['loading'] = 'lazy'
            return str(soup).encode()
        return processor

    def execute(self, build, module_config):
        processor = self.make_processor()
        build.processors.append(processor)
