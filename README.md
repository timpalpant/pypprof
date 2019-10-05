# pypprof
pypprof adds HTTP-based endpoints for collecting profiles from a running Python application a la Go's [`net/http/pprof`](https://golang.org/pkg/net/http/pprof/).

Under the hood, it uses [zprofile](https://github.com/timpalpant/zprofile) and [mprofile](https://github.com/timpalpant/mprofile) to collect CPU and heap profiles with minimal overhead.

# Usage

## Add profiling endpoints to an application

Register the profiling endpoints in your application:
```python
from pypprof.net_http import start_pprof_server

start_pprof_server(port=8081)
```

## Fetch profiles from your running application

Fetch a 30s CPU profile, and view as a flamegraph:
```bash
$ go tool pprof -http=:8088 :8081/debug/pprof/profile
```

Fetch a heap profile:
```bash
$ go tool pprof :8081/debug/pprof/heap
```

Dump stacks from your application:
```bash
$ curl localhost:8081/debug/pprof/thread?debug=1
```

# Compatibility

pypprof is compatible with Python >= 2.7. Memory profiling is only available by default in Python >= 3.4. To enable memory profiling in earlier Pythons, you must patch Python and manually install [mprofile](https://github.com/timpalpant/mprofile).

# Contributing

Pull requests and issues are welcomed!

# License

pypprof is released under the [GNU Lesser General Public License, Version 3.0](https://www.gnu.org/licenses/lgpl-3.0.en.html)
