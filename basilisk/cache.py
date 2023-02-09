import os
import hashlib
import pickle
import appdirs
import datetime
import shutil
import typing

class Cache(object):

    def __init__(self, config, source_directory, output_directory):
        self.config = config
        self.source_directory = source_directory
        self.output_directory = output_directory
        self.storage = CacheStorage()

    def get(self, build) -> typing.Optional[bytes]:
        build_cache_key = self._get_key(build)
        return self.storage.get(build_cache_key)

    def put(self, build) -> None:
        build_cache_key = self._get_key(build)
        file_path = os.path.join(self.output_directory, build.output_path)
        self.storage.put(build_cache_key, file_path)

    def cleanup(self) -> None:
        self.storage.cleanup()

    def _get_key(self, build) -> bytes:
        inpath = os.path.join(self.source_directory, build.input_path)
        content = build.read(inpath)

        m = hashlib.sha256()
        m.update(inpath.encode('utf-8'))
        m.update(content)
        m.update(pickle.dumps(self.config))
        m.update(pickle.dumps(build.additional_context))
        return m.digest()

class CacheStorage(object):

    def __init__(self):
        self.cache_directory = appdirs.user_cache_dir("basilisk", "boreq")

    def get(self, h: bytes) -> typing.Optional[bytes]:
        file_path = os.path.join(self.cache_directory, h.hex())
        try:
            with open(file_path, 'rb') as f:
                now = self.utc_now()
                os.utime(file_path, (now.timestamp(), now.timestamp()))
                return f.read()
        except FileNotFoundError:
            return None

    def put(self, h: bytes, file_path: str) -> None:
        os.makedirs(self.cache_directory, exist_ok=True)
        target_file_path = os.path.join(self.cache_directory, h.hex())
        shutil.copyfile(file_path, target_file_path)

    def cleanup(self) -> None:
        for file_name in os.listdir(self.cache_directory):
            file_path = os.path.join(self.cache_directory, file_name)
            statinfo = os.stat(file_path)
            v = datetime.datetime.utcfromtimestamp(statinfo.st_atime)
            now = self.utc_now()
            if abs((v - now).total_seconds()) > 60 * 60:
                os.remove(file_path)

    def utc_now(self) -> datetime.datetime:
        return datetime.datetime.utcnow()
