"""Booking/availability rules. Single source of truth for all request validation."""
MAX_DURATION_MIN = 120
DAY_END_MIN = 1440

MSG_BLOCKED = "Room is blocked"
MSG_TIMES = "Times must be whole minutes from 0 to 1440"
MSG_ORDER = "End must be after start"
MSG_PAST = "Start must be after the current time"
MSG_DURATION = f"Duration cannot exceed {MAX_DURATION_MIN} minutes"
MSG_OVERLAP = "Overlaps an existing booking"


def _is_int(value):
    # bool is a subclass of int, so exclude it.
    return isinstance(value, int) and not isinstance(value, bool)


def validate_request(start, end, now, blocked, existing):
    """Return None if the interval is valid and free, otherwise the reason message."""
    # AC3: a blocked room rejects every request.
    if blocked:
        return MSG_BLOCKED
    # AC1: integer minutes only.
    if not all(_is_int(value) for value in (start, end, now)):
        return MSG_TIMES
    # AC1: non-empty and ordered interval inside the day.
    if start >= end:
        return MSG_ORDER
    if start < 0 or end > DAY_END_MIN:
        return MSG_TIMES
    # AC1: start must be strictly after now.
    if start <= now:
        return MSG_PAST
    # AC2: maximum 120 minutes (exactly 120 allowed).
    if end - start > MAX_DURATION_MIN:
        return MSG_DURATION
    # AC4: any overlap rejects; strict comparisons let touching endpoints pass.
    for s, e in existing:
        if start < e and s < end:
            return MSG_OVERLAP
    return None


def can_book(start, end, now, blocked, existing) -> bool:
    """Return True only if the requested interval is a valid, free booking."""
    return validate_request(start, end, now, blocked, existing) is None


def check_room(room, start, end, now):
    """F5: availability uses the chosen room's own blocked status and bookings."""
    return validate_request(start, end, now, room.blocked, room.bookings)
