import csv
import argparse
import os
import subprocess

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
    for team in teams:
        team["points"] = 0
    for match in matches:
        if match["points1"] > match["points2"]:
            idx = get_team_index(teams, match["team1"])
            if idx != -1:
               teams[idx]["points"] += 3
        elif match["points2"] > match["points1"]:
            idx = get_team_index(teams, match["team2"])
            if idx != -1:
                teams[idx]["points"] += 3
        else:
            idx1 = get_team_index(teams, match["team1"])
            idx2 = get_team_index(teams, match["team2"])
            teams[idx1]["points"] += 1
            teams[idx2]["points"] += 1
    return teams

def add_team(teams, name, color, points=0):
    teams.append({"name": name, "color": color, "points": points})
    return teams

def add_match(matches, team1, team2, sport, status, points1=0, points2=0):
    matches.append({"team1": team1, "team2": team2, "sport": sport, "status": status, "points1": points1, "points2": points2})
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
        fieldnames = ["team1", "team2", "sport", "status", "points1", "points2"]
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
| Match             | Sport | Status | Score | 
|-------------------|-------|--------|-------|
"""

def write_md(teams, matches, output_file="index.md"):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(header)
        teams.sort(key=lambda t: t["points"],reverse=True)
        for team in teams:
            match_count = 0
            for match in matches:
                if match["team1"] == team["name"] or match["team2"] == team["name"]:
                    match_count += 1
            if match_count == 0: # avoiding zero division
                match_count = 1
            file.write(f"""
**Team {team["name"]}: {team["points"]} Points**
<div style="background-color: #eee; border-radius: 8px; width: 100%; height: 20px;">
  <div style="width: {(team["points"]/(match_count * 3))*100}%; background-color: {team["color"]}; height: 100%; border-radius: 8px;"></div>
</div>
            """)
        file.write(matchups_page)
        for match in reversed(matches):
            if match["status"] == "Finished":
                score = f"{match['points1']} - {match['points2']}"
            else:
                score = "-"
            file.write(f"| {match['team1']} vs {match['team2']} | {match['sport']} | {match['status']} | {score} |\n")

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
        team1 = input("Team 1: ")
        team2 = input("Team 2: ")
        sport = input("Sport: ")
        matches = add_match(matches, team1, team2, sport, status="Scheduled")

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
