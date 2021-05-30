from typing import Dict, List, Optional, Tuple, Union
from src.problem import Problem
from src.metaheuristic.solver import Solver
import numpy as np
import copy as cp
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import os


class Ant:
    def __init__(self, aco, problem: Problem, alpha: float, beta: float):
        self.tour: List[int] = []
        self.current_node: int = 0
        self.possibles_moves: List[int] = []
        self.aco = aco
        self.fitness = 0.0
        self.problem: Problem = problem
        self.alpha: float = alpha
        self.beta: float = beta

    def run(self):
        self.reset(np.random.randint(self.problem.size))

        self.possibles_moves = self.problem.init_possibles_moves(
            self.current_node)

        while self.possibles_moves:
            next_node = self.move_to_next_node()

            self.possibles_moves.remove(next_node)
            self.tour.append(next_node)

            # self.local_update_pheromone(self.current_node, next_node)

            self.current_node = next_node

            self.possibles_moves = self.problem.update_possibles_moves(
                self.tour, self.possibles_moves)

        self.fitness = self.problem.fitness(self.tour)
        return (self.fitness, cp.copy(self.tour))

    def reset(self, start_node: int):
        self.tour = [start_node]
        self.possibles_moves = []
        self.current_node = start_node
        self.fitness = 0.0

    def local_update_pheromone(self, i: int, j: int):
        self.aco.pheromones[i][j] = (
            1.0 - 0.1) * self.aco.pheromones[i][j] + 0.1 * self.aco.trail_0
        self.aco.pheromones[j][i] = self.aco.pheromones[i][j]

    def move_to_next_node(self) -> int:
        attractiveness = {}
        sum_attractiveness = 0.0
        i = self.current_node

        for move in self.possibles_moves:
            attractiveness[move] = pow(
                self.aco.pheromones[i][move], self.alpha) * pow(
                    self.problem.heuristic(i, move), self.beta)
            sum_attractiveness += attractiveness[move]

        if sum_attractiveness == 0.0:
            next_node = np.random.choice(list(attractiveness.keys()))
        else:
            next_node = np.random.choice(list(attractiveness.keys()),
                                         p=list(attractiveness.values()) /
                                         np.sum(list(attractiveness.values())))

        return next_node


class ACO(Solver):
    def __init__(self, problem: Problem, **kwargs):
        self.problem: Problem = problem
        self.pheromones = np.ones((problem.size, problem.size), dtype=float)
        self.ants: List[Ant] = list()
        self.best_tour: Tuple(Union[float, int], List[int]) = (None, list())
        self.trail_max: float = 0.0
        self.trail_min: float = 0.0
        self.trail_0: float = 0.0
        self.stagnation_count: int = 0

        # Parameters for Ant Colony
        self.num_ants: int = kwargs.get("num_ants", 10)
        self.rho: float = kwargs.get("rho", 0.5)  # evaporation rate
        self.alpha: float = kwargs.get("alpha", 1.0)  # used for edge detection
        self.beta: float = kwargs.get("beta", 2.0)  # used for edge detection
        self.num_iterations: int = kwargs.get("num_iterations", 10)  # N
        self.stagnation: int = kwargs.get("stagnation", 5)  # N

    def run(self, **kwargs):
        self.num_ants = kwargs.get("num_ants", self.num_ants)
        self.rho = kwargs.get("rho", self.rho)  # evaporation rate
        self.alpha = kwargs.get("alpha", self.alpha)  # used for edge detection
        self.beta = kwargs.get("beta", self.beta)  # used for edge detection
        self.num_iterations = kwargs.get("num_iteration", self.num_iterations)
        self.stagnation = kwargs.get("stagnation", self.stagnation)  # N

        # Init ants
        self.ants = [
            Ant(self, self.problem, self.alpha, self.beta)
            for _ in range(self.num_ants)
        ]

        self.trail_max = 1.0 / (self.rho * self.problem.size)
        self.trail_min = self.trail_max / (2.0 * self.problem.size)
        self.trail_0 = self.trail_max
        self.init_pheromones()

        for i in range(self.num_iterations):
            print(i)
            # construct
            self.construct_phase()

            if self.stagnation == self.stagnation_count:
                self.init_pheromones()
                self.stagnation_count = 0
            else:
                self.update_pheromones()

        print([ant.fitness for ant in self.ants])
        print(self.pheromones)
        return self.best_tour

    def construct_phase(self):
        last_best = self.best_tour[0]

        with ThreadPoolExecutor() as executor:
            results = [executor.submit(ant.run) for ant in self.ants]
            for f in as_completed(results):
                result = f.result()
                if self.best_tour[0] is None or self.problem.best_fitness(
                        result[0], self.best_tour[0]):
                    self.best_tour = (result[0], result[1])

        if last_best == self.best_tour[0]:
            self.stagnation_count += 1
        else:
            self.stagnation_count = 0

        self.trail_max = 1.0 / (self.rho * self.best_tour[0])
        self.trail_min = self.trail_max / (2. * self.problem.size)
        self.trail_0 = self.trail_max

    def init_pheromones(self):
        for i in range(self.problem.size):
            for j in range(i, self.problem.size):
                if i != j:
                    self.pheromones[i][j] = self.pheromones[j][
                        i] = self.trail_0

    def update_pheromones(self):
        d_tau = np.sum(
            [self.problem.delta_tau(ant.fitness) for ant in self.ants])

        deposition = np.zeros_like(self.pheromones, dtype=np.float32)
        deposition[self.best_tour[1],
                   self.best_tour[1][1:] + self.best_tour[1][:1]] += d_tau

        self.pheromones = ((1 - self.rho) * self.pheromones) + deposition

        self.pheromones = np.clip(self.pheromones, self.trail_min,
                                  self.trail_max)
