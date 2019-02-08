import threading
import tempfile
import logging
import datetime
import socketserver
from http.server import SimpleHTTPRequestHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .builder import Builder
from .helpers import remove_directory_contents


logger = logging.getLogger('server')


def create_handler(directory_path):

    class RequestHandler(SimpleHTTPRequestHandler):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory_path, **kwargs)

    return RequestHandler


class EventHandler(FileSystemEventHandler):

    def __init__(self):
        self.received_event = threading.Event()

    def on_any_event(self, event):
        self.received_event.set()


class Server(object):
    """Server watches the specified directory and starts a build whenever any
    of the files changes. The output directory is set to a temporary directory
    which is served by the server. In consequence it is possible to run this
    command, open the browser and enjoy automated builds requiring the user to
    simply refresh the page when needed.

    Example usage:

        server = Server(source_directory)
        server.run()

    source_directory: root directory of the project to build.
    """

    # How often should the loop check if a new event arrived?
    event_timeout = 0.5 # [seconds]

    # How much time should pass without new events for the compiltion to start?
    event_debounce = 1 # [seconds]

    def __init__(self, source_directory, host='localhost', port=8080):
        self.source_directory = source_directory
        self.host = host
        self.port = port

    def create_text_frame(self, text):
        """Creates a nice frame for the text:
        
            #======================#
            #                      #
            # Your text goes here! #
            #                      #
            #======================#

        Returns a list of strings containing the frame lines.

        text: a string.
        """
        length = len(text)
        frame_edge = '=' * (length + 4)
        frame_padding = '#' + ' ' * (length + 2) + '#' 
        lines = [
                frame_edge,
                frame_padding,
                '# ' + text + ' #',
                frame_padding,
                frame_edge,
        ]
        return lines

    def run(self):
        text = 'Starting development server on http://{}:{}'.format(self.host, self.port)
        for line in self.create_text_frame(text):
            logger.info(line)

        with tempfile.TemporaryDirectory() as tmp_directory:
            logger.info('Created temporary directory: %s' % tmp_directory)

            serve = lambda: self.serve(tmp_directory)
            t = threading.Thread(target=serve)
            t.daemon = True
            t.start()

            self.compile(tmp_directory)

            event_handler = EventHandler()
            observer = Observer()
            observer.schedule(event_handler, self.source_directory, recursive=True)
            observer.start()
            try:
                self.watch_events(event_handler, tmp_directory)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

    def watch_events(self, event_handler, tmp_directory):
        last_event = None
        while True:
            if event_handler.received_event.wait(timeout=self.event_timeout):
                last_event = datetime.datetime.now()
                event_handler.received_event.clear()

            if last_event is not None:
                time_passed = datetime.datetime.now() - last_event
                if time_passed > datetime.timedelta(seconds=self.event_debounce):
                    last_event = None
                    self.compile(tmp_directory)

    def compile(self, tmp_directory):
        logger.info('Compiling...')
        remove_directory_contents(tmp_directory)
        builder = Builder(self.source_directory, tmp_directory)
        builder.run()
        logger.info('Compiled!')

    def serve(self, directory_path):
        server_address = (self.host, self.port)
        handler = create_handler(directory_path)
        with socketserver.TCPServer(server_address, handler) as httpd:
            httpd.serve_forever()

