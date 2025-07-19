import random
from itertools import combinations

def generate_balanced_matchups(num_teams, games_per_team):
    if games_per_team >= num_teams:
        raise ValueError("Each team must play fewer games than the number of teams.")

    teams = [f"Team{i+1}" for i in range(num_teams)]
    all_possible_matches = list(combinations(teams, 2))
    random.shuffle(all_possible_matches)

    team_game_counts = {team: 0 for team in teams}
    scheduled_matches = []

    for t1, t2 in all_possible_matches:
        if team_game_counts[t1] < games_per_team and team_game_counts[t2] < games_per_team:
            scheduled_matches.append((t1, t2))
            team_game_counts[t1] += 1
            team_game_counts[t2] += 1

        if all(count == games_per_team for count in team_game_counts.values()):
            break

    if not all(count == games_per_team for count in team_game_counts.values()):
        raise ValueError("⚠️ Could not generate a valid schedule with the given constraints.")

    return scheduled_matches


def main():
    print("🎯 Match Generator for Equal Play Time")
    try:
        num_teams = int(input("Enter number of teams: "))
        games_per_team = int(input("Enter games each team should play: "))

        matchups = generate_balanced_matchups(num_teams, games_per_team)

        print("\n📅 Generated Matchups:\n")
        for i, (team1, team2) in enumerate(matchups, 1):
            print(f"{i:>2}. {team1} vs {team2}")

    except ValueError as e:
        print(f"❌ Error: {e}")
    except KeyboardInterrupt:
        print("\n❌ Aborted by user.")


if __name__ == "__main__":
    main()
