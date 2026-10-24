from abc import ABC, abstractmethod
from typing import Sequence
from point import Point

class Spline(ABC):
    @abstractmethod
    def update_spline(
        self,
        points: Sequence[Point],
        f_value: Sequence[float]
    ) -> None:
        pass

    @abstractmethod
    def get_value(self, p: Point) -> list[float]:
        pass