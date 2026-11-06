"""Regression tests for the original rules AC1-AC6 (Assignment #03).

Each case of test_booking.CASES becomes its own executable test, so the unittest
count reflects every case. Run: python -m unittest -v test_ac_regression
"""
import copy
import random
import unittest

from booking import can_book, check_room
from fuzz_check import oracle
from rooms import CATALOG, NOW
from test_booking import CASES, run_case


class RegressionCases(unittest.TestCase):
    pass


def _make(expected, start, end, overrides):
    def test(self):
        self.assertIs(run_case(start, end, overrides), expected)
    return test


for cid, rule, desc, start, end, overrides, expected in CASES:
    setattr(RegressionCases, f"test_{cid}_{rule}", _make(expected, start, end, overrides))


class BoundaryAndImmutability(unittest.TestCase):
    def test_ac2_120_minutes_allowed_121_rejected(self):
        self.assertTrue(can_book(600, 720, NOW, False, []))
        self.assertFalse(can_book(600, 721, NOW, False, []))

    def test_ac4_touching_allowed_overlap_rejected(self):
        existing = [(660, 720)]
        self.assertTrue(can_book(600, 660, NOW, False, existing))
        self.assertTrue(can_book(720, 780, NOW, False, existing))
        self.assertFalse(can_book(600, 661, NOW, False, existing))
        self.assertFalse(can_book(719, 780, NOW, False, existing))

    def test_ac5_catalog_bookings_unchanged_by_checks(self):
        before = repr(CATALOG)
        for room in CATALOG:
            for start, end in [(600, 660), (700, 760), (1380, 1440), (720, 660)]:
                check_room(room, start, end, NOW)
        self.assertEqual(repr(CATALOG), before)

    def test_ac5_input_list_not_mutated(self):
        existing = [(900, 960), (600, 660)]
        snapshot = copy.deepcopy(existing)
        can_book(630, 690, NOW, False, existing)
        self.assertEqual(existing, snapshot)

    def test_differential_against_oracle(self):
        rng = random.Random(7)
        for _ in range(20000):
            now = rng.randint(0, 1439)
            start = rng.randint(-5, 1445)
            end = start + rng.randint(-5, 130)
            blocked = rng.random() < 0.1
            existing = []
            for _ in range(rng.randint(0, 4)):
                s = rng.randint(0, 1400)
                existing.append((s, s + rng.randint(1, 120)))
            self.assertIs(can_book(start, end, now, blocked, existing),
                          oracle(start, end, now, blocked, existing),
                          (start, end, now, blocked, existing))


if __name__ == "__main__":
    unittest.main()
