MAX_DURATION_MIN = 120
DAY_END_MIN = 1440


def can_book(start, end, now, blocked, existing) -> bool:
    """Return True only if the requested interval is a valid, free booking."""
    # AC3: a blocked room rejects every request.
    if blocked:
        return False

    # Type guard: only real ints are accepted; bool is a subclass of int, so exclude it.
    for value in (start, end, now):
        if not isinstance(value, int) or isinstance(value, bool):
            return False

    # AC1: interval must lie within the day and be non-empty and ordered.
    if not (0 <= start < end <= DAY_END_MIN):
        return False

    # AC1: start must be strictly after now.
    if start <= now:
        return False

    # AC2: maximum duration is 120 minutes (exactly 120 is allowed).
    if end - start > MAX_DURATION_MIN:
        return False

    # AC4: reject any overlap; strict comparisons let touching endpoints pass.
    for s, e in existing:
        if start < e and s < end:
            return False

    # All checks passed.
    return True