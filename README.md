# The BuzzBot

[![wakatime](https://wakatime.com/badge/user/eb310a2d-fc37-4859-8755-b6b88930af57/project/018cdb8d-3c59-4706-8b4c-4fb2808b90c9.svg)](https://wakatime.com/badge/user/eb310a2d-fc37-4859-8755-b6b88930af57/project/018cdb8d-3c59-4706-8b4c-4fb2808b90c9)

`If the EUHC Cinematic Universe allowed myself, Jack Mead, and Ed Bury to do the umpiring assignments for EUMHC together at the same time. Then times that by 10 million. That is The BuzzBot`

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

## Constraints, Heuristics, and Assumptions

- The higher the team, the better the umpiring ability. (1s > 2s > 3s > ...)
- An umpire cannot umpire and play at the same time (*u* umpires *t* where *u* != *t*)
- An umpire cannot umpire a fixture if the fixture overlaps with their own playing fixture (for A, B in list of fixtures
  F,
  not ( A.start < B.end and A.end > B.start))
- An umpire cannot umpire a fixture if the time between the umpiring fixture and the playing fixture is less than the
  total time to travel between the two.
- The travel time A -> B is equal to B -> A
- Umpires travel to and from games in cars

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