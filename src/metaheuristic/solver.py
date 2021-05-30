from abc import ABC, abstractmethod
from typing import Any


class Solver(ABC):
    @abstractmethod
    def run(self, **options) -> Any:
        pass
