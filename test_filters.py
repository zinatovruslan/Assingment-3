"""Tests for the catalog and filters F1-F5. Run: python -m unittest -v test_filters"""
import unittest

from booking import MSG_BLOCKED, MSG_OVERLAP, check_room
from filtering import filter_rooms
from rooms import CATALOG, EQUIPMENT, NOW, find_room


def ids(rooms):
    return [room.id for room in rooms]


class CatalogTests(unittest.TestCase):
    def test_catalog_has_at_least_four_rooms_with_required_fields(self):
        self.assertGreaterEqual(len(CATALOG), 4)
        for room in CATALOG:
            self.assertTrue(room.id and room.name)
            self.assertGreater(room.capacity, 0)
            self.assertIsInstance(room.equipment, tuple)
            self.assertIsInstance(room.blocked, bool)
            self.assertIsInstance(room.bookings, tuple)

    def test_room_ids_unique_and_bookings_valid(self):
        self.assertEqual(len(set(ids(CATALOG))), len(CATALOG))
        for room in CATALOG:
            for s, e in room.bookings:
                self.assertTrue(0 <= s < e <= 1440)


class FilterTests(unittest.TestCase):
    def test_f1_exact_capacity_included(self):
        self.assertIn("R104", ids(filter_rooms(CATALOG, 20, [])))  # capacity 20

    def test_f1_insufficient_capacity_excluded(self):
        self.assertNotIn("R104", ids(filter_rooms(CATALOG, 21, [])))
        self.assertIn("R101", ids(filter_rooms(CATALOG, 21, [])))

    def test_f2_all_selected_items_required(self):
        self.assertEqual(ids(filter_rooms(CATALOG, 1, ["projector", "whiteboard"])),
                         ["R101", "R104"])

    def test_f2_one_missing_item_excludes_room(self):
        # R104 has projector and whiteboard but no computers.
        self.assertEqual(ids(filter_rooms(CATALOG, 1, ["projector", "computers"])), ["R101"])

    def test_f2_no_selection_means_no_equipment_constraint(self):
        self.assertEqual(len(filter_rooms(CATALOG, 1, [])), len(CATALOG))

    def test_f4_no_match_returns_empty_list(self):
        self.assertEqual(filter_rooms(CATALOG, 1000, []), [])
        self.assertEqual(filter_rooms(CATALOG, 1, ["projector", "video-conference",
                                                   "whiteboard", "computers"]), [])

    def test_equipment_options_cover_catalog(self):
        self.assertEqual(set(EQUIPMENT), {"computers", "projector",
                                          "video-conference", "whiteboard"})


class AvailabilityPerRoomTests(unittest.TestCase):
    def test_f3_blocked_room_never_available(self):
        gamma = find_room(CATALOG, "R103")
        for start, end in [(600, 660), (700, 760), (1380, 1440)]:
            self.assertEqual(check_room(gamma, start, end, NOW), MSG_BLOCKED)

    def test_f3_blocked_room_still_listed_when_it_matches_requirements(self):
        self.assertIn("R103", ids(filter_rooms(CATALOG, 80, [])))

    def test_f5_availability_uses_selected_room_bookings_only(self):
        alpha, delta = find_room(CATALOG, "R101"), find_room(CATALOG, "R104")
        # 620-650 overlaps Alpha (600-660), not Delta (660-720). 670-700 is the reverse.
        self.assertEqual(check_room(alpha, 620, 650, NOW), MSG_OVERLAP)
        self.assertIsNone(check_room(delta, 620, 650, NOW))
        self.assertEqual(check_room(delta, 670, 700, NOW), MSG_OVERLAP)
        self.assertIsNone(check_room(alpha, 670, 700, NOW))

    def test_boundary_120_vs_121_on_free_room(self):
        pod = find_room(CATALOG, "R105")
        self.assertIsNone(check_room(pod, 600, 720, NOW))
        self.assertIsNotNone(check_room(pod, 600, 721, NOW))

    def test_boundary_touching_vs_overlapping_on_room_with_booking(self):
        delta = find_room(CATALOG, "R104")  # booked 660-720
        self.assertIsNone(check_room(delta, 600, 660, NOW))
        self.assertIsNone(check_room(delta, 720, 780, NOW))
        self.assertEqual(check_room(delta, 600, 661, NOW), MSG_OVERLAP)
        self.assertEqual(check_room(delta, 719, 780, NOW), MSG_OVERLAP)


if __name__ == "__main__":
    unittest.main()
