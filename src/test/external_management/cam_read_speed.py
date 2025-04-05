import cv2
from time import monotonic, sleep

NUM_TESTS = 5
INDICES = [0, 1, 2]
BACKENDS = {
    'ANY': cv2.CAP_ANY,
    'DSHOW': cv2.CAP_DSHOW,
}


class Records:
    def __init__(self, name: str, index: int, backend: str):
        self.name = name
        self.index = index
        self.backend = backend
        self._open_times = []
        self._read_times = []

    def store_open_time(self, open_time: float):
        self._open_times.append(open_time)

    def store_read_time(self, read_time: float):
        self._read_times.append(read_time)

    def average_open_time(self):
        return sum(self._open_times) / len(self._open_times)

    def average_read_time(self):
        return sum(self._read_times) / len(self._read_times)

    def print(self):
        print(f'{f"{self.name} ({self.index},{self.backend}) ":=<80}')
        print(f'{f"Min open: {1000*min(self._open_times):.3f}ms": <40}'
              f'{f"Min read: {1000*min(self._read_times):.3f}ms": <40}')
        print(f'{f"Avg open: {1000*self.average_open_time():.3f}ms": <40}'
              f'{f"Avg read: {1000*self.average_read_time():.3f}ms": <40}')
        print(f'{f"Max open: {1000*max(self._open_times):.3f}ms": <40}'
              f'{f"Max read: {1000*max(self._read_times):.3f}ms": <40}')


records_list = []

for i in INDICES:
    try:
        for b in BACKENDS.keys():
            rec = Records("camera", i, b)
            for t in range(NUM_TESTS):
                print(f'{f"TEST {i},{b} ({t+1}/{NUM_TESTS})": <30}', end='\n')
                # open test
                t0 = monotonic()
                cap = cv2.VideoCapture(i, BACKENDS[b])
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                rec.store_open_time(monotonic() - t0)
                # read test
                sleep(1)
                t0 = monotonic()
                ret, image = cap.read()
                rec.store_read_time(monotonic() - t0)
                cv2.imshow(f'{i},{b}', image)
                # disconnect
                cap.release()
            cv2.destroyAllWindows()
            print()
            records_list.append(rec)
            rec.print()
            print()
    except:
        print(f'CAM {i} failed to open')


print('\n\n-----------')
print('Best open time:')
rec = min(records_list, key=lambda x: x.average_open_time())
rec.print()
print()
print('Best read time:')
rec = min(records_list, key=lambda x: x.average_read_time())
rec.print()


