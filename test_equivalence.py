"""Behavior-preservation check: refactored app vs frozen pre-refactor v1.

Compares the complete HTML output for many generated requests.
Run: python -m unittest -v test_equivalence
"""
import random
import unittest

import app
from legacy import app_v1

ATTENDEES = ["1", "6", "12", "20", "21", "30", "31", "80", "81", "0", "-3", "abc", "", " 5 ", "1_0", "2.5"]
EQUIP = ["computers", "projector", "video-conference", "whiteboard", "bogus"]
ROOMS = ["R101", "R102", "R103", "R104", "R105", "zzz"]


def random_params(rng):
    params = {}
    if rng.random() < 0.9:
        params["attendees"] = [rng.choice(ATTENDEES)]
    chosen = [item for item in EQUIP if rng.random() < 0.3]
    if chosen:
        params["equip"] = chosen
    if rng.random() < 0.8:
        params["room"] = [rng.choice(ROOMS)]
    for key in ("start", "end"):
        if rng.random() < 0.85:
            params[key] = [rng.choice([str(rng.randint(-10, 1450)), "", "x", "600.0", " 700 ", "<b>"])]
    return params


class EquivalenceTests(unittest.TestCase):
    def test_html_identical_for_random_requests(self):
        rng = random.Random(1)
        for _ in range(5000):
            params = random_params(rng)
            self.assertEqual(app.handle(params), app_v1.handle(params), params)

    def test_html_identical_for_every_room_and_boundary_times(self):
        for room in ROOMS:
            for start, end in [(600, 660), (660, 720), (659, 700), (720, 840), (720, 841),
                               (1380, 1440), (540, 570), (720, 660)]:
                params = {"attendees": ["1"], "room": [room],
                          "start": [str(start)], "end": [str(end)]}
                self.assertEqual(app.handle(params), app_v1.handle(params), params)


if __name__ == "__main__":
    unittest.main()
