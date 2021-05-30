from typing import List, Union
from src.problem import Problem


class Knapsack(Problem):
    def __init__(self,
                 nb_items: int = 0,
                 capacity: float = 0.0,
                 values: List = list(),
                 weight: List = list()):
        self.values: List = values
        self.weight: List = weight
        self.nb_items: int = nb_items
        self.capacity: float = capacity

        self.total_values = sum(self.values)

    def read_file(self, path: str):
        is_first = True
        with open(path, "r") as fp:
            for line in fp.readlines():
                if is_first:
                    self.nb_items, self.capacity = (int(line.split(" ")[0]),
                                                    int(line.split(" ")[1]))
                    is_first = False
                else:
                    self.values.append(int(line.split(" ")[0]))
                    self.weight.append(int(line.split(" ")[1]))

        self.total_values = sum(self.values)

    def best_fitness(self, actual_fitness: float, best_fitness: float) -> bool:
        return actual_fitness > best_fitness

    def delta_tau(self, fitness: float):
        return fitness / self.total_values

    def heuristic(self, i: int, j: int) -> Union[float, int]:
        return self.values[i] / self.weight[j]

    def init_possibles_moves(self, start_move: int) -> List[int]:
        moves = []
        for i in range(self.nb_items):
            if i != start_move and self.weight[i] <= self.capacity:
                moves.append(i)
        return moves

    def update_possibles_moves(self, solution: List[int],
                               actual_moves: List[int]) -> List[int]:

        moves_to_remove = []
        actual_weight = sum([self.weight[i] for i in solution])

        for move in actual_moves:
            if actual_weight + self.weight[move] > self.capacity:
                moves_to_remove.append(move)

        for i in moves_to_remove:
            actual_moves.remove(i)

        return actual_moves

    def fitness(self, solution: List[int]) -> Union[float, int]:
        return sum([self.values[i] for i in solution])

    @property
    def size(self) -> int:
        return self.nb_items