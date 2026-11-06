"""Version v1 (pre-refactor): room catalog, filters, rules and HTML in one module.

Frozen behavioral reference. Used only by test_equivalence.py.
"""
import re
from html import escape

from booking import can_book  # v0 boolean rule, unchanged

NOW = 540

ROOMS = [
    {"id": "R101", "name": "Alpha Lab", "capacity": 30,
     "equipment": ["computers", "projector", "whiteboard"],
     "blocked": False, "bookings": [(600, 660), (780, 840)]},
    {"id": "R102", "name": "Beta Studio", "capacity": 12,
     "equipment": ["video-conference", "whiteboard"],
     "blocked": False, "bookings": [(570, 630), (900, 960)]},
    {"id": "R103", "name": "Gamma Hall", "capacity": 80,
     "equipment": ["projector", "video-conference"],
     "blocked": True, "bookings": []},
    {"id": "R104", "name": "Delta Seminar", "capacity": 20,
     "equipment": ["projector", "whiteboard"],
     "blocked": False, "bookings": [(660, 720)]},
    {"id": "R105", "name": "Epsilon Pod", "capacity": 6,
     "equipment": ["video-conference"],
     "blocked": False, "bookings": []},
]

EQUIPMENT = sorted({item for room in ROOMS for item in room["equipment"]})

CSS = """
body{font-family:system-ui,sans-serif;margin:0;padding:16px;background:#f6f7f9;color:#1b1f23}
main{max-width:720px;margin:0 auto}
fieldset{border:1px solid #c8ccd0;border-radius:8px;margin:0 0 16px;padding:12px;min-width:0}
label{display:block;margin:8px 0}
input,select,button{font:inherit;padding:8px;max-width:100%;box-sizing:border-box}
.row{display:flex;flex-wrap:wrap;gap:12px}
.rooms{list-style:none;padding:0;margin:0}
.rooms li{background:#fff;border:1px solid #d5d9dd;border-radius:8px;padding:10px;margin:8px 0;overflow-wrap:anywhere}
.badge{background:#b42318;color:#fff;border-radius:4px;padding:2px 6px;font-size:.85em}
.msg{padding:12px;border-radius:8px;font-weight:600;overflow-wrap:anywhere;margin:0 0 16px}
.available{background:#e3f6e8;border:1px solid #1e7a3c}
.unavailable,.error{background:#fde8e8;border:1px solid #b42318}
.empty{background:#fff4d6;border:1px solid #8a6100}
@media (max-width:480px){.row>*{flex:1 1 100%}}
""".strip()


def filter_rooms(attendees, required):
    result = []
    for room in ROOMS:
        if room["capacity"] >= attendees and all(i in room["equipment"] for i in required):
            result.append(room)
    return result


def explain_failure(start, end, now, room):
    """Reason text for a rejected request (re-implements the can_book checks)."""
    if room["blocked"]:
        return "Room is blocked"
    if start >= end:
        return "End must be after start"
    if start < 0 or end > 1440:
        return "Times must be whole minutes from 0 to 1440"
    if start <= now:
        return "Start must be after the current time"
    if end - start > 120:
        return "Duration cannot exceed 120 minutes"
    for s, e in room["bookings"]:
        if start < e and s < end:
            return "Overlaps an existing booking"
    return None


def handle(params):
    attendees_text = params.get("attendees", ["1"])[0]
    required = [i for i in params.get("equip", []) if i in EQUIPMENT]
    start_text = params.get("start", [""])[0]
    end_text = params.get("end", [""])[0]
    room_param = params.get("room", [""])[0]

    banner = ""
    matches = []
    t = attendees_text.strip()
    attendees = int(t) if re.fullmatch(r"-?[0-9]+", t) else None
    if attendees is None or attendees < 1:
        banner = "Attendees must be a whole number of at least 1"
    else:
        matches = filter_rooms(attendees, required)

    selected = None
    for room in matches:
        if room["id"] == room_param:
            selected = room
    if selected is None and matches:
        selected = matches[0]

    result_html = ""
    if selected and (start_text.strip() or end_text.strip()):
        ts, te = start_text.strip(), end_text.strip()
        start = int(ts) if re.fullmatch(r"-?[0-9]+", ts) else None
        end = int(te) if re.fullmatch(r"-?[0-9]+", te) else None
        label = f"{selected['name']} ({selected['id']})"
        if start is None or end is None:
            reason = "Times must be whole minutes from 0 to 1440"
        elif can_book(start, end, NOW, selected["blocked"], selected["bookings"]):
            reason = None
        else:
            reason = explain_failure(start, end, NOW, selected)
        if reason is None:
            text = f"{label}: Available for {start}-{end}"
            result_html = f'<p class="msg available" role="status" id="result">{escape(text)}</p>'
        else:
            text = f"{label}: Unavailable - {reason}"
            result_html = f'<p class="msg unavailable" role="status" id="result">{escape(text)}</p>'

    boxes = ""
    for item in EQUIPMENT:
        checked = " checked" if item in required else ""
        boxes += (f'<label><input type="checkbox" name="equip" value="{escape(item)}"'
                  f'{checked}> {escape(item)}</label>')
    requirements = ("<fieldset><legend>Requirements</legend>"
                    f'<label>Attendees <input type="number" name="attendees" min="1" '
                    f'value="{escape(attendees_text)}"></label>{boxes}</fieldset>')

    if banner:
        room_list = f'<p class="msg error" role="alert">{escape(banner)}</p>'
    elif not matches:
        room_list = '<p class="msg empty" role="status">No rooms match these requirements.</p>'
    else:
        items = ""
        for room in matches:
            blocked = ' <span class="badge">blocked</span>' if room["blocked"] else ""
            booked = ", ".join(f"{s}-{e}" for s, e in room["bookings"]) or "none"
            items += (f"<li><strong>{escape(room['name'] + ' (' + room['id'] + ')')}</strong>"
                      f" - capacity {room['capacity']}"
                      f" - equipment: {escape(', '.join(room['equipment']))}"
                      f"{blocked} - booked: {booked}</li>")
        room_list = f'<ul class="rooms">{items}</ul>'

    check = ""
    if matches:
        options = ""
        for room in matches:
            sel = " selected" if selected and room["id"] == selected["id"] else ""
            options += (f'<option value="{escape(room["id"])}"{sel}>'
                        f'{escape(room["name"] + " (" + room["id"] + ")")}</option>')
        check = ('<fieldset><legend>Availability check</legend><div class="row">'
                 f'<label>Room <select name="room" onchange="this.form.submit()">{options}</select></label>'
                 f'<label>Start (min) <input type="text" inputmode="numeric" name="start" '
                 f'value="{escape(start_text)}"></label>'
                 f'<label>End (min) <input type="text" inputmode="numeric" name="end" '
                 f'value="{escape(end_text)}"></label></div></fieldset>')

    title = "Smart Campus Room Availability Checker"
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f"<title>{title}</title><style>{CSS}</style></head><body><main>"
            f"<h1>{title}</h1>"
            f"<p>Current time (fixed): {NOW} min</p>"
            '<form method="get" action="/">'
            f"{requirements}{room_list}{check}"
            '<button type="submit">Check availability</button></form>'
            f"{result_html}</main></body></html>")
