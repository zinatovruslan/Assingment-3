# Smart Campus Room Availability Checker (Assignment #04)

Python 3.12+, standard library only. No login, payments, live APIs or database. All data is fictional.

## Setup
No installation. Check the interpreter:

    python --version

## Run the application

    python app.py

Open http://127.0.0.1:8000/ . Stop with Ctrl+C. The current time is fixed at 540 (09:00).

## Run the tests

    python -m unittest discover -v

Single suites:

    python -m unittest -v test_booking          # original Assignment #03 tests (4 tests, 42 cases)
    python -m unittest -v test_ac_regression    # AC1-AC6 regression, one test per case
    python -m unittest -v test_filters          # catalog, F1-F5, boundaries
    python -m unittest -v test_app_integration  # integration / UI behavior through WSGI
    python -m unittest -v test_equivalence      # refactored app == pre-refactor v1 (HTML identical)

Other checks:

    python fuzz_check.py        # differential check against an independent oracle (200000 cases)
    python mutation_check.py    # injects 11 bugs, one at a time; every one must be caught

## Files
| File | Responsibility |
|---|---|
| rooms.py | Room data: fictional catalog (5 rooms), fixed current time |
| booking.py | Booking/availability rules: single source of truth for validation and messages |
| filtering.py | Capacity and equipment filtering (F1, F2) |
| ui.py | HTML presentation (pure functions) |
| app.py | Request parsing, wiring, WSGI server |
| legacy/app_v1.py | Frozen pre-refactor version (v1), used only by test_equivalence.py |
| report.md, ai_appendix.md, test_results.txt | Report, AI evidence, recorded command output |

## Versions (Git)
- `v0-initial`: Assignment #03 code (booking.py, test_booking.py, fuzz_check.py).
- `v1-feature`: catalog, filters and UI in one module (legacy/app_v1.py), before refactoring.
- `v-final`: refactored modules.
