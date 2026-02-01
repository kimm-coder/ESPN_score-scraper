# Architecture Decision Records (ADR)

## ADR-001: Use ESPN Public API

**Status:** Accepted

**Context:**
We needed a reliable data source for live sports scores across multiple leagues (NBA, NFL, NHL, NCAAB, NCAAF).

**Decision:**
Use ESPN's public scoreboard API endpoints:
- `http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard`
- `http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard`
- `http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard`
- `http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard`
- `http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard`

**Consequences:**
- Pros: Free, no API key required, reliable data, supports date queries
- Cons: No official documentation, API could change without notice, rate limits unknown

---

## ADR-002: Python with Requests Library

**Status:** Accepted

**Context:**
Needed to choose a programming language and HTTP library for making API calls.

**Decision:**
Use Python 3 with the `requests` library for HTTP requests.

**Consequences:**
- Pros: Simple syntax, widely supported, easy to package as executable
- Cons: Requires Python runtime (mitigated by PyInstaller packaging)

---

## ADR-003: PyInstaller for Windows Executable

**Status:** Accepted

**Context:**
Users should be able to run the application without installing Python or dependencies.

**Decision:**
Use PyInstaller with `--onefile` flag to create a single standalone Windows executable.

**Consequences:**
- Pros: Single file distribution, no dependencies required, runs on any Windows PC
- Cons: Larger file size (~12MB), slower startup time, must rebuild for updates

---

## ADR-004: CSV for Data Storage

**Status:** Accepted

**Context:**
Needed a simple way to persist scraped data for future reference and analysis.

**Decision:**
Save results to a CSV file (`sports_scores.csv`) in the same directory as the executable.

**Consequences:**
- Pros: Human-readable, easy to import into Excel/Google Sheets, no database setup
- Cons: No deduplication (same query appends duplicate records), file grows over time

---

## ADR-005: Interactive Command-Line Interface

**Status:** Accepted

**Context:**
Initially the application closed immediately after execution, making it difficult to use.

**Decision:**
Implement an interactive mode with a command prompt that stays open until the user types `quit`.

**Consequences:**
- Pros: User-friendly, can run multiple queries in one session, shows help on startup
- Cons: Slightly more complex code, requires input parsing

---

## ADR-006: Natural Language Query Parsing

**Status:** Accepted

**Context:**
Users should be able to type commands in a flexible, human-readable format.

**Decision:**
Parse queries using string matching and regex to extract:
- League names (nba, nfl, nhl, ncaab, ncaaf)
- Dates (today, yesterday, tomorrow, MMDDYY format)
- Team names for "vs" queries

**Consequences:**
- Pros: Flexible input (e.g., "nba score today", "lakers vs celtics score yesterday")
- Cons: May misinterpret ambiguous queries, limited error handling

---

## ADR-007: Fuzzy Team Name Matching

**Status:** Accepted

**Context:**
Users may not type exact team names when searching for specific matchups.

**Decision:**
Use Python's `difflib.SequenceMatcher` for fuzzy string matching with a 0.6 similarity threshold.

**Consequences:**
- Pros: Matches partial names (e.g., "lakers" matches "Los Angeles Lakers")
- Cons: May return false positives for similar team names

---

## ADR-008: Support Multiple Leagues in Single Query

**Status:** Accepted

**Context:**
Users often want to see scores from multiple leagues at once.

**Decision:**
Allow comma-separated league names (e.g., "nba, nfl, nhl score today") and an "all sports" command.

**Consequences:**
- Pros: Convenient for users, reduces number of queries needed
- Cons: Longer response time when fetching multiple leagues

---

## ADR-009: Append-Only CSV Storage

**Status:** Accepted

**Context:**
Needed to decide how to handle repeated queries that return the same data.

**Decision:**
Always append new results to the CSV file without checking for duplicates.

**Consequences:**
- Pros: Simple implementation, preserves historical data, fast writes
- Cons: Can accumulate duplicate records, requires manual cleanup

---

## ADR-010: Minimal Dependencies

**Status:** Accepted

**Context:**
Wanted to keep the application simple and reduce potential points of failure.

**Decision:**
Only use one external dependency (`requests`). All other functionality uses Python standard library.

**Consequences:**
- Pros: Smaller executable, fewer security vulnerabilities, easier maintenance
- Cons: Less feature-rich (no advanced date parsing, no database, no GUI)

---

## ADR-011: Error Handling Strategy

**Status:** Accepted

**Context:**
Network requests can fail due to connectivity issues or API changes.

**Decision:**
- Use 10-second timeout for API requests
- Display warning messages for failed requests but continue with other leagues
- Gracefully handle keyboard interrupts (Ctrl+C)

**Consequences:**
- Pros: Application doesn't crash on errors, user is informed of issues
- Cons: Partial data may be returned if some leagues fail

---

## ADR-012: Date Format Support

**Status:** Accepted

**Context:**
Users need flexibility in specifying dates for historical scores.

**Decision:**
Support multiple date formats:
- Relative: `today`, `yesterday`, `tomorrow`
- MMDDYY: `120625` (December 6, 2025)
- Default to today if no date specified

**Consequences:**
- Pros: Flexible input, common date format
- Cons: MMDDYY format may be unfamiliar to non-US users
