"""Filtering logic: which rooms satisfy the user's requirements."""


def matches_requirements(room, attendees, required):
    # F1: capacity >= attendees. F2: ALL required items present.
    return room.capacity >= attendees and all(item in room.equipment for item in required)


def filter_rooms(catalog, attendees, required):
    return [room for room in catalog if matches_requirements(room, attendees, required)]
