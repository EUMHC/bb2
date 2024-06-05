from abc import ABC, abstractmethod


class SelectionFunction(ABC):
    def __init__(self):
        super().__init__()
        print("[+] Heuristic Initialised")

    @abstractmethod
    def evaluate(self, eligible_teams: [str], **kwargs) -> str:
        """
        Finds the most suited team for umpiring from the list of eligible teams
        :param eligible_teams: list of string of eligible teams that can umpire a given fixture
        :return: The best team to umpire
        """
        pass


class GreedyFair(SelectionFunction):
    def evaluate(self, eligible_teams: [str], **kwargs) -> str:
        umpiring_count = kwargs.get('umpiring_count', {})
        eligible_teams = sorted(eligible_teams, key=lambda x: (umpiring_count[x], x))
        best_selection = eligible_teams[0]
        return best_selection
