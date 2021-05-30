from abc import ABC, abstractmethod
from typing import List, Union


class Problem(ABC):
    @abstractmethod
    def best_fitness(self, actual_fitness: float, best_fitness: float) -> bool:
        pass

    @abstractmethod
    def delta_tau(self, fitness: float):
        pass

    @abstractmethod
    def heuristic(self, i: int, j: int) -> Union[float, int]:
        pass

    @abstractmethod
    def update_possibles_moves(self, solution: List[int],
                               actual_moves: List[int]) -> List[int]:
        pass

    @abstractmethod
    def init_possibles_moves(self, start_move: int) -> List[int]:
        pass

    @abstractmethod
    def fitness(self, solution: List[int]) -> Union[float, int]:
        pass

    @property
    @abstractmethod
    def size(self) -> int:
        pass