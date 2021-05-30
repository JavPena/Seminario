from typing import List, Union
from src.problem import Problem
import numpy as np
import random


class SUKP(Problem):
    def __init__(self,
                 nb_items: int = 0,
                 mb_containers: int = 0,
                 capacity: float = 0.0,
                 values: List = list(),
                 weight: List = list(),
                 unions: List = list(),
                 m_weight: List = list()):
        self.values: List = values
        self.weight: List = weight
        self.nb_items: int = nb_items
        self.capacity: float = capacity
        self.unions: List = list()
        self.mb_containers: int = mb_containers
        self.m_weights: List = m_weight

        self.total_values = sum(self.values)

    def read_file(self, path: str):
        cont = 0
        text = False
        with open(path, "r") as fp:
            for line in fp.readlines():
                if len(line.strip()) == 0:
                    cont += 1
                    text = True
                    continue
                if cont == 2:
                    linea = line.strip().split(" ")
                    linea = list(filter(lambda a: a != "", linea))
                    self.nb_items = int(linea[0].split("=")[1])
                    self.mb_containers = int(linea[1].split("=")[1])
                    self.capacity = float(linea[3].split("=")[1])
                    continue
                if cont == 3:
                    if text:
                        text = False
                        continue
                    for i in line.strip().split(" "):
                        self.values.append(int(i))
                if cont == 4:
                    if text:
                        text = False
                        continue
                    for i in line.strip().split(" "):
                        self.m_weights.append(int(i))
                    continue
                if cont == 5:
                    if text:
                        text = False
                        continue
                    auxList = list()
                    for i in line.strip().split(" "):
                        auxList.append(int(i))
                    self.unions.append(auxList)
        self.weight = self.calcula_pesos()
        self.total_values = sum(self.values)

    def calcula_pesos(self):
        pesos = list()
        for i in range(len(self.unions)):
            suma = 0
            for j in range(len(self.unions[i])):
                suma += self.unions[i][j] * self.m_weights[j]
            pesos.append(suma)
        return pesos

    def best_fitness(self, actual_fitness: float, best_fitness: float) -> bool:
        return actual_fitness > best_fitness

    def delta_tau(self, fitness: float):
        return fitness / self.total_values

    def generateInitialSolution(self) -> List[int]:
        solution = list()
        for i in range(len(self.values)):
            solution.append(random.randint(0, 1))
        solution = self.fixSolution(solution)

        return solution

    def fixSolution(self, solution: List[int]) -> List[int]:
        capacity = self.calculate_weight(solution)
        while capacity > self.capacity:
            for i in random.sample(range(len(solution)), len(solution)):
                if solution[i] == 1:
                    solution[i] = 0
                    break
            capacity = self.calculate_weight(solution)
        return solution

    def calculate_weight(self, solution: List[int]) -> float:
        matriz = np.array(self.unions, np.int32)
        matriz = np.transpose(matriz)
        weight = 0
        for i in range(len(matriz)):
            for j in range(len(matriz[0])):
                if matriz[i][j] * solution[j] == 1:
                    weight += self.m_weights[i]
                    break
        return weight

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
        return sum(
            [self.values[i] * solution[i] for i in range(len(solution))])

    @property
    def size(self) -> int:
        return self.nb_items