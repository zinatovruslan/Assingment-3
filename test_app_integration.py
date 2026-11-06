"""Integration/UI behavior tests through the WSGI application (no network, no browser).

Run: python -m unittest -v test_app_integration
"""
import unittest
from wsgiref.util import setup_testing_defaults

from app import application
from rooms import CATALOG


def get(query="", path="/", method="GET"):
    environ = {"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query}
    setup_testing_defaults(environ)
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    body = b"".join(application(environ, start_response)).decode("utf-8")
    return captured["status"], body


class IntegrationTests(unittest.TestCase):
    def test_successful_filter_and_available_result(self):
        status, html = get("attendees=10&equip=projector&room=R101&start=700&end=760")
        self.assertTrue(status.startswith("200"))
        self.assertIn("Alpha Lab (R101): Available for 700-760", html)
        self.assertIn("Delta Seminar (R104)", html)
        self.assertNotIn("Beta Studio", html)  # no projector

    def test_unsuccessful_filter_shows_empty_state(self):
        _, html = get("attendees=500")
        self.assertIn("No rooms match these requirements.", html)
        self.assertNotIn('<select name="room"', html)

    def test_equipment_combination_with_no_match_shows_empty_state(self):
        _, html = get("attendees=1&equip=projector&equip=video-conference"
                      "&equip=whiteboard&equip=computers")
        self.assertIn("No rooms match these requirements.", html)

    def test_room_switching_changes_result_for_same_times(self):
        _, alpha = get("attendees=1&room=R101&start=620&end=650")
        _, delta = get("attendees=1&room=R104&start=620&end=650")
        self.assertIn("Alpha Lab (R101): Unavailable - Overlaps an existing booking", alpha)
        self.assertIn("Delta Seminar (R104): Available for 620-650", delta)

    def test_blocked_room_reports_unavailable(self):
        _, html = get("attendees=80&room=R103&start=700&end=760")
        self.assertIn("Gamma Hall (R103): Unavailable - Room is blocked", html)
        self.assertIn('class="badge">blocked', html)

    def test_selected_room_outside_filter_falls_back_to_first_match(self):
        _, html = get("attendees=30&room=R105&start=700&end=760")
        self.assertIn("Alpha Lab (R101)", html.split('id="result"')[1])

    def test_validation_feedback_messages(self):
        cases = {
            "start=720&end=660": "End must be after start",
            "start=500&end=560": "Start must be after the current time",
            "start=700&end=821": "Duration cannot exceed 120 minutes",
            "start=1380&end=1441": "Times must be whole minutes from 0 to 1440",
            "start=abc&end=700": "Times must be whole minutes from 0 to 1440",
            "start=600.0&end=700": "Times must be whole minutes from 0 to 1440",
        }
        for query, message in cases.items():
            with self.subTest(query=query):
                _, html = get("attendees=1&room=R105&" + query)
                self.assertIn(message, html)

    def test_invalid_attendees_shows_error_not_empty_state(self):
        _, html = get("attendees=abc")
        self.assertIn("Attendees must be a whole number of at least 1", html)
        self.assertNotIn("No rooms match", html)

    def test_responsive_markup_present(self):
        _, html = get("")
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', html)
        self.assertIn("@media (max-width:480px)", html)
        self.assertIn("flex-wrap:wrap", html)

    def test_user_input_is_escaped(self):
        _, html = get("attendees=%22%3E%3Cscript%3Ealert(1)%3C/script%3E&start=%3Cb%3E")
        self.assertNotIn("<script>alert", html)

    def test_requests_do_not_mutate_catalog(self):
        before = repr(CATALOG)
        for room in CATALOG:
            get(f"attendees=1&room={room.id}&start=700&end=760")
        self.assertEqual(repr(CATALOG), before)

    def test_unknown_path_returns_404(self):
        status, _ = get(path="/admin")
        self.assertTrue(status.startswith("404"))


if __name__ == "__main__":
    unittest.main()
