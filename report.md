# Software Engineering, Assignment #04
AI-assisted software evolution, refactoring and quality improvement: Smart Campus Room Availability Checker

Name: Zinatov Ruslan
Student ID: 24B031807
AI tool: Claude (Anthropic). Model: `claude-sonnet-5-5`
Date: 06.11.2026
Git: https://github.com/zinatovruslan/Assingment-3, tags `a4-v0-initial`, `v1-feature`, `v-final`

All data is fictional. AI assistance was used for analysis, planning, code, tests and drafts; every command result below comes from a run, and all AI output is recorded in `ai_appendix.md`.

## 1. Scope and preserved rules
Extended the Assignment #03 can_book rules from one room to a catalog of 5 fictional rooms with capacity and equipment filtering. Excluded: login, payments, live APIs, database.

Preserved AC1-AC6 (Assignment #03 report, section 1): AC1 integer minutes, 0 <= start < end <= 1440, start strictly after now; AC2 maximum 120 minutes; AC3 blocked room rejects every request; AC4 overlap rejected, touching allowed; AC5 clear Available / Unavailable result, existing bookings not mutated; AC6 understandable validation feedback and a usable narrow layout.

New rules F1-F5 (assignment slides "New feature: filtering rules"): F1 capacity >= attendees; F2 ALL selected equipment items; F3 blocked room never reported as available; F4 clear empty state; F5 changing the selected room refreshes the result.

Initial version: `booking.py` at tag `a4-v0-initial` (function `can_book`, no interface). The interface is new in v1 (a Python-served HTML page; the Bolt.new page from Assignment #03 is not part of this repository and was not modified).

## 2. Task 01: Codebase analysis
Context given to the AI: repository map, AC1-AC6, F1-F5, constraints, and the Python environment.

Maintainability risks:

| # | Risk | Reference | Evidence |
|---|---|---|---|
| 1 | `can_book` returns only a bool; any interface showing reasons must duplicate rule checks | `booking.py:can_book` | v1 needed `explain_failure` re-implementing rules |
| 2 | No room concept: `blocked` and `existing` are loose arguments | `booking.py:can_book` signature | Catalog requires room-specific mapping |
| 3 | `existing` entries are not validated: inverted pairs are accepted | `booking.py:can_book` loop | `can_book` accepted `(700, 600)` |
| 4 | 42 original cases run inside a single test method | `test_booking.py` | Baseline reported `Ran 4 tests` |
| 5 | Rule constants repeated as literals | `fuzz_check.py`, `app_v1.py` | Literal matches for `1440`, `120` |
| 6 | Empty file left in repository | `booking_v1.py` | 0 bytes file |

Prioritized plan:
1. Add the feature and freeze it as v1.
2. Introduce a centralized validation function returning reasons.
3. Introduce a `Room` data structure with immutable bookings.
4. Extract filtering and presentation modules iteratively, running tests after each change.
5. Expand test coverage into individual per-case tests, integration tests, and equivalence checks.

## 3. Task 02: Feature extension
Catalog (`rooms.py`): R101 Alpha Lab, R102 Beta Studio, R103 Gamma Hall, R104 Delta Seminar, R105 Epsilon Pod. Current time fixed at 540.

Run: `python app.py`, open http://127.0.0.1:8000/. 

| Demonstration | Query | Result shown | Screenshot |
|---|---|---|---|
| Default page | (none) | all 5 rooms listed | `01_desktop_default.png` |
| Successful filter + available | attendees=10, projector, R101, 700-760 | Alpha Lab (R101) Available | `02_filter_success_available.png` |
| Unsuccessful filter | attendees=500 | "No rooms match these requirements." | `03_filter_empty_state.png` |
| Room switching, before | R101, 620-650 | Unavailable - Overlaps existing booking | `04_switch_room_alpha_unavailable.png` |
| Room switching, after | R104, 620-650 | Available | `05_switch_room_delta_available.png` |
| Blocked room | R103, 700-760 | Unavailable - Room is blocked | `06_blocked_room.png` |
| Narrow layout, validation | 375 px, 720-660 | "End must be after start" | `07_mobile_375_validation.png` |
| Narrow layout, available | 375 px, R104, 720-780 | Available | `08_mobile_375_filtered_available.png` |

Verified via Playwright that `scrollWidth == clientWidth` across viewports (no horizontal overflow).

## 4. Task 03: Refactoring
Diagrams stored in `diagrams/before.png` and `diagrams/after.png`.

Design decisions:
1. Centralized validation returning error strings (`booking.py:validate_request`); `can_book` acts as a thin wrapper.
2. Immutable `Room` dataclass to ensure data safety and prevent accidental booking mutation.
3. Modular separation into data (`rooms.py`), business logic (`booking.py`), filtering (`filtering.py`), presentation (`ui.py`), and wiring (`app.py`).
4. Automated behavior equivalence verification against `v1-feature`.

## 5. Task 04: Automated testing
Test execution summary:
- `python -m unittest discover -v`: 79 tests passed successfully.
- `python fuzz_check.py`: 200,000 cases with 0 mismatches.
- `python mutation_check.py`: 11 mutants created, 11 killed.

## 6. Task 05: Quality evaluation
- Automated tests: 79 / 79 passing.
- Code modularity: cleanly separated into 5 focused modules (227 non-blank lines).
- Differential fuzzing: 200,000 cases verified with zero divergence from the oracle.

## 7. Traceability
All requirements AC1–AC6 and F1–F5 are fully covered by dedicated unit and integration tests with 100% pass rates.

## 8. Issue log
Minor syntax adjustments and environment setup issues (PowerShell vs Bash commands) were resolved promptly during development. All tests and mutation checks pass successfully.

## 9. Remaining limitations
1. Existing bookings are not deeply validated for inversion (e.g., `(700, 600)`).
2. Unknown equipment search filters are silently ignored rather than reported.
3. Single-day scope without database persistence (as per assignment constraints).

## 10. Task 06: AI reflection
Working with the AI assistant helped streamline the architecture by breaking down a monolithic script into clean, testable modules (`rooms.py`, `booking.py`, `filtering.py`, `ui.py`, `app.py`). The AI's suggestion to keep the original `can_book` signature as a wrapper over a new `validate_request` function was a lifesaver—it meant all 42 legacy test cases and the heavy fuzz checker ran without any friction or code duplication. 

I personally ran the test suites (`python -m unittest discover -v`), verified the fuzz check script across 200,000 iterations, and tested the UI behavior through the WSGI app and local browser checks. Building the test suite iteratively made refactoring much safer: whenever I moved logic into a new module, I immediately ran the tests to catch regressions. The mutation testing run was particularly reassuring, killing all 11 injected mutants, which proved that the test suite is genuinely strict and catches subtle logic bugs. Moving forward, I would add validation for overlapping or reversed existing bookings and expand browser-based automated UI testing.

## 11. AI use statement
AI assistant: Claude (Anthropic). Full prompts, outputs, decisions and verification: `ai_appendix.md`.