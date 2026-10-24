"""Acceptance tests for can_book (Assignment #03, AC1-AC5).

Run tests:           python -m unittest -v test_booking
Print results table: python test_booking.py --table
"""
import copy
import sys
import unittest

from booking import can_book

NOW = 540
EXISTING = [(600, 660)]

# (id, rule, description, start, end, overrides, expected)
# overrides may contain: now, blocked, existing
CASES = [
    # --- AC4: overlap and touching endpoints ---
    ("T01", "AC4", "touching: starts at booking end", 660, 720, {}, True),
    ("T02", "AC4", "touching: ends at booking start", 560, 600, {}, True),
    ("T03", "AC4", "overlap: partial, from inside", 630, 690, {}, False),
    ("T04", "AC4", "overlap: partial, into booking", 570, 630, {}, False),
    ("T05", "AC4", "overlap: request contains booking", 590, 670, {}, False),
    ("T06", "AC4", "overlap: request inside booking", 610, 650, {}, False),
    ("T07", "AC4", "overlap: identical interval", 600, 660, {}, False),
    ("T08", "AC4", "no bookings at all", 600, 660, {"existing": []}, True),
    ("T09", "AC4", "multiple bookings: fits between, touching both", 660, 700,
     {"existing": [(600, 660), (700, 760), (900, 960)]}, True),
    ("T10", "AC4", "multiple bookings: overlaps the second", 650, 710,
     {"existing": [(600, 660), (700, 760), (900, 960)]}, False),
    ("T11", "AC4", "unsorted bookings: touching, valid", 880, 900,
     {"existing": [(900, 960), (600, 660)]}, True),
    ("T12", "AC4", "unsorted bookings: overlaps the first listed", 920, 980,
     {"existing": [(900, 960), (600, 660)]}, False),
    # --- AC3: blocked room ---
    ("T13", "AC3", "blocked, otherwise valid", 660, 720, {"blocked": True}, False),
    ("T14", "AC3", "blocked, no bookings", 700, 760,
     {"blocked": True, "existing": []}, False),
    ("T15", "AC3", "blocked and invalid", 720, 660, {"blocked": True}, False),
    # --- AC2: duration ---
    ("T16", "AC2", "exactly 120 minutes", 720, 840, {}, True),
    ("T17", "AC2", "121 minutes", 720, 841, {}, False),
    ("T18", "AC2", "minimum duration 1 minute", 541, 542, {"existing": []}, True),
    # --- AC1: bounds, order, starts-now ---
    ("T19", "AC1", "starts exactly now", 540, 570, {}, False),
    ("T20", "AC1", "starts before now", 500, 560, {}, False),
    ("T21", "AC1", "starts one minute after now", 541, 571, {}, True),
    ("T22", "AC1", "reversed times", 720, 660, {}, False),
    ("T23", "AC1", "zero length", 700, 700, {}, False),
    ("T24", "AC1", "negative start", -10, 30, {"now": 0}, False),
    ("T25", "AC1", "end after day end", 1380, 1441, {}, False),
    ("T26", "AC1", "end exactly 1440", 1380, 1440, {}, True),
    ("T27", "AC1", "last minute of the day", 1439, 1440, {}, True),
    ("T28", "AC1", "start at 1440", 1440, 1441, {"now": 1439}, False),
    ("T29", "AC1", "now at day edge, no valid request", 1439, 1440, {"now": 1439}, False),
    ("T30", "AC1", "now at 0, earliest start", 1, 61, {"now": 0, "existing": []}, True),
    ("T31", "AC1", "start 0 is never after now", 0, 60, {"now": 0, "existing": []}, False),
    # --- AC1: integer minutes only (non-integer input is rejected) ---
    ("T32", "AC1", "bool start (True == 1)", True, 61, {"now": 0, "existing": []}, False),
    ("T33", "AC1", "float start", 600.0, 660, {"existing": []}, False),
    ("T34", "AC1", "string start", "600", 660, {"existing": []}, False),
    ("T35", "AC1", "float end", 600, 660.5, {"existing": []}, False),
    # --- added after review of v1 (Exchange 3): test-suite gaps ---
    ("T36", "AC4", "overlap by 1 minute at booking end", 659, 700, {}, False),
    ("T37", "AC4", "overlap by 1 minute at booking start", 541, 601, {}, False),
    ("T38", "AC2", "120 minutes ending at day end", 1320, 1440, {"now": 0}, True),
    ("T39", "AC1", "bool now (False == 0)", 1, 61, {"now": False, "existing": []}, False),
    ("T40", "AC1", "float now", 700, 760, {"now": 600.0, "existing": []}, False),
    ("T41", "AC1", "string now", 700, 760, {"now": "600", "existing": []}, False),
    ("T42", "AC2", "121 minutes ending at day end", 1319, 1440, {"now": 0}, False),
]


def run_case(start, end, overrides):
    args = dict(now=NOW, blocked=False, existing=copy.deepcopy(EXISTING))
    args.update(copy.deepcopy(overrides))
    return can_book(start, end, args["now"], args["blocked"], args["existing"])


class AcceptanceTests(unittest.TestCase):
    def test_cases(self):
        for cid, rule, desc, start, end, overrides, expected in CASES:
            with self.subTest(case=cid, rule=rule, desc=desc):
                self.assertIs(run_case(start, end, overrides), expected)

    def test_inputs_unchanged_when_available(self):
        existing = [(900, 960), (600, 660)]
        snapshot = copy.deepcopy(existing)
        self.assertIs(can_book(660, 720, NOW, False, existing), True)
        self.assertEqual(existing, snapshot)

    def test_inputs_unchanged_when_unavailable(self):
        existing = [(900, 960), (600, 660)]
        snapshot = copy.deepcopy(existing)
        self.assertIs(can_book(630, 690, NOW, False, existing), False)
        self.assertEqual(existing, snapshot)

    def test_inputs_unchanged_when_blocked(self):
        existing = [(900, 960), (600, 660)]
        snapshot = copy.deepcopy(existing)
        self.assertIs(can_book(700, 760, NOW, True, existing), False)
        self.assertEqual(existing, snapshot)


def print_table():
    print("ID  | AC  | start -> end | now  | blocked | existing                | "
          "expected | actual | match | description")
    for cid, rule, desc, start, end, overrides, expected in CASES:
        args = dict(now=NOW, blocked=False, existing=EXISTING)
        args.update(overrides)
        actual = run_case(start, end, overrides)
        mark = "OK" if actual is expected else "FAIL"
        span = f"{start!r} -> {end!r}"
        print(f"{cid} | {rule} | {span:<12} | {args['now']!r:<4} | "
              f"{args['blocked']!r:<7} | {args['existing']!r:<23} | "
              f"{expected!r:<8} | {actual!r:<6} | {mark:<5} | {desc}")


if __name__ == "__main__":
    if "--table" in sys.argv:
        print_table()
    else:
        unittest.main()