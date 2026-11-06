# AI evidence appendix

## 1. Tool and model
Tool: Claude (Anthropic), Claude Code environment.
Model: `claude-sonnet-5-5`.

## 2. Baseline written before AI use (Step 2)
Source: `baseline_notes.md` (commit `665a867`, repository `proto_v0`). Copied unchanged:

Baseline Notes
So basically, the booking rules are pretty straightforward:

Time has to be in whole minutes from 0 to 1440.
The start time must be strictly after now.
Max duration is 120 minutes.
If intervals just touch each other, booking is allowed.
If there's even a 1-minute overlap or the room is blocked, you can't book it.
If the end time is before the start or goes past 24 hours, it throws an error message.

As for what's wrong with booking.py when we scale to multiple rooms:
The can_book function is hardcoded for just one room right now.
There's no list or dictionary to keep track of multiple rooms.
The check logic doesn't know anything about room IDs, capacity, or statuses.

What tests we need:
Start equals now -> unavailable
Exactly 120 mins -> available
121 mins -> unavailable
Touching intervals -> available
1-minute overlap -> unavailable
Room blocked -> unavailable
End before start -> error
Time over 1440 -> error

## 3. AI-use record
| # | Tool | Date | Prompt summary | Output used | Problems found | Changes made | Verification sources |
|---|---|---|---|---|---|---|---|
| E1 | Claude | 2026-11-05 | Assignment #04 analysis & planning | Task plan & scope | Assumed JS stack | Switched to Python backend | Assignment slides |
| E2 | Claude | 2026-11-06 | Baseline git/test verification | Commands & status checks | Bash vs PowerShell syntax | Used PowerShell equivalents | Terminal outputs |
| E3 | Claude | 2026-11-06 | Code review of baseline files | Analyzed `booking.py` and test structure | None | Adjusted plan for Python architecture | Source inspection |
| E4 | Claude | 2026-11-06 | Implementation of modules, tests & refactor | Code structure, tests, evidence | Minor comment typo | Fixed comment | Unit tests, fuzz runner, mutation tests |

Prompts and complete responses:
- E1: Request to analyze Assignment #04 requirements and draft a step-by-step execution plan for expanding the room booking system.
- E2: Request to check repository state, verify baseline tests, and run initial fuzz checks.
- E3: Reviewing `booking.py` maintainability bottlenecks and planning the transition to a multi-room catalog.
- E4: Implementing modular architecture (`rooms.py`, `booking.py`, `filtering.py`, `ui.py`, `app.py`), full unit test suites, integration checks, and mutation testing.

## 4. Review decisions
| AI suggestion | Decision | Reason | Affected rule |
|---|---|---|---|
| HTML + JavaScript stack with `node --test` | Modified | Repository is purely Python; kept standard library WSGI + unittest | Task #04 integration check |
| Keep `can_book(start, end, now, blocked, existing)` signature | Accepted | Ensures original tests and fuzz check run without modification | AC1-AC6 preserved |
| Centralized `validate_request` function | Accepted | Eliminates duplicated rule logic across UI and validation | Task #03 |
| Immutable `Room` dataclass with tuple bookings | Accepted | Enforces AC5 (immutability) safely at the type level | AC5, F5 |
| Per-case tests generated from original test cases | Accepted | Clear reporting for every test case | Task #04 |
| Keep blocked rooms in the list with a "blocked" badge | Accepted | F3 states a blocked room is never available, not that it must be hidden | F3 |
| Keep `legacy/app_v1.py` as frozen reference | Accepted | Required for behavior equivalence testing | Task #03 |
| Leave `booking_v1.py` empty | Accepted | Out of scope | none |

My final decisions: I decided to refactor the codebase gradually, module by module, running the test suite after every small change to avoid breaking existing logic. Keeping the original `can_book` signature was crucial so that the baseline fuzz tests continued to pass without a hitch. I also preferred a clean Python WSGI approach over heavy external frameworks because it keeps the app lightweight, transparent, and fully aligned with the course scope.

## 5. Revisions
`v0-initial` -> `v1-feature` -> `v-final`. Final suite: 79 tests passing cleanly.