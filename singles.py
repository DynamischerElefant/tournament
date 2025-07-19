import csv
import argparse
import os
import subprocess
from collections import defaultdict

def load_players(filename="players.csv"):
    players = []
    if not os.path.exists(filename):
        return players
    with open(filename) as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["points"] = int(row["points"])
            players.append(row)
    return players

def load_matches(filename="matches.csv"):
    matches = []
    if not os.path.exists(filename):
        return matches
    with open(filename) as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["points1"] = int(row["points1"])
            row["points2"] = int(row["points2"])
            matches.append(row)
    return matches

def save_players(players, filename="players.csv"):
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "color", "points"])
        writer.writeheader()
        for p in players:
            writer.writerow(p)

def save_matches(matches, filename="matches.csv"):
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "team1player1", "team1player2",
            "team2player1", "team2player2",
            "sport", "status", "points1", "points2"
        ])
        writer.writeheader()
        for m in matches:
            writer.writerow(m)

def add_player(players, name, color):
    players.append({"name": name, "color": color, "points": 0})
    return players

def add_match(matches):
    print("👥 Enter players for Team 1:")
    t1p1 = input(" - Player 1: ")
    t1p2 = input(" - Player 2: ")
    print("👥 Enter players for Team 2:")
    t2p1 = input(" - Player 1: ")
    t2p2 = input(" - Player 2: ")
    sport = input("🏅 Sport: ")
    matches.append({
        "team1player1": t1p1,
        "team1player2": t1p2,
        "team2player1": t2p1,
        "team2player2": t2p2,
        "sport": sport,
        "status": "Scheduled",
        "points1": 0,
        "points2": 0
    })
    return matches

def update_match_score(matches):
    unfinished = [m for m in matches if m["status"] != "Finished"]
    if not unfinished:
        print("✅ No unfinished matches.")
        return matches

    for i, m in enumerate(unfinished):
        t1 = f"{m['team1player1']} & {m['team1player2']}"
        t2 = f"{m['team2player1']} & {m['team2player2']}"
        print(f"[{i}] {t1} vs {t2} ({m['sport']})")

    try:
        idx = int(input("🔢 Choose match to update: "))
        m = unfinished[idx]
        m["points1"] = int(input(f"Score for {m['team1player1']} & {m['team1player2']}: "))
        m["points2"] = int(input(f"Score for {m['team2player1']} & {m['team2player2']}: "))
        m["status"] = "Finished"
        print("✅ Score updated.")
    except Exception as e:
        print("❌ Error:", e)
    return matches

def update_match_status(matches):
    unfinished = [m for m in matches if m["status"] != "Finished"]
    if not unfinished:
        print("✅ All matches finished.")
        return matches

    for i, m in enumerate(unfinished):
        t1 = f"{m['team1player1']} & {m['team1player2']}"
        t2 = f"{m['team2player1']} & {m['team2player2']}"
        print(f"[{i}] {t1} vs {t2} ({m['sport']})")

    try:
        idx = int(input("🔢 Choose match to update status: "))
        new_status = input("New status (Scheduled, Ongoing, Finished): ")
        unfinished[idx]["status"] = new_status
    except Exception as e:
        print("❌ Error:", e)
    return matches

def calculate_points(players, matches):
    points_map = defaultdict(int)
    for m in matches:
        if m["status"] != "Finished":
            continue
        p1 = m["points1"]
        p2 = m["points2"]

        if p1 > p2:
            points_map[m["team1player1"]] += 3
            points_map[m["team1player2"]] += 3
        elif p2 > p1:
            points_map[m["team2player1"]] += 3
            points_map[m["team2player2"]] += 3
        else:  # draw
            points_map[m["team1player1"]] += 1
            points_map[m["team1player2"]] += 1
            points_map[m["team2player1"]] += 1
            points_map[m["team2player2"]] += 1

    for player in players:
        player["points"] = points_map[player["name"]]

    return players

def write_md(players, matches, output_file="index.md"):
    header = "# 🏆 Tournament\n## 🏅 Player Rankings\n"
    matches_header = """
---

## ⚔️ Matchups \n

| Team 1                | Team 2                | Sport     | Status   | Score     |
|-----------------------|-----------------------|-----------|----------|-----------|
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(header)
        players.sort(key=lambda p: p["points"], reverse=True)
        for p in players:
            f.write(f"""
**{p["name"]}: {p["points"]} Points**
<div style="background-color: #eee; border-radius: 8px; width: 100%; height: 20px;">
  <div style="width: {(p["points"]/20) * 100}%; background-color: {p["color"]}; height: 100%; border-radius: 8px;"></div>
</div>
            """)
        f.write(matches_header)
        for m in reversed(matches):
            t1 = f"{m['team1player1']} & {m['team1player2']}"
            t2 = f"{m['team2player1']} & {m['team2player2']}"
            score = f"{m['points1']} - {m['points2']}" if m["status"] == "Finished" else "-"
            f.write(f"| {t1:<21} | {t2:<21} | {m['sport']:<9} | {m['status']:<8} | {score:<9} |\n")

def main():
    parser = argparse.ArgumentParser(description="🏅 Player Tournament CLI")
    parser.add_argument("--add-player", action="store_true", help="Add a new player")
    parser.add_argument("--add-match", action="store_true", help="Add a new match")
    parser.add_argument("--update-score", action="store_true", help="Update match score")
    parser.add_argument("--update-status", action="store_true", help="Update match status")
    parser.add_argument("--rebuild", action="store_true", help="Recalculate and rebuild site")
    args = parser.parse_args()

    players = load_players()
    matches = load_matches()

    if args.add_player:
        name = input("Player name: ")
        color = input("Player color: ")
        players = add_player(players, name, color)

    if args.add_match:
        matches = add_match(matches)

    if args.update_score:
        matches = update_match_score(matches)

    if args.update_status:
        matches = update_match_status(matches)

    if any([args.add_player, args.add_match, args.update_score, args.update_status, args.rebuild]):
        players = calculate_points(players, matches)
        save_players(players)
        save_matches(matches)
        write_md(players, matches)

    if args.rebuild:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🔄 Tournament update"], check=True)
        subprocess.run(["git", "push"], check=True)

if __name__ == "__main__":
    main()
