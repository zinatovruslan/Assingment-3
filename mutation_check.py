"""Test-quality check: inject one realistic bug at a time and confirm the suite fails.

Run: python mutation_check.py     (exit code 0 when every mutant is killed)
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).parent
FILES = ["booking.py", "rooms.py", "filtering.py", "ui.py", "app.py", "fuzz_check.py",
         "test_booking.py", "test_ac_regression.py", "test_filters.py",
         "test_app_integration.py", "test_equivalence.py"]

MUTANTS = [
    ("duration >120 -> >=120", "booking.py", "end - start > MAX_DURATION_MIN", "end - start >= MAX_DURATION_MIN"),
    ("overlap strict -> inclusive", "booking.py", "start < e and s < end", "start <= e and s <= end"),
    ("start>now -> start>=now", "booking.py", "if start <= now:", "if start < now:"),
    ("blocked ignored", "booking.py", "if blocked:", "if False:"),
    ("day end 1440 -> 1439", "booking.py", "end > DAY_END_MIN", "end >= DAY_END_MIN"),
    ("capacity >= -> >", "filtering.py", "room.capacity >= attendees", "room.capacity > attendees"),
    ("ALL equipment -> ANY", "filtering.py", "all(item in room.equipment", "any(item in room.equipment"),
    ("room bookings ignored (F5)", "booking.py", "room.blocked, room.bookings)", "room.blocked, ())"),
    ("selected room param ignored", "app.py", "find_room(matches, _first(params, \"room\")) or (", "None or ("),
    ("empty state removed", "ui.py", "No rooms match these requirements.", ""),
    ("viewport meta removed", "ui.py", "'<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">'", "''"),
]


def main():
    survived = 0
    for name, filename, old, new in MUTANTS:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            for f in FILES:
                shutil.copy(ROOT / f, tmp / f)
            shutil.copytree(ROOT / "legacy", tmp / "legacy")
            source = (tmp / filename).read_text(encoding="utf-8")
            if old not in source:
                print(f"SETUP-ERROR  {name}: pattern not found in {filename}")
                survived += 1
                continue
            (tmp / filename).write_text(source.replace(old, new, 1), encoding="utf-8")
            run = subprocess.run([sys.executable, "-m", "unittest", "discover"], cwd=tmp,
                                 capture_output=True, text=True)
            last = run.stderr.strip().splitlines()[-1]
            status = "KILLED  " if run.returncode != 0 else "SURVIVED"
            survived += run.returncode == 0
            print(f"{status} {name:<34} {filename:<13} ({last})")
    print(f"mutants: {len(MUTANTS)}, survived: {survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
