# Sports Score Scraper

A Windows command-line tool that fetches live sports scores from ESPN's public API.

## Supported Leagues

- NBA (Basketball)
- NFL (Football)
- NHL (Hockey)
- NCAAB (College Basketball)
- NCAAF (College Football)

## Installation

No installation required. Just download and run `sports_scraper.exe`.

### Requirements

- Windows 10/11 (64-bit)
- Internet connection

## Usage

Double-click `sports_scraper.exe` to open the interactive prompt:

```
======================================================================
                    SPORTS SCORE SCRAPER
======================================================================

  COMMANDS:
    all sports score today/yesterday/MMDDYY
    nba, nfl, nhl, ncaab, ncaaf score today/yesterday/MMDDYY
    <team> vs <team> score today/yesterday/MMDDYY

  EXAMPLES:
    all sports score yesterday
    nba score today
    nba, nfl, nhl score yesterday
    lakers vs celtics score today

  Type 'quit' to exit
======================================================================

>>
```

### Commands

| Command | Description |
|---------|-------------|
| `all sports score today` | Get all games from all leagues |
| `nba score today` | Get NBA games only |
| `nba, nfl score yesterday` | Get NBA and NFL games |
| `nba, nfl, nhl, ncaab, ncaaf score today` | Get specific leagues |
| `lakers vs celtics score today` | Find specific matchup |
| `cowboys vs eagles score yesterday` | Find specific matchup |
| `quit` | Exit the program |

### Date Formats

| Format | Example | Description |
|--------|---------|-------------|
| `today` | `nba score today` | Current date |
| `yesterday` | `nfl score yesterday` | Previous day |
| `tomorrow` | `nhl score tomorrow` | Next day |
| `MMDDYY` | `nba score 120625` | Dec 6, 2025 |

## Output

### Console Output

```
Fetching: NBA games - December 06, 2025
------------------------------------------------------------------------------------------
League Away                           Score      Home                           Status
------------------------------------------------------------------------------------------
NBA    New Orleans Pelicans           -          Brooklyn Nets                  Scheduled
NBA    Atlanta Hawks                  -          Washington Wizards             Scheduled
NBA    Golden State Warriors          102-110    Cleveland Cavaliers            Final
------------------------------------------------------------------------------------------
Saved 3 games to sports_scores.csv
```

### CSV Output

Results are automatically saved to `sports_scores.csv` in the same folder as the executable:

```csv
date,league,home,away,score,status
2025-12-06,NBA,Brooklyn Nets,New Orleans Pelicans,-,Scheduled
2025-12-06,NBA,Cleveland Cavaliers,Golden State Warriors,102-110,Final
```

## Building from Source

### Requirements

- Python 3.10+
- pip

### Steps

1. Install dependencies:
   ```
   pip install requests pyinstaller
   ```

2. Build the executable:
   ```
   python -m PyInstaller --onefile --console --name sports_scraper sports_scraper.py
   ```

3. Find the executable in the `dist` folder.

## Project Structure

```
ESPN_score scraper/
├── sports_scraper.py      # Main Python script
├── sports_scraper.spec    # PyInstaller configuration
├── README.md              # This file
├── ADR.md                 # Architecture Decision Records
├── dist/
│   ├── sports_scraper.exe # Windows executable
│   └── sports_scores.csv  # Output data
└── build/                 # Build artifacts
```

## Data Source

All data is fetched from ESPN's public API:
- `http://site.api.espn.com/apis/site/v2/sports/`

## License

MIT License - Free to use and modify.
