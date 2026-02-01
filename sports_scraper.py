#!/usr/bin/env python3
"""
Sports Score Scraper - Interactive Mode
Supports:
    game scores nba, nfl, nhl, ncaab, ncaaf MMDDYY/Yesterday/Today
    team vs team score MMDDYY
    team vs team score today
    team vs team score yesterday
"""

import requests
import csv
import sys
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from difflib import SequenceMatcher

# ESPN API endpoints
APIS = {
    "nba": "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    "nfl": "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
    "nhl": "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard",
    "ncaab": "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard",
    "ncaaf": "http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard",
}

# Get directory where the executable/script is located
if getattr(sys, 'frozen', False):
    APP_DIR = Path(os.path.dirname(sys.executable))
else:
    APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

CSV_FILE = APP_DIR / "sports_scores.csv"


def parse_query(query: str) -> dict:
    """Parse user query to extract league, week, and date."""
    query = query.lower().strip()

    # Detect league
    league = None
    for lg in APIS.keys():
        if lg in query:
            league = lg
            break

    # Check for week (NFL/NCAAF)
    week = None
    week_match = re.search(r'week\s*(\d{1,2})', query)
    if week_match:
        week = int(week_match.group(1))

    # Extract date
    date = None
    if "today" in query:
        date = datetime.now()
    elif "yesterday" in query:
        date = datetime.now() - timedelta(days=1)
    elif "tomorrow" in query:
        date = datetime.now() + timedelta(days=1)
    else:
        # Look for MMDDYY format
        date_match = re.search(r'(\d{6})', query)
        if date_match:
            date_str = date_match.group(1)
            try:
                date = datetime.strptime(date_str, "%m%d%y")
            except ValueError:
                pass
        # Look for YYYY-MM-DD format
        if not date:
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', query)
            if date_match:
                try:
                    date = datetime.strptime(date_match.group(0), "%Y-%m-%d")
                except ValueError:
                    pass

    # Default to today if no date and no week
    if not date and not week:
        date = datetime.now()

    return {"league": league, "week": week, "date": date}


def fetch_games(league: str = None, week: int = None, date: datetime = None) -> list:
    """Fetch games from ESPN API."""
    all_games = []

    # Determine which leagues to fetch
    leagues_to_fetch = [league] if league else list(APIS.keys())

    for lg in leagues_to_fetch:
        if lg not in APIS:
            continue

        url = APIS[lg]
        params = {}

        # Week-based query (NFL/NCAAF only)
        if week and lg in ["nfl", "ncaaf"]:
            params["week"] = week
            params["seasontype"] = 2  # Regular season
        elif date:
            params["dates"] = date.strftime("%Y%m%d")
        else:
            params["dates"] = datetime.now().strftime("%Y%m%d")

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for event in data.get("events", []):
                game_info = parse_game(event, lg)
                if game_info:
                    all_games.append(game_info)
        except requests.RequestException as e:
            print(f"Warning: Could not fetch {lg.upper()} data: {e}")

    return all_games


def parse_game(event: dict, league: str) -> dict:
    """Parse a single game event."""
    try:
        competition = event.get("competitions", [{}])[0]
        competitors = competition.get("competitors", [])

        if len(competitors) != 2:
            return None

        home_team = away_team = None
        home_score = away_score = "0"

        for comp in competitors:
            team_data = comp.get("team", {})
            team_name = team_data.get("displayName", team_data.get("name", "Unknown"))
            score = comp.get("score", "0")

            if comp.get("homeAway") == "home":
                home_team = team_name
                home_score = score
            else:
                away_team = team_name
                away_score = score

        status = event.get("status", {}).get("type", {})
        status_name = status.get("name", "Unknown")

        if status_name == "STATUS_FINAL":
            game_status = "Final"
        elif status_name == "STATUS_IN_PROGRESS":
            game_status = "Live"
        else:
            game_status = "Scheduled"

        # Format score string
        if game_status == "Final":
            score_str = f"{away_score}-{home_score}"
        elif game_status == "Live":
            score_str = f"{away_score}-{home_score}"
        else:
            score_str = "-"

        return {
            "league": league.upper(),
            "home": home_team,
            "away": away_team,
            "score": score_str,
            "status": game_status,
            "date": event.get("date", "")[:10],
        }
    except Exception:
        return None


def save_to_csv(games: list):
    """Save games to CSV file."""
    if not games:
        return

    file_exists = CSV_FILE.exists()

    fieldnames = ["date", "league", "home", "away", "score", "status"]

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        for game in games:
            writer.writerow({
                "date": game["date"],
                "league": game["league"],
                "home": game["home"],
                "away": game["away"],
                "score": game["score"],
                "status": game["status"],
            })


def print_games(games: list):
    """Print games in a formatted table."""
    if not games:
        print("No games found.")
        return

    # Print header
    print(f"{'League':<6} {'Away':<30} {'Score':<10} {'Home':<30} {'Status'}")
    print("-" * 90)

    for game in games:
        print(f"{game['league']:<6} {game['away']:<30} {game['score']:<10} {game['home']:<30} {game['status']}")


def fuzzy_match(name1: str, name2: str) -> float:
    """Calculate similarity ratio between two team names."""
    name1 = name1.lower().strip()
    name2 = name2.lower().strip()
    return SequenceMatcher(None, name1, name2).ratio()


def find_team_game(games: list, team1: str, team2: str = None) -> list:
    """Find games matching team name(s)."""
    matched = []
    team1 = team1.lower().strip()
    team2 = team2.lower().strip() if team2 else None

    for game in games:
        home = game['home'].lower()
        away = game['away'].lower()

        # Check if team1 matches either home or away
        team1_match = (team1 in home or team1 in away or
                       fuzzy_match(team1, home) > 0.6 or
                       fuzzy_match(team1, away) > 0.6)

        if team1_match:
            if team2:
                # Check if team2 also matches
                team2_match = (team2 in home or team2 in away or
                              fuzzy_match(team2, home) > 0.6 or
                              fuzzy_match(team2, away) > 0.6)
                if team2_match:
                    matched.append(game)
            else:
                matched.append(game)

    return matched


def parse_multi_league_query(query: str) -> dict:
    """Parse query with multiple leagues like 'nba, nfl, nhl score today'."""
    query_lower = query.lower().strip()

    # Remove "score" keyword
    query_lower = query_lower.replace("score", "").strip()

    # Extract date first
    date = None
    if "today" in query_lower:
        date = datetime.now()
    elif "yesterday" in query_lower:
        date = datetime.now() - timedelta(days=1)
    elif "tomorrow" in query_lower:
        date = datetime.now() + timedelta(days=1)
    else:
        # Look for MMDDYY format
        date_match = re.search(r'(\d{6})', query_lower)
        if date_match:
            date_str = date_match.group(1)
            try:
                date = datetime.strptime(date_str, "%m%d%y")
            except ValueError:
                pass

    if not date:
        date = datetime.now()

    # Find all leagues mentioned
    leagues = []
    for lg in APIS.keys():
        if lg in query_lower:
            leagues.append(lg)

    return {"leagues": leagues, "date": date}


def parse_team_query(query: str) -> dict:
    """Parse team vs team query."""
    query = query.lower().strip()

    # Extract date first
    date = None
    if "today" in query:
        date = datetime.now()
        query = query.replace("today", "")
    elif "yesterday" in query:
        date = datetime.now() - timedelta(days=1)
        query = query.replace("yesterday", "")
    elif "tomorrow" in query:
        date = datetime.now() + timedelta(days=1)
        query = query.replace("tomorrow", "")
    else:
        # Look for MMDDYY format
        date_match = re.search(r'(\d{6})', query)
        if date_match:
            date_str = date_match.group(1)
            try:
                date = datetime.strptime(date_str, "%m%d%y")
                query = query.replace(date_str, "")
            except ValueError:
                pass

    if not date:
        date = datetime.now()

    # Remove "score" keyword
    query = query.replace("score", "").strip()

    # Parse team vs team
    if " vs " in query:
        parts = query.split(" vs ")
        team1 = parts[0].strip()
        team2 = parts[1].strip() if len(parts) > 1 else None
        return {"team1": team1, "team2": team2, "date": date}
    elif " v " in query:
        parts = query.split(" v ")
        team1 = parts[0].strip()
        team2 = parts[1].strip() if len(parts) > 1 else None
        return {"team1": team1, "team2": team2, "date": date}

    # Single team search
    return {"team1": query.strip(), "team2": None, "date": date}


def print_help():
    """Print help/usage information."""
    print()
    print("=" * 70)
    print("                    SPORTS SCORE SCRAPER")
    print("=" * 70)
    print()
    print("COMMANDS:")
    print("-" * 70)
    print()
    print("  GAME SCORES:")
    print("    <leagues> score <date>")
    print()
    print("    Examples:")
    print("      nba score today")
    print("      nba, nfl, nhl score today")
    print("      nba, nfl, nhl, ncaab, ncaaf score yesterday")
    print("      nfl score 120625")
    print()
    print("  TEAM VS TEAM:")
    print("    <team> vs <team> score <date>")
    print()
    print("    Examples:")
    print("      lakers vs celtics score today")
    print("      cowboys vs eagles score yesterday")
    print("      chiefs vs bills score 120125")
    print()
    print("  OTHER COMMANDS:")
    print("    help     - Show this help message")
    print("    quit     - Exit the program")
    print()
    print("  LEAGUES: nba, nfl, nhl, ncaab, ncaaf")
    print("  DATES:   today, yesterday, tomorrow, MMDDYY (e.g., 120625)")
    print("=" * 70)
    print()


def interactive_mode():
    """Run the scraper in interactive mode."""
    print()
    print("=" * 70)
    print("                    SPORTS SCORE SCRAPER")
    print("=" * 70)
    print()
    print("  COMMANDS:")
    print("    all sports score today/yesterday/MMDDYY")
    print("    nba, nfl, nhl, ncaab, ncaaf score today/yesterday/MMDDYY")
    print("    <team> vs <team> score today/yesterday/MMDDYY")
    print()
    print("  EXAMPLES:")
    print("    all sports score yesterday")
    print("    nba score today")
    print("    nba, nfl, nhl score yesterday")
    print("    lakers vs celtics score today")
    print()
    print("  Type 'quit' to exit")
    print("=" * 70)
    print()

    while True:
        try:
            user_input = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        # Exit commands
        if cmd in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        # Help command
        if cmd == "help":
            print_help()
            continue

        # Check for "all sports" command
        if "all sports" in cmd or "all score" in cmd:
            # Parse date from query
            date = None
            if "today" in cmd:
                date = datetime.now()
            elif "yesterday" in cmd:
                date = datetime.now() - timedelta(days=1)
            elif "tomorrow" in cmd:
                date = datetime.now() + timedelta(days=1)
            else:
                date_match = re.search(r'(\d{6})', cmd)
                if date_match:
                    try:
                        date = datetime.strptime(date_match.group(1), "%m%d%y")
                    except ValueError:
                        pass
            if not date:
                date = datetime.now()

            date_str = date.strftime('%B %d, %Y')
            print(f"\nFetching: ALL SPORTS - {date_str}")
            print("-" * 90)

            all_games = []
            for league in APIS.keys():
                games = fetch_games(league=league, date=date)
                all_games.extend(games)

            print_games(all_games)

            if all_games:
                save_to_csv(all_games)
                print("-" * 90)
                print(f"Saved {len(all_games)} games to {CSV_FILE}")
            print()
            continue

        # Check for team vs team query first
        if " vs " in cmd or " v " in cmd:
            team_query = parse_team_query(user_input)

            date_str = team_query['date'].strftime('%B %d, %Y')
            if team_query['team2']:
                print(f"\nSearching: {team_query['team1']} vs {team_query['team2']} - {date_str}")
            else:
                print(f"\nSearching: {team_query['team1']} - {date_str}")
            print("-" * 90)

            # Fetch all leagues for that date
            all_games = fetch_games(date=team_query['date'])

            # Filter by team
            matched_games = find_team_game(all_games, team_query['team1'], team_query['team2'])

            print_games(matched_games)

            if matched_games:
                save_to_csv(matched_games)
                print("-" * 90)
                print(f"Saved {len(matched_games)} games to {CSV_FILE}")
            print()
            continue

        # Try to parse as a league query (e.g., "nba today", "nba, nfl, nhl yesterday")
        parsed = parse_multi_league_query(user_input)
        if parsed["leagues"]:
            date_str = parsed['date'].strftime('%B %d, %Y')
            league_str = ', '.join([lg.upper() for lg in parsed['leagues']])
            print(f"\nFetching: {league_str} games - {date_str}")
            print("-" * 90)

            all_games = []
            for league in parsed["leagues"]:
                games = fetch_games(league=league, date=parsed["date"])
                all_games.extend(games)

            print_games(all_games)

            if all_games:
                save_to_csv(all_games)
                print("-" * 90)
                print(f"Saved {len(all_games)} games to {CSV_FILE}")
            print()
            continue

        # Unknown command
        print(f"Unknown command: {user_input}")
        print("Type 'help' for available commands.")
        print()


def main():
    # If no arguments, run interactive mode
    if len(sys.argv) < 2:
        interactive_mode()
        return

    query = " ".join(sys.argv[1:])
    parsed = parse_query(query)

    # Display what we're searching for
    if parsed["week"]:
        print(f"Fetching: {parsed['league'].upper() if parsed['league'] else 'All'} games - Week {parsed['week']}")
    elif parsed["date"]:
        print(f"Fetching: {parsed['league'].upper() if parsed['league'] else 'All'} games - {parsed['date'].strftime('%B %d, %Y')}")
    print("-" * 90)

    games = fetch_games(
        league=parsed["league"],
        week=parsed["week"],
        date=parsed["date"]
    )

    print_games(games)

    if games:
        save_to_csv(games)
        print("-" * 90)
        print(f"Saved {len(games)} games to {CSV_FILE}")


if __name__ == "__main__":
    main()
