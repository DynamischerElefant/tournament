import csv
import argparse
import os
import subprocess
from collections import defaultdict

def load_teams(filename="teams.csv"):
    teams = []
    if os.path.exists(filename):
        with open(filename) as file:
            reader = csv.DictReader(file)
            for row in reader:
                row["points"] = int(row["points"])
                teams.append(row)
    return teams

def load_matches(filename="matches.csv"):
    matches = []
    if os.path.exists(filename):
        with open(filename) as file:
            reader = csv.DictReader(file)
            for row in reader:
                row["points1"] = int(row["points1"])
                row["points2"] = int(row["points2"])
                matches.append(row)
    return matches

def save_teams_to_csv(teams, filename="teams.csv"):
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["color", "name", "points"])
        writer.writeheader()
        for team in teams:
            writer.writerow(team)

def save_matches_to_csv(matches, filename="matches.csv"):
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["team1", "team2", "sport", "status", "bracket_stage", "points1", "points2"])
        writer.writeheader()
        for match in matches:
            writer.writerow(match)

def get_team_index(teams, name):
    for i, team in enumerate(teams):
        if team["name"] == name:
            return i
    return -1

def add_team(teams, name, color, points=0):
    teams.append({"name": name, "color": color, "points": points})
    return teams

def add_match(matches, team1, team2, sport, bracket_stage, status="Scheduled", points1=0, points2=0):
    matches.append({
        "team1": team1,
        "team2": team2,
        "sport": sport,
        "bracket_stage": bracket_stage,
        "status": status,
        "points1": points1,
        "points2": points2
    })
    return matches

def update_match_score(matches):
    unfinished = [m for m in matches if m["status"] != "Finished"]
    if not unfinished:
        print("✅ All matches are finished.")
        return matches

    for idx, match in enumerate(unfinished):
        print(f"[{idx}] {match['team1']} vs {match['team2']} ({match['sport']}, {match['bracket_stage']}) - {match['status']}")

    try:
        choice = int(input("Select match to update score: "))
        match = unfinished[choice]
        match["points1"] = int(input(f"Score for {match['team1']}: "))
        match["points2"] = int(input(f"Score for {match['team2']}: "))
        match["status"] = "Finished"
    except (ValueError, IndexError):
        print("❌ Invalid selection or input.")

    return matches

def calculate_bracket_points(teams, matches):
    sports = defaultdict(list)
    for match in matches:
        sports[match["sport"]].append(match)

    for sport, sport_matches in sports.items():
        finals = [m for m in sport_matches if m["bracket_stage"] == "Finals" and m["status"] == "Finished"]
        losers = [m for m in sport_matches if m["bracket_stage"] == "Losers" and m["status"] == "Finished"]
        semis = [m for m in sport_matches if m["bracket_stage"] == "Semis" and m["status"] == "Finished"]

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


def generate_brackets_md(matches):
    output = "\n---\n## 🎮 Brackets\n"
    sports = defaultdict(list)
    for m in matches:
        sports[m["sport"]].append(m)

    for sport, sport_matches in sports.items():
        output += f"\n### 🏟️ {sport}\n\n"
        semis = [m for m in sport_matches if m["bracket_stage"] == "Semis"]
        finals = [m for m in sport_matches if m["bracket_stage"] == "Finals"]
        losers = [m for m in sport_matches if m["bracket_stage"] == "Losers"]

        if len(semis) != 2 or len(finals) != 1:
            output += "_Bracket incomplete._\n"
            continue

        # Sort semi matches for consistent layout
        semi1, semi2 = semis

        def fmt_match(m):
            s = f"{m['points1']} - {m['points2']}" if m["status"] == "Finished" else "     "
            return m["team1"], m["team2"], s

        # Format Semis
        a1, a2, a_score = fmt_match(semi1)
        b1, b2, b_score = fmt_match(semi2)

        # Format Final
        f1, f2, f_score = fmt_match(finals[0])

        bracket = f"""
    ┌───── Semifinal ─────┐          ┌────── Final ──────┐
    │ {a1:<10} {semi1['points1'] if semi1['status'] == 'Finished' else ' '}       │          │                        │
    │           vs         ├────┐    │   {f1:<10}        │
    │ {a2:<10} {semi1['points2'] if semi1['status'] == 'Finished' else ' '}       │    │    │        {finals[0]['points1'] if finals[0]['status'] == 'Finished' else ' '}         │
    └─────────────────────┘    │    │   vs              │
                               ├────┤                    │
    ┌───── Semifinal ─────┐    │    │   {f2:<10}         │
    │ {b1:<10} {semi2['points1'] if semi2['status'] == 'Finished' else ' '}       │    │    │        {finals[0]['points2'] if finals[0]['status'] == 'Finished' else ' '}         │
    │           vs         ├────┘    └──────────────────┘
    │ {b2:<10} {semi2['points2'] if semi2['status'] == 'Finished' else ' '}       │
    └─────────────────────┘
"""
        output += f"```\n{bracket}\n```\n"

        # Losers bracket
        if losers:
            loser = losers[0]
            if loser["status"] == "Finished":
                score = f"{loser['points1']} - {loser['points2']}"
            else:
                score = "-"
            output += f"\n**🥉 3rd Place:** {loser['team1']} vs {loser['team2']} → {score}\n"

    return output

def write_md(teams, matches, output_file="index.md"):
    header = "# 🏆 Tournament Standings\n## 🥇 Cumulative Rankings\n"
    matchups = "\n---\n## ⚔️ Matchups\n| Match | Sport | Status | Score |\n|-------|-------|--------|-------|\n"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(header)
        for team in sorted(teams, key=lambda t: -t["points"]):
            f.write(f"\n**{team['name']}**: {team['points']} Points\n")

        f.write(generate_brackets_md(matches))

        f.write(matchups)
        for m in matches:
            score = f"{m['points1']} - {m['points2']}" if m["status"] == "Finished" else "-"
            f.write(f"| {m['team1']} vs {m['team2']} | {m['sport']} | {m['status']} | {score} |\n")

def main():
    parser = argparse.ArgumentParser(description="🏆 Multi-Sport Bracket Tournament")
    parser.add_argument("--add-team", action="store_true", help="Add a new team")
    parser.add_argument("--add-match", action="store_true", help="Add a bracket match")
    parser.add_argument("--update-score", action="store_true", help="Update match scores")
    parser.add_argument("--rebuild", action="store_true", help="Recalculate points and rebuild site")

    args = parser.parse_args()

    if not os.path.exists("teams.csv"):
        save_teams_to_csv([])
    if not os.path.exists("matches.csv"):
        save_matches_to_csv([])

    teams = load_teams()
    matches = load_matches()

    if args.add_team:
        name = input("Team name: ")
        color = input("Color: ")
        add_team(teams, name, color)

    if args.add_match:
        team1 = input("Team 1: ")
        team2 = input("Team 2: ")
        sport = input("Sport: ")
        stage = input("Bracket stage (Semis / Finals / Losers): ")
        add_match(matches, team1, team2, sport, bracket_stage=stage)

    if args.update_score:
        matches = update_match_score(matches)

    if args.rebuild:
        teams = calculate_bracket_points(teams, matches)

        save_teams_to_csv(teams)
        save_matches_to_csv(matches)
        write_md(teams, matches)

        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🏁 Tournament update"], check=True)
        subprocess.run(["git", "push"], check=True)
    else:
        # Even without --rebuild, persist changes like match/score updates
        save_teams_to_csv(teams)
        save_matches_to_csv(matches)
        write_md(teams, matches)

if __name__ == "__main__":
    main()
