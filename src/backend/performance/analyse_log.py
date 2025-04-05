from os import listdir
from typing import List


def print_analysis(section_title: str, times: List[float]):
    """Prints statistics about a timed section.
    """
    print(f'{section_title + ' ':=<40}')
    print(f'Minimum: {min(times):.3f}ms')
    print(f'Average: {sum(times) / len(times):.3f}ms')
    print(f'Maximum: {max(times):.3f}ms')


def print_loop_time(section_titles: List[str], times: List[float]):
    """Prints times for each section in a given loop.
    """
    tn = len(times)
    to_print = []
    for t in range(1, tn):
        to_print.append(f'{section_titles[t-1]}:{(times[t]-times[t-1])*1000:06.2f}ms')
    print(f'{' '.join(to_print)} | {(times[tn-1]-times[0])*1000:06.2f}ms')


if __name__ == '__main__':
    # find logs ===========================================
    choice = -1
    logs = list(filter(lambda x: x.endswith('log'), listdir()))
    while choice <= 0 or choice > len(logs):
        for i, log in enumerate(logs):
            print(f'{i+1}: {log}')
        choice = int(input('Select which log to analyse: '))
    log = logs[choice-1]

    # read selected logs ==================================
    print(f'Analysing log file "{log}"...')
    with open(log, 'r') as file:
        # setup
        sections = file.readline().strip().split(' ')
        section_times = [[] for _ in range(len(sections))]
        all_times = []
        # read
        line = file.readline().strip()
        while len(line) > 0:
            times = line.split(' ')
            print_loop_time(sections, [float(t) for t in times])
            for i in range(len(sections)):
                section_times[i].append(1000 * (float(times[i+1]) - float(times[i])))
            all_times.append(1000 * (float(times[len(sections)]) - float(times[0])))
            line = file.readline().strip(' ')
    # analyse logs ========================================
    for i, section in enumerate(sections):
        print_analysis(section.upper(), section_times[i])
    print_analysis('ALL', all_times)
