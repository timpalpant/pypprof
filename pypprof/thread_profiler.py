from collections import Counter
import six
import sys

from pypprof import builder

# Maximum stack frames to record.
_MAX_STACK_DEPTH = 128


def take_snapshot():
  samples = {extract_trace(frame): (1, 1)
             for frame in six.itervalues(sys._current_frames())}
  profile_builder = builder.Builder()
  profile_builder.populate_profile(samples, 'THREADS', 'count', 1, 1)
  return profile_builder.emit()


def extract_trace(frame):
  """Extracts the call stack trace of the given frame.

  Args:
    frame: A Frame object representing the leaf frame of the stack.

  Returns:
    A tuple of frames. The leaf frame is at position 0. A frame is a
    (function name, filename, line number) tuple.
  """
  depth = 0
  trace = []
  while frame is not None and depth < _MAX_STACK_DEPTH:
    frame_tuple = (frame.f_code.co_name, frame.f_code.co_filename,
                   frame.f_code.co_firstlineno, frame.f_lineno)
    trace.append(frame_tuple)
    frame = frame.f_back
    depth += 1
  return tuple(trace)

