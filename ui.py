"""UI presentation: pure functions that turn a PageView into HTML."""
from dataclasses import dataclass
from html import escape

TITLE = "Smart Campus Room Availability Checker"

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


@dataclass(frozen=True)
class PageView:
    now: int
    attendees_text: str
    required: tuple
    equipment_options: tuple
    matches: tuple
    selected_id: str
    start_text: str
    end_text: str
    banner: str
    result: tuple  # (css_class, text) or None


def room_label(room):
    return f"{room.name} ({room.id})"


def _minutes(pairs):
    return ", ".join(f"{s}-{e}" for s, e in pairs) or "none"


def _render_requirements(view):
    boxes = "".join(
        f'<label><input type="checkbox" name="equip" value="{escape(item)}"'
        f'{" checked" if item in view.required else ""}> {escape(item)}</label>'
        for item in view.equipment_options
    )
    return (
        "<fieldset><legend>Requirements</legend>"
        f'<label>Attendees <input type="number" name="attendees" min="1" '
        f'value="{escape(view.attendees_text)}"></label>{boxes}</fieldset>'
    )


def _render_room_list(view):
    if view.banner:
        return f'<p class="msg error" role="alert">{escape(view.banner)}</p>'
    if not view.matches:
        return '<p class="msg empty" role="status">No rooms match these requirements.</p>'
    items = "".join(
        f"<li><strong>{escape(room_label(room))}</strong> - capacity {room.capacity}"
        f" - equipment: {escape(', '.join(room.equipment))}"
        f"{' <span class=\"badge\">blocked</span>' if room.blocked else ''}"
        f" - booked: {_minutes(room.bookings)}</li>"
        for room in view.matches
    )
    return f'<ul class="rooms">{items}</ul>'


def _render_check(view):
    if not view.matches:
        return ""
    options = "".join(
        f'<option value="{escape(room.id)}"'
        f'{" selected" if room.id == view.selected_id else ""}>'
        f"{escape(room_label(room))}</option>"
        for room in view.matches
    )
    return (
        "<fieldset><legend>Availability check</legend><div class=\"row\">"
        f'<label>Room <select name="room" onchange="this.form.submit()">{options}</select></label>'
        f'<label>Start (min) <input type="text" inputmode="numeric" name="start" '
        f'value="{escape(view.start_text)}"></label>'
        f'<label>End (min) <input type="text" inputmode="numeric" name="end" '
        f'value="{escape(view.end_text)}"></label></div></fieldset>'
    )


def _render_result(view):
    if view.result is None:
        return ""
    css_class, text = view.result
    return f'<p class="msg {css_class}" role="status" id="result">{escape(text)}</p>'


def render_page(view):
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{TITLE}</title><style>{CSS}</style></head><body><main>"
        f"<h1>{TITLE}</h1>"
        f"<p>Current time (fixed): {view.now} min</p>"
        '<form method="get" action="/">'
        f"{_render_requirements(view)}{_render_room_list(view)}{_render_check(view)}"
        '<button type="submit">Check availability</button></form>'
        f"{_render_result(view)}</main></body></html>"
    )
