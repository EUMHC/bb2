# The BuzzBot

[![wakatime](https://wakatime.com/badge/user/eb310a2d-fc37-4859-8755-b6b88930af57/project/018cdb8d-3c59-4706-8b4c-4fb2808b90c9.svg)](https://wakatime.com/badge/user/eb310a2d-fc37-4859-8755-b6b88930af57/project/018cdb8d-3c59-4706-8b4c-4fb2808b90c9)

`If the EUHC Cinematic Universe allowed Jack Mead, Ed Bury, and I to do the umpiring assignments for EUMHC together at the same time. Then times that by 10 million. That is The BuzzBot`

## Abstract

Students don't like umpiring. In an ideal world, every player at a university hockey club would never have to umpire
a game during their time at the club. Alas, this is not the case. At Edinburgh University Men's Hockey Club, the club
policy
is that all umpires are players; the two are not mutually exclusive like they are at other clubs. When priority is given
to ensure all players are able to put playing first, a system for assigning umpires to fixtures can be modelled. Given a
uniform spread of umpires across all playing teams, assignments can be given to a team rather than an individual. The
system
presented, called The BuzzBot, successfully assigns 'covering teams' to fixtures based on set assumptions and
constraints.

### Constraints, Heuristics, and Assumptions

#### Mathematical Notation

Let:
- \( T_{AB} \) be the travel time between fixtures \( A \) and \( B \).
- \( A.\text{start} \) and \( A.\text{end} \) be the start and end times of fixture \( A \).
- \( \text{players}(g) \) be the set of players in game \( g \).
- \( \text{UmpireAbility}(t) \) be the umpiring ability of team \( t \).


1. **Heuristic: Team Ranking and Umpiring Ability**
   - The higher the team, the better the umpiring ability.
   - If team \( t_1 \) is ranked higher than team \( t_2 \), then \( \text{umpiring ability of } t_1 > \text{umpiring ability of } t_2 \).
   - Formally: \( t_1 > t_2 \implies \text{UmpireAbility}(t_1) > \text{UmpireAbility}(t_2) \)

2. **Constraint: Umpire Cannot Play and Umpire Simultaneously**
   - An umpire \( u \) cannot umpire and play at the same time:
   - \( u \text{ umpires game } g \implies u \not\in \text{players}(g) \)

3. **Constraint: Fixture Overlap**
   - An umpire cannot umpire a fixture if the fixture overlaps with their own playing fixture.
   - For fixtures \( A \) and \( B \) in the list of fixtures \( F \):
   - \( \neg (A.\text{start} < B.\text{end} \land A.\text{end} > B.\text{start}) \)

4. **Constraint: Travel Time Between Fixtures**
   - An umpire cannot umpire a fixture if the time between the umpiring fixture and the playing fixture is less than the total travel time between the two.
   - Let \( T_{AB} \) be the travel time between fixtures \( A \) and \( B \):
   - \( A.\text{end} + T_{AB} \leq B.\text{start} \) and \( B.\text{end} + T_{BA} \leq A.\text{start} \)

5. **Assumption: Symmetric Travel Time**
   - The travel time from fixture \( A \) to fixture \( B \) is equal to the travel time from fixture \( B \) to fixture \( A \).
   - Formally: \( T_{AB} = T_{BA} \)

6. **Assumption: Mode of Travel**
   - Umpires travel to and from games in cars.





## Prerequisites

Make sure you have the following installed on your system:

- Python (>=3.6)
- pip (Python package installer)
- Virtualenv (optional but recommended)

## Installation

### Clone the Repository

```bash
git clone https://github.com/CallumAlexander/The-BuzzBot-Python.git
cd The-BuzzBot-Python
```

### Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```


## Running the Application

To start the Flask application, use the following command:

```bash
flask run
```

By default, the application will run on `http://127.0.0.1:5000/`. Navigate to there in your browser.

## To-do list of things to do
- [x] Prioritised covering selection for teams playing on the same day
- [x] Doesn't select the playing team as the covering team
- [x] Doesn't select teams that are playing in overlapping times
- [x] Handles requiring no umpires and requiring 2 umpires
- [x] Add location to fixtures
  - [x] Integrate travel time calculation and overlap checking using Google Maps API(?)
- [ ] Handle having a teams as an away team in a fixture
- [ ] Heuristic involving confidence metric to select the best team to umpire rather than a greedy heuristic
- [ ] Rewrite as a proper constraint search problem.
- [ ] Handle multiple team assignments for a single game (1s and 2s provide an umpire each for a match - only when 2
  umpires are required).