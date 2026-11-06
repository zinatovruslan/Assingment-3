"""Differential check: can_book vs an independent minute-by-minute oracle.

Run: python fuzz_check.py
Prints the number of random cases compared and any mismatch.
"""
import copy
import random

from booking import can_book


def oracle(start, end, now, blocked, existing):
    """Independent reference: compares sets of occupied minutes, no interval formulas."""
    if blocked:
        return False
    if not (0 <= start < end <= 1440):
        return False
    if start <= now:
        return False
    if len(range(start, end)) > 120:
        return False
    requested = set(range(start, end))
    for s, e in existing:
        if requested & set(range(s, e)):
            return False
    return True


def main(n=200_000, seed=2026):
    rng = random.Random(seed)
    mismatches = 0
    for _ in range(n):
        now = rng.randint(0, 1439)
        start = rng.randint(-5, 1445)
        end = start + rng.randint(-5, 130)
        blocked = rng.random() < 0.1
        existing = []
        for _ in range(rng.randint(0, 4)):
            s = rng.randint(0, 1400)
            existing.append((s, s + rng.randint(1, 120)))
        snapshot = copy.deepcopy(existing)
        got = can_book(start, end, now, blocked, existing)
        want = oracle(start, end, now, blocked, existing)
        if got is not want or existing != snapshot:
            mismatches += 1
            if mismatches <= 5:
                print("MISMATCH", start, end, now, blocked, snapshot, got, want)
    print(f"compared {n} random cases, mismatches: {mismatches}")


if __name__ == "__main__":
    main()   
