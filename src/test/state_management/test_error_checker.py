from src.backend.state_management.error_checker import verify_track

import unittest

TEST_DATA_HAPPY = [
    (0.0, (0.0, 0.0, 0.0)),
    (0.1, (0.0, 0.0, 0.5)),
    (0.2, (0.0, 0.0, 1.0)),
    (0.3, (0.0, 0.0, 1.5)),
    (0.4, (0.0, 0.0, 2.0)),
    (0.5, (0.0, 0.0, 2.5)),
    (0.6, (0.0, 0.0, 3.0)),
    (0.7, (0.0, 0.0, 3.5)),
    (0.8, (0.0, 0.0, 4.0)),
    (0.9, (0.0, 0.0, 4.5)),
    (1.0, (0.0, 0.0, 5.0)),
    (1.1, (0.0, 0.0, 5.5)),
    (1.2, (0.0, 0.0, 6.0)),
    (1.3, (0.0, 0.0, 6.5)),
    (1.4, (0.0, 0.0, 7.0)),
]

TEST_DATA_TIME = [
    (0.0, (0.0, 0.0, 0.0)),
    (0.3, (0.0, 0.0, 0.0)),
]

TEST_DATA_DIST = [
    (0.0, (0.0, 0.0, 0.0)),
    (0.1, (0.7, 0.7, 0.7)),
]

TEST_DATA_EDGE = [
    (0.0, (0.0, 0.0, 0.0)),
    (0.2, (0.5, 0.5, 0.5)),
    (0.0, (0.0, 0.0, 0.0)),
    (0.0, (-1, 0, 0)),
    (0.0, (-1, 1, 0)),
]

class TestErrorChecker(unittest.TestCase):

    def test_verify_track_happy(self):
        """Happy path of ``verify_track``.
        """
        self.assertTrue(verify_track(TEST_DATA_HAPPY))

    def test_verify_track_empty(self):
        """``verify_track`` should pass if no history exists.
        """
        self.assertTrue(verify_track([]))

    def test_verify_track_time(self):
        """``verify_track`` should fail if time interval is too great.
        """
        self.assertFalse(verify_track(TEST_DATA_TIME))

    def test_verify_track_dist(self):
        """``verify_track`` should fail if distance interval is too great.
        """
        self.assertFalse(verify_track(TEST_DATA_DIST))

    def test_verify_track_edge(self):
        """``verify_track`` should fail if distance interval is too great.
        """
        self.assertTrue(verify_track(TEST_DATA_EDGE))

if __name__ == '__main__':
    unittest.main()