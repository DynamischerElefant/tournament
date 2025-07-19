import csv
import argparse
import os
import subprocess
from collections import defaultdict


#teams: list of teams = {color, name, points}
#matches: list of matches = {team1, team2, sport, status, points1, points2}

def load_teams(filename="teams.csv"):
    teams = []
    with open(filename) as teams_file:
        reader = csv.DictReader(teams_file)
        for row in reader:
            teams.append(row)
    for team in teams:
        team["points"] = int(team["points"])
    return teams

def load_matches(filename="matches.csv"):
    matches = []
    with open(filename) as matches_file:
        reader = csv.DictReader(matches_file)
        for row in reader:
            matches.append(row)
    for match in matches:
        match["points1"] = int(match["points1"])
        match["points2"] = int(match["points2"])
    return matches

def get_team_index(teams, name):
    for i in range(len(teams)):
        if teams[i]['name'] == name:
            return i
    return -1

def set_points(teams, matches):
    sports = defaultdict(list)
    for match in matches:
        sports[match["sport"]].append(match)

    for sport, sport_matches in sports.items():
        finals = [m for m in sport_matches if m["bracket"] == "Finals" and m["status"] == "Finished"]
        losers = [m for m in sport_matches if m["bracket"] == "Losers" and m["status"] == "Finished"]
        semis = [m for m in sport_matches if m["bracket"] == "Semis" and m["status"] == "Finished"]

        if len(semis) < 2 or len(finals) < 1 or len(losers) < 1:
            continue

        semi_winners, semi_losers = [], []
        for m in semis:
            if m["points1"] > m["points2"]:
                semi_winners.append(m["team1"])
                semi_losers.append(m["team2"])
            else:
                semi_winners.append(m["team2"])
                semi_losers.append(m["team1"])

        final = finals[0]
        first = final["team1"] if final["points1"] > final["points2"] else final["team2"]
        second = final["team2"] if final["points1"] > final["points2"] else final["team1"]

        loser = losers[0]
        third = loser["team1"] if loser["points1"] > loser["points2"] else loser["team2"]
        fourth = loser["team2"] if loser["points1"] > loser["points2"] else loser["team1"]

        placements = {first: 3, second: 2, third: 1, fourth: 0}
        for team in teams:
            if team["name"] in placements:
                team["points"] += placements[team["name"]]

    return teams

def add_team(teams, name, color, points=0):
    teams.append({"name": name, "color": color, "points": points})
    return teams

def add_match(matches, team1, team2, sport, status, bracket, points1=0, points2=0):
    matches.append({"team1": team1, "team2": team2, "sport": sport, "status": status, "bracket": bracket, "points1": points1, "points2": points2})
    return matches

def save_teams_to_csv(teams, filename="teams.csv"):
    with open(filename, "w", newline="") as file:
        fieldnames = ["color", "name", "points"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for team in teams:
            writer.writerow(team)

def save_matches_to_csv(matches, filename="matches.csv"):
    with open(filename, "w", newline="") as file:
        fieldnames = ["team1", "team2", "sport", "status", "bracket", "points1", "points2"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for match in matches:
            writer.writerow(match)

def list_unfinished_matches(matches):
    unfinished = [m for m in matches if m["status"] != "Finished"]
    if not unfinished:
        print("✅ All matches are finished!")
        return []

    print("\n📋 Unfinished Matches:")
    for idx, m in enumerate(unfinished):
        print(f"[{idx}] {m['team1']} vs {m['team2']} ({m['sport']}) - Status: {m['status']}")

    return unfinished

def update_match_score(matches):
    unfinished = list_unfinished_matches(matches)
    if not unfinished:
        return matches

    try:
        choice = int(input("🔢 Choose match number to update score: "))
        match = unfinished[choice]

        new_score1 = int(input(f"Enter score for {match['team1']}: "))
        new_score2 = int(input(f"Enter score for {match['team2']}: "))

        match["points1"] = new_score1
        match["points2"] = new_score2
        match["status"] = "Finished"
        print("✅ Score updated.")
    except (IndexError, ValueError):
        print("❌ Invalid selection or input.")

    return matches

def update_match_status(matches):
    unfinished = list_unfinished_matches(matches)
    if not unfinished:
        return matches

    try:
        choice = int(input("🔢 Choose match number to update status: "))
        match = unfinished[choice]

        new_status = input("Enter new status (e.g., Ongoing, Finished): ").strip()
        match["status"] = new_status
        print("✅ Status updated.")
    except (IndexError, ValueError):
        print("❌ Invalid selection or input.")

    return matches

header = """
# 🏆 Tournament
## 🏅 Rankings
"""

matchups_page = """
---

## ⚔️ Matchups \n
| Match             | Sport | Status | Score | Bracket |
|-------------------|-------|--------|-------|---------|
"""

def write_md(teams, matches, output_file="index.md"):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(header)
        teams.sort(key=lambda t: t["points"],reverse=True)
        for team in teams:
            match_count = len(matches)
            if match_count == 0: # avoiding zero division
                match_count = 1
            file.write(f"""
**Team {team["name"]}: {team["points"]} Points**
<div style="background-color: #eee; border-radius: 8px; width: 100%; height: 20px;">
  <div style="width: {(team["points"]/20)}%; background-color: {team["color"]}; height: 100%; border-radius: 8px;"></div>
</div>
            """)
        file.write(matchups_page)
        for match in reversed(matches):
            if match["status"] == "Finished":
                score = f"{match['points1']} - {match['points2']}"
            else:
                score = "-"
            file.write(f"| {match['team1']} vs {match['team2']} | {match['sport']} | {match['status']} | {score} | {match['bracket']} |\n")

def main():
    parser = argparse.ArgumentParser(description="🎮 Tournament Manager CLI")

    parser.add_argument("--add-team", action="store_true", help="Add a new team")
    parser.add_argument("--add-match", action="store_true", help="Add a new match")
    parser.add_argument("--update-score", action="store_true", help="Update match score")
    parser.add_argument("--update-status", action="store_true", help="Update match status")
    parser.add_argument("--rebuild", action="store_true", help="Recalculate points and rebuild the site")

    args = parser.parse_args()

    # Handle missing CSVs gracefully
    if not os.path.exists("teams.csv"):
        print("📁 Creating empty teams.csv...")
        save_teams_to_csv([])

    if not os.path.exists("matches.csv"):
        print("📁 Creating empty matches.csv...")
        save_matches_to_csv([])

    # Load data
    teams = load_teams()
    matches = load_matches()

    if args.add_team:
        name = input("Team name: ")
        color = input("Team color: ")
        teams = add_team(teams, name, color)

    elif args.add_match:
        team1 = input(f"Team 1({[t["name"] for t in teams]}): ")
        team2 = input(f"Team 2({[t["name"] for t in teams]}): ")
        sport = input("Sport: ")
        bracket = input("Bracket (Semis, Finals or Losers): ")
        status = "Scheuduled"
        matches = add_match(matches, team1, team2, sport, status, bracket)

    elif args.update_score:
        matches = update_match_score(matches)

    elif args.update_status:
        matches = update_match_status(matches)

    # Rebuild site or if anything changed
    if any([args.add_team, args.add_match, args.update_score, args.update_status, args.rebuild]):
        teams = set_points(teams, matches)
        save_teams_to_csv(teams)
        save_matches_to_csv(matches)
        write_md(teams, matches)

    if args.rebuild:
        # Optional: Auto-push to GitHub Pages
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🔄 automatic Tournament update"], check=True)
        subprocess.run(["git", "push"], check=True)

if __name__ == "__main__":
    main()
