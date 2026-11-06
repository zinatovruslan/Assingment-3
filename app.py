"""Application wiring: parse request, call filtering and rules, hand a view to the UI.

Run: python app.py   (serves http://127.0.0.1:8000/)
"""
import re
from wsgiref.simple_server import make_server

from booking import MSG_TIMES, check_room
from filtering import filter_rooms
from rooms import CATALOG, EQUIPMENT, NOW, find_room
from ui import PageView, render_page, room_label

MSG_ATTENDEES = "Attendees must be a whole number of at least 1"


def parse_whole_number(text):
    """Return an int for ASCII whole-number text, otherwise None."""
    text = text.strip()
    return int(text) if re.fullmatch(r"-?[0-9]+", text) else None


def _first(params, name, default=""):
    return params.get(name, [default])[0]


def handle(params, catalog=CATALOG, now=NOW):
    attendees_text = _first(params, "attendees", "1")
    required = tuple(item for item in params.get("equip", []) if item in EQUIPMENT)
    start_text = _first(params, "start")
    end_text = _first(params, "end")

    attendees = parse_whole_number(attendees_text)
    banner = ""
    matches = ()
    if attendees is None or attendees < 1:
        banner = MSG_ATTENDEES
    else:
        matches = tuple(filter_rooms(catalog, attendees, required))

    selected = find_room(matches, _first(params, "room")) or (matches[0] if matches else None)

    result = None
    if selected and (start_text.strip() or end_text.strip()):
        start, end = parse_whole_number(start_text), parse_whole_number(end_text)
        reason = MSG_TIMES if start is None or end is None else check_room(selected, start, end, now)
        label = room_label(selected)
        if reason is None:
            result = ("available", f"{label}: Available for {start}-{end}")
        else:
            result = ("unavailable", f"{label}: Unavailable - {reason}")

    return render_page(PageView(
        now=now, attendees_text=attendees_text, required=required,
        equipment_options=EQUIPMENT, matches=matches,
        selected_id=selected.id if selected else "",
        start_text=start_text, end_text=end_text, banner=banner, result=result))


def application(environ, start_response):
    from urllib.parse import parse_qs
    if environ.get("REQUEST_METHOD") != "GET" or environ.get("PATH_INFO", "/") != "/":
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Not found"]
    body = handle(parse_qs(environ.get("QUERY_STRING", ""))).encode("utf-8")
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"),
                              ("Content-Length", str(len(body)))])
    return [body]


if __name__ == "__main__":
    with make_server("127.0.0.1", 8000, application) as server:
        print("Serving on http://127.0.0.1:8000/")
        server.serve_forever()
