from __future__ import print_function

import gc
import pkg_resources
import sys
import threading
import time
import traceback

import six
from six.moves.BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from six.moves.urllib.parse import parse_qs, urlparse

try:
    import mprofile
    has_mprofile = True
except ImportError:
    has_mprofile = False

from zprofile.cpu_profiler import CPUProfiler
from zprofile.wall_profiler import WallProfiler
from pypprof.builder import Builder
from pypprof import thread_profiler


_wall_profiler = WallProfiler()


def start_pprof_server(host='localhost', port=8080):
    '''Start a pprof server at the given host:port in a background thread.

    After calling this function, the pprof endpoints should be available
    at /debug/pprof/profile, etc.

    Returns the underlying HTTPServer. To stop the server, call shutdown().
    '''
    # WallProfiler's registers a Python signal handler, which must be done
    # on the main thread. So do it now before spawning the background thread.
    # As a result, starting the pprof server has the side effect of registering the
    # wall-clock profiler's SIGALRM handler, which may conflict with other uses.
    _wall_profiler.register_handler()

    server = HTTPServer((host, port), PProfRequestHandler)
    bg_thread = threading.Thread(target=server.serve_forever)
    bg_thread.daemon = True
    bg_thread.start()
    return server


class PProfRequestHandler(BaseHTTPRequestHandler):
    '''Handle pprof endpoint requests a la Go's net/http/pprof.

    The following endpoints are implemented:
      - /debug/pprof: List the available profiles.
      - /debug/pprof/profile: Collect a CPU profile.
      - /debug/pprof/wall: Collect a wall-clock profile.
      - /debug/pprof/heap: Get snapshot of current heap profile.
      - /debug/pprof/cmdline: The running program's command line.
      - /debug/pprof/thread (or /debug/pprof/goroutine): Currently running threads.
    '''
    def do_GET(self):
        url = urlparse(self.path)
        route = url.path.rstrip("/")
        qs = parse_qs(url.query)

        if route == "/debug/pprof":
            self.index()
        elif route == "/debug/pprof/profile":
            self.profile(qs)
        elif route == "/debug/pprof/wall":
            self.wall(qs)
        elif route == "/debug/pprof/heap":
            self.heap(qs)
        elif route in ("/debug/pprof/thread", "/debug/pprof/goroutine"):
            self.thread(qs)
        elif route == "/debug/pprof/cmdline":
            self.cmdline()
        else:
            self.send_error(404)

    def index(self):
        template = pkg_resources.resource_string(__name__, "index.html").decode("utf-8")
        body = template.format(num_threads=threading.active_count())

        self.send_response(200)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def profile(self, query):
        duration_qs = query.get("seconds", [30])
        duration_secs = int(duration_qs[0])
        cpu_profiler = CPUProfiler()
        pprof = cpu_profiler.profile(duration_secs)
        self._send_profile(pprof)

    def wall(self, query):
        duration_qs = query.get("seconds", [30])
        duration_secs = int(duration_qs[0])
        pprof = _wall_profiler.profile(duration_secs)
        self._send_profile(pprof)

    def heap(self, query):
        if query.get("gc"):
            gc.collect()
        if not has_mprofile:
            return self.send_error(412, "mprofile must be installed to enable heap profiling")
        if not mprofile.is_tracing():
            return self.send_error(412, "Heap profiling is not enabled")
        snap = mprofile.take_snapshot()
        pprof = build_heap_pprof(snap)
        self._send_profile(pprof)

    def thread(self, query):
        if query.get("debug"):
            self.send_response(200)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            for frame in six.itervalues(sys._current_frames()):
                for line in traceback.format_stack(frame):
                    self.wfile.write(line.encode("utf-8"))
                self.wfile.write("\n".encode("utf-8"))
        else:
            pprof = thread_profiler.take_snapshot()
            self._send_profile(pprof)

    def cmdline(self):
        body = "\0".join(sys.argv)
        self.send_response(200)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def _send_profile(self, pprof):
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", 'attachment; filename="profile"')
        self.end_headers()
        self.wfile.write(pprof)


def build_heap_pprof(snap):
  profile_builder = Builder()
  samples = {}  # trace => (count, measurement)
  for stat in snap.statistics('traceback'):
    trace = tuple((frame.name, frame.filename, frame.firstlineno, frame.lineno)
                  for frame in stat.traceback)
    try:
        samples[trace][0] += stat.count
        samples[trace][1] += stat.size
    except KeyError:
        samples[trace] = (stat.count, stat.size)
  profile_builder.populate_profile(samples, 'HEAP', 'bytes', snap.sample_rate, 1)
  return profile_builder.emit()
