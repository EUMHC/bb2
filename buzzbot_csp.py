from constraint import Problem, AllDifferentConstraint
import datetime
import random
import string

from buzzbot import Fixture

teams = ["1s", "2s", "3s", "4s", "5s", "6s", "7s"]
# matches = [Fixture(teams[i], teams[j]) for i in range(len(teams)) for j in range(i + 1, len(teams))]

matches = []
for i in range(0, len(teams)):
    team1 = teams[i]
    random_opponent1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    random_start_time, random_end_time = 11, 18  # 8AM & 8PM
    start_hour = random.randint(random_start_time, random_end_time)
    start_time = datetime.datetime.now().replace(hour=start_hour, minute=0, second=0, microsecond=0)
    matches.append(Fixture(team1, random_opponent1, start_time))

umpiring_count = {team: 0 for team in teams}

# Initialize the constraint problem
problem = Problem()

# Add variables with unique identifiers for each match
match_ids = list(range(len(matches)))
for i, match in enumerate(matches):
    teams_not_playing = [team for team in teams if team not in [match.home, match.away]]
    problem.addVariable(i, teams_not_playing)  # Using match index as variable

# Constraint: All matches must have different umpiring teams
problem.addConstraint(AllDifferentConstraint())

# Constraint: A team cannot umpire a match if they are playing at the same time
def no_overlap_constraint(umpire, *other_match_ids):
    match = matches[umpire]
    for other_id in other_match_ids:
        other_match = matches[other_id]
        if match.overlaps_with(other_match) and umpire == other_match.home or umpire == other_match.away:
            return False
    return True

# Add no-overlap constraint for each match
for i in match_ids:
    problem.addConstraint(no_overlap_constraint, [i] + [j for j in match_ids if j != i])

# Solve the problem
solution = problem.getSolutions()

# Print one of the possible solutions
if solution:
    for i in match_ids:
        match = matches[i]
        print(f"{match.home} vs {match.away} - Umpiring Team: {solution[0][i]}")
else:
    print("No solution found")
