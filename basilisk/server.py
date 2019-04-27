import threading
import tempfile
import logging
import datetime
import io
import bs4
import time
import flask
import os
import traceback
from werkzeug import serving
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .builder import Builder
from .helpers import remove_directory_contents


logger = logging.getLogger('server')


script =  """
    function basilisk() {
        let lastCompilationTimestamp;

        function scheduleReload() {
            setTimeout(doRequest, 1000);
        }

        function responseListener() {
            let compilationTimestamp = this.response.compilationTimestamp;

            if (lastCompilationTimestamp && compilationTimestamp !== lastCompilationTimestamp) {
                location.reload(true);
            }

            lastCompilationTimestamp = compilationTimestamp;
            scheduleReload();
        }

        function errorListener() {
            console.log('Error! Is basilisk running?');
            scheduleReload();
        }

        function doRequest() {
            let request = new XMLHttpRequest();
            request.addEventListener('load', responseListener);
            request.addEventListener('error', errorListener);
            request.open('GET', '/basilisk-status.json');
            request.responseType = 'json';
            request.send();
        }

        doRequest();
    };

    basilisk();
"""


def create_script_tag(soup):
    """Creates a <script> tag containing a script which auto refreshes the
    website after the project is rebuilt.
    """
    script_tag = soup.new_tag('script')
    script_tag.string = script
    return script_tag


def inject_script(bufferedReader):
    """Injects a script into the body of all html files. This script makes the
    website automatically reload itself after changes are detected. This is
    done using polling.
    """
    content = bufferedReader.read()
    soup = bs4.BeautifulSoup(content, features='html.parser')
    if soup.body:
        script_tag = create_script_tag(soup)
        soup.body.append(script_tag)
        content = str(soup).encode('utf-8')
    return io.BytesIO(content)


def create_text_frame(text, character_horizontal='=', character_vertical='#'):
    """Creates a nice frame for the text:
    
        #======================#
        #                      #
        # Your text goes here! #
        #                      #
        #======================#

    Returns a list of strings containing the frame lines.

    text: a string.
    character_horizontal: a character used for horizontal lines.
    character_vertical: a character used for vertical lines.
    """
    length = len(text)
    frame_edge = character_horizontal * (length + 4)
    frame_padding = character_vertical + ' ' * (length + 2) + character_vertical
    lines = [
            frame_edge,
            frame_padding,
            '{} {} {}'.format(character_vertical, text, character_vertical),
            frame_padding,
            frame_edge,
    ]
    return lines


def iter_file_paths(path):
    if os.path.isfile(path):
        yield path
    yield os.path.join(path, 'index.html')
    yield os.path.join(path, 'index.htm')


def create_app(directory_path, status):
    """Creates a Flask app which serves files from the specified directory as
    well as a special endpoint used by basilisk to check the compilation
    status. Flask is used instead of using socketserver directly because of
    some truly bizzare "address is already in use" errors that I encountered
    when using it directly (despite freeing up resources on program shutdown).
    """
    app = flask.Flask(__name__, static_folder=None)

    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)

    from functools import update_wrapper

    def nocache(f):
        def new_func(*args, **kwargs):
            resp = flask.make_response(f(*args, **kwargs))
            resp.cache_control.no_cache = True
            return resp
        return update_wrapper(new_func, f)

    @app.route('/basilisk-status.json')
    @nocache
    def route_status():
        return flask.jsonify(status)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    @nocache
    def route_file(path):
        path = flask.safe_join(directory_path, path)
        for file_path in iter_file_paths(path):
            if os.path.exists(file_path):
                f = open(file_path, 'rb')
                if f.name.endswith('.html') or f.name.endswith('.htm'):
                    f = inject_script(f)
                return flask.send_file(f, attachment_filename=file_path)

        logger.warning('Server: file not found: {}'.format(path))
        flask.abort(404)
    return app


class ServerThread(threading.Thread):

    def __init__(self, app, host, port):
        threading.Thread.__init__(self)
        self.srv = serving.make_server(host, port, app)

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


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


    def run(self):
        text = 'Starting development server on http://{}:{}'.format(self.host, self.port)
        for line in create_text_frame(text):
            logger.info(line)

        with tempfile.TemporaryDirectory() as tmp_directory:
            logger.info('Created temporary directory: %s' % tmp_directory)

            status = {}

            self.compile(tmp_directory, status)

            app = create_app(tmp_directory, status)
            server = ServerThread(app, self.host, self.port)
            server.start()

            event_handler = EventHandler()
            observer = Observer()
            observer.schedule(event_handler, self.source_directory, recursive=True)
            observer.start()
            try:
                self.watch_events(event_handler, tmp_directory, status)
            except KeyboardInterrupt:
                pass
            finally:
                logger.info('Cleaning up')
                observer.stop()
                server.shutdown()
                server.join()
            observer.join()

    def watch_events(self, event_handler, tmp_directory, status):
        last_event = None
        while True:
            if event_handler.received_event.wait(timeout=self.event_timeout):
                last_event = datetime.datetime.now()
                event_handler.received_event.clear()

            if last_event is not None:
                time_passed = datetime.datetime.now() - last_event
                if time_passed > datetime.timedelta(seconds=self.event_debounce):
                    last_event = None
                    self.compile(tmp_directory, status)

    def compile(self, tmp_directory, status):
        try:
            remove_directory_contents(tmp_directory)
            builder = Builder(self.source_directory, tmp_directory)
            builder.run()
            status['compilationTimestamp'] = time.time()
            logger.info('Compiled!')
        except:
            logger.error('Compilation failed!')
            traceback.print_exc()
