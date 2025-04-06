import cv2
from time import monotonic, sleep

INDEX = 1
variables = {
    'exposure': -5.0,  # default: -4.0
    'backend': cv2.CAP_DSHOW,  # default CAP_ANY
    'buffer': -1.0,  # default: -1.0
    'width': 640.0,  # default: 640.0
    'height': 480.0,  # default: 480.0
}
CV_VARIABLES = {
    'exposure': cv2.CAP_PROP_EXPOSURE,
    'buffer': cv2.CAP_PROP_BUFFERSIZE,
    'width': cv2.CAP_PROP_FRAME_WIDTH,
    'height': cv2.CAP_PROP_FRAME_HEIGHT,
}


class FPS:
    def __init__(self, precision: int):
        self._start = None
        self._frames = 0
        self._precision = precision

    def start(self):
        self._start = monotonic()
        return self

    def update(self):
        self._frames += 1

    def get_fps(self):
        return round(self._frames / (monotonic() - self._start), self._precision)

    def get_avg_ms_delay(self):
        return round(1000 * (monotonic() - self._start) / self._frames, self._precision)


# start capture
t0 = monotonic()
cap = cv2.VideoCapture(INDEX, variables['backend'])
print(f'Time to open: {1000*(monotonic() - t0)}ms')
# print info
print('-- Current Capture Info --')
for attr in CV_VARIABLES.keys():
    print(f'{attr}: {cap.get(CV_VARIABLES[attr])}')
# set new info
print('\n-- New Capture Info --')
for attr in CV_VARIABLES.keys():
    cap.set(CV_VARIABLES[attr], variables[attr])
    print(f'{attr}: {cap.get(CV_VARIABLES[attr])}')
# video feed
update_freq = 10
u = 0
fps = FPS(2)
fps.start()
while True:
    # read
    ret, frame = cap.read()
    fps.update()
    # print FPS
    if u >= update_freq:
        print(f'\rFPS: {fps.get_fps()}   ', end='')
        u = 0
    else:
        u += 1
    # check for break conditions
    if not ret:
        print('!! Could not capture image, exiting...')
        break
    cv2.imshow('Video Feed', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Optional: press 'q' to quit
        print('Exit key pressed')
        break
# print stats
print('\n------------------')
print(f'Final FPS: {fps.get_fps()}')
print(f'Final average delay: {fps.get_avg_ms_delay()}ms')
cap.release()
print()
print(f'Testing complete in {(monotonic() - t0)}s')


