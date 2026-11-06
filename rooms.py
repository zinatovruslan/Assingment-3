"""Room data: fictional catalog only. No rules, no filtering, no presentation."""
from dataclasses import dataclass

NOW = 540  # fixed current time, minutes after midnight (09:00)


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    capacity: int
    equipment: tuple
    blocked: bool
    bookings: tuple  # tuple of (start, end) tuples; immutable by construction


CATALOG = (
    Room("R101", "Alpha Lab", 30, ("computers", "projector", "whiteboard"),
         False, ((600, 660), (780, 840))),
    Room("R102", "Beta Studio", 12, ("video-conference", "whiteboard"),
         False, ((570, 630), (900, 960))),
    Room("R103", "Gamma Hall", 80, ("projector", "video-conference"),
         True, ()),
    Room("R104", "Delta Seminar", 20, ("projector", "whiteboard"),
         False, ((660, 720),)),
    Room("R105", "Epsilon Pod", 6, ("video-conference",),
         False, ()),
)

EQUIPMENT = tuple(sorted({item for room in CATALOG for item in room.equipment}))


def find_room(catalog, room_id):
    for room in catalog:
        if room.id == room_id:
            return room
    return None
