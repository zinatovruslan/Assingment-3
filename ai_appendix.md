# AI evidence appendix

## 1. Tool and model
Tool: Claude (Anthropic), Claude Code environment.
Model: configured identifier `claude-sonnet-5-5`. The serving model may differ and can change during a session. [[PASTE: model name shown in your Claude interface]]

## 2. Baseline written before AI use (Step 2)
Source: `baseline_notes.md` (commit `665a867`, repository `proto_v0`). Copied unchanged:

```
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
```

## 3. AI-use record
| # | Tool | Date | Prompt summary | Output used | Problems found | Changes made | Verification sources |
|---|---|---|---|---|---|---|---|
| E1 | Claude | 2026-11-05 | Master prompt (file `c54a27e5-attachment.txt`) plus the Assignment #04 PDF: extract requirements, deadline, deliverables, plan | Requirement checklist, deadline conversion (08.11.2026 23:59:59, UTC+5 assumed), execution plan | Assumed an HTML + JavaScript stack and `node --test` | Stack changed to Python after the repository listing was seen (E3) | Assignment #04 slides: Starting point and scope, New feature, Task #01-#06, Submission details |
| E2 | Claude | 2026-11-06 | Baseline snapshot commands | Git tag check, file list, test and fuzz commands | Bash `xargs` given for PowerShell; a pytest fallback step would have overwritten `baseline_tests.txt` | PowerShell equivalents; files recreated | Command output pasted in the session: `git show --stat v0-initial`, `Ran 4 tests ... OK`, `mismatches: 0` |
| E3 | Claude | 2026-11-06 | Review of the baseline output and the source files (`booking.py`, `test_booking.py`, `fuzz_check.py`) | Reading of the code: 42 cases in 1 unittest test, bool-only result, unvalidated `existing` | none beyond E1 stack error | Plan adjusted to Python, per-case tests, reason-returning validation | Source files; run of `can_book(610, 650, 540, False, [(700, 600)])` returned True; Assignment #03 report assumption 2 |
| E4 | Claude | 2026-11-06 | Build the package: catalog, filters, UI, tests, refactor, evidence | `rooms.py`, `booking.py`, `filtering.py`, `ui.py`, `app.py`, `legacy/app_v1.py`, 4 new test files, `mutation_check.py`, docs, screenshots, diagrams | Misleading comment in `test_filters.py` | Comment corrected | `python -m unittest discover -v` (79 OK); `fuzz_check.py` (0 mismatches); `mutation_check.py` (11 killed); `test_equivalence.py`; Playwright measurements; grep for duplicated logic |

Prompts and complete responses: [[PASTE: full text of each exchange E1-E4 from the chat, unchanged]].

## 4. Review decisions
| AI suggestion | Decision | Reason | Affected rule |
|---|---|---|---|
| HTML + JavaScript stack with `node --test` | Modified | Repository is Python (`git show --stat v0-initial`); stdlib WSGI + unittest | Task #04 integration check |
| Keep `can_book(start, end, now, blocked, existing)` signature | Accepted | Original tests and fuzz check run unchanged | AC1-AC6 preserved |
| One reason-returning `validate_request`; `can_book` as wrapper | Accepted | Removes 5 duplicated rule copies | Task #03 |
| Immutable `Room` with tuple bookings | Accepted | AC5 enforced by type; F5 safe by construction | AC5, F5 |
| Per-case tests generated from `test_booking.CASES`, original file untouched | Accepted | Reports every case; no edit of baseline | Task #04 |
| Keep blocked rooms in the list with a badge | Accepted, confirm yourself | F3 says a blocked room cannot be reported as available, not that it is hidden | F3 |
| Keep `legacy/app_v1.py` as frozen reference | Accepted | Needed for the behavior-equivalence test | Task #03 |
| Leave `booking_v1.py` empty and untouched | Accepted | Out of scope | none |

Decisions that are yours to record in your own words: [[MY OWN WORDS: your final decisions and why, 3-5 sentences]].

## 5. Revisions
v0-initial -> v1-feature (feature in one module, `legacy/app_v1.py`) -> v-final (5 modules). One change per step with test rerun; final run: 79 tests OK.
