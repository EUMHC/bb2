# The BuzzBot

`If the EUHC Cinematic Universe allowed myself, Jack Mead, and Ed Bury to do the umpiring assignments for EUMHC together at the same time. Then times that by 10 million. That is The BuzzBot`

## Constraints, Heuristics, and Assumptions

- The higher the team, the better the umpiring ability. (1s > 2s > 3s > ...)
- An umpire cannot umpire and play at the same time (*u* umpires *t* where *u* != *t*)
- An umpire cannot umpire a fixture if the fixture overlaps with their own fixture (for A, B in list of fixtures F,
  not ( A.start < B.end and A.end > B.start))
- An umpire cannot umpire a fixture if the time between the umpiring fixture and the playing fixture is less than the
  total time to travel between the two.
-

## To-do list of things to do
- [x] Prioritised covering selection for teams playing on the same day
- [x] Doesn't select the playing team as the covering team
- [x] Doesn't select teams that are playing in overlapping times
- [x] Handles requiring no umpires and requiring 2 umpires
- [x] Add location to fixtures
  - [ ] Integrate travel time calculation and overlap checking using Google Maps API(?)
- [ ] Handle having a teams as an away team in a fixture
- [ ] Rewrite as a proper constraint search problem.