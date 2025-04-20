from time import monotonic
from typing import List, Optional
from os.path import dirname, realpath, join

# Import is now conditional
try:
    from src.backend.performance.analyse_log import print_loop_time
    PERFORMANCE_LOGGING_ENABLED = True
except ImportError:
    PERFORMANCE_LOGGING_ENABLED = False

PERFORMANCE_LOG_NAME = 'performance'


class Timer:
    """For timing segments of runtime loop to analyze where time can be saved.
    """
    def __init__(self, sections: List[str], log_name: Optional[str] = None, verbose_freq: Optional[int] = None):
        self.sections = sections
        self.tn = len(sections) + 1
        self.verbose_freq = verbose_freq
        self.print_counter = 0
        self.times = None
        self.segment = 0
        self.log = log_name is not None and PERFORMANCE_LOGGING_ENABLED
        if self.log:
            self.log_file = open(join(dirname(realpath(__file__)), log_name + '.log'), 'w')
            self.log_file.write(' '.join(self.sections) + '\n')

    def start_loop(self):
        """Write loop to file and start new timer for next loop.
        """
        if self.times is not None:
            # print old times
            if self.print_counter + 1 == self.verbose_freq and PERFORMANCE_LOGGING_ENABLED:
                self.print_counter = 0
                print_loop_time(self.sections, self.times)
            else:
                self.print_counter += 1
            # write old times to file
            if self.log:
                self.log_file.write(' '.join(str(t) for t in self.times) + '\n')
        # setup new times
        self.times = [-1.0] * self.tn
        self.segment = 1
        self.times[0] = monotonic()

    def split(self):
        """End timer for current section.
        """
        self.times[self.segment] = monotonic()
        self.segment += 1

    def end(self):
        """Stop timing and finish writing log file.
        """
        if self.log:
            self.log_file.close()
