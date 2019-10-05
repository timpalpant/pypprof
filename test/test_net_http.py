import gzip
import io
from six.moves.urllib.error import HTTPError
from six.moves.urllib.request import urlopen
import unittest

import mprofile
from pypprof.net_http import start_pprof_server
from pypprof.profile_pb2 import Profile


def parse_profile(buf):
    bufio = io.BytesIO(buf)
    with gzip.GzipFile(fileobj=bufio) as fd:
        return Profile.FromString(fd.read())


class TestPprofRequestHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mprofile.start(sample_rate=512)
        cls.host = "localhost"
        cls.port = 8083
        cls.server = start_pprof_server(cls.host, cls.port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        mprofile.stop()

    def _make_request(self, route):
        url = "http://{}:{}/debug/pprof/{}".format(
            self.host, self.port, route)
        return urlopen(url)

    def test_index(self):
        resp = self._make_request("")
        body = resp.read().decode("utf-8")
        self.assertIn("Profile Descriptions:", body)

    def test_cmdline(self):
        resp = self._make_request("cmdline")
        body = resp.read().decode("utf-8")
        self.assertTrue(len(body) > 0)

    def test_profile(self):
        resp = self._make_request("profile?seconds=1")
        body = resp.read()
        profile = parse_profile(body)

    def test_wall(self):
        resp = self._make_request("wall?seconds=1")
        body = resp.read()
        profile = parse_profile(body)

    def test_thread(self):
        resp = self._make_request("thread")
        body = resp.read()
        profile = parse_profile(body)

    def test_thread_debug(self):
        resp = self._make_request("thread?debug=2")
        body = resp.read().decode("utf-8")
        self.assertIn("pypprof/net_http.py", body)
        self.assertIn("test/main.py", body)

    def test_heap(self):
        resp = self._make_request("heap")
        body = resp.read()
        profile = parse_profile(body)

    def test_heap_gc(self):
        resp = self._make_request("heap?gc=1")
        body = resp.read()
        profile = parse_profile(body)

    def test_404(self):
        with self.assertRaises(HTTPError):
            self._make_request("noexisto")


if __name__ == '__main__':
    unittest.main()
