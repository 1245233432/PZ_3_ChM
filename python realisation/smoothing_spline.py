from typing import Sequence

from point import Point
from spline import Spline


class SmoothingSpline(Spline):
    def __init__(self, smooth: float):
        if not 0.0 <= smooth < 1.0:
            raise ValueError(
                "Параметр сглаживания должен принадлежать [0, 1)."
            )

        self.smooth = float(smooth)
        self.points = []
        self.alpha = []
        self.omega = []

    def transition_to_master_element(
        self,
        seg_num: int,
        x: float
    ) -> float:
        """Переход с сегмента на мастер-элемент [-1, 1]."""

        x_left = self.points[seg_num].x()
        x_right = self.points[seg_num + 1].x()

        return (
            2.0 * (x - x_left) / (x_right - x_left)
            - 1.0
        )

    @staticmethod
    def basis_function(number: int, ksi: float) -> float:
        """Линейные базисные функции на [-1, 1]."""

        if number == 1:
            return 0.5 * (1.0 - ksi)

        if number == 2:
            return 0.5 * (1.0 + ksi)

        raise ValueError(
            f"Неверный номер базисной функции: {number}"
        )

    @staticmethod
    def der_basis_function(number: int, ksi: float) -> float:
        if number == 1:
            return -0.5

        if number == 2:
            return 0.5

        raise ValueError(
            f"Неверный номер производной: {number}"
        )

    def set_omega(
        self,
        random_values: Sequence[float]
    ) -> None:
        if len(random_values) == 0:
            raise ValueError(
                "Нельзя определить веса пустой выборки."
            )

        values = [float(value) for value in random_values]

        if not all(
            __import__("math").isfinite(value)
            for value in values
        ):
            raise ValueError(
                "Выборка содержит NaN или бесконечность."
            )

        sorted_values = sorted(values)
        count = len(sorted_values)
        pos1 = 0.25 * (count - 1)
        pos3 = 0.75 * (count - 1)

        def quantile(position: float) -> float:
            low = int(position)
            high = min(low + 1, count - 1)
            fraction = position - low

            return (
                sorted_values[low] * (1.0 - fraction)
                + sorted_values[high] * fraction
            )

        q1 = quantile(pos1)
        q3 = quantile(pos3)

        iqr = q3 - q1

        low_limit = q1 - 1.5 * iqr
        high_limit = q3 + 1.5 * iqr

        self.omega = [
            0.1 if value < low_limit or value > high_limit
            else 1.0
            for value in values
        ]

    def update_spline(
        self,
        points: Sequence[Point],
        f_value: Sequence[float]
    ) -> None:

        if len(points) < 2:
            raise ValueError(
                "Для построения сплайна нужны минимум две точки."
            )

        if len(points) != len(f_value):
            raise ValueError(
                "Количество точек и значений функции не совпадает."
            )

        if not self.omega:
            self.omega = [1.0] * len(points)

        if len(self.omega) != len(points):
            raise ValueError(
                "Количество весов должно совпадать "
                "с количеством узлов."
            )

        self.points = list(points)
        values = [float(value) for value in f_value]

        x_values = [point.x() for point in self.points]

        if not all(
            x_values[i] < x_values[i + 1]
            for i in range(len(x_values) - 1)
        ):
            raise ValueError(
                "Абсциссы узлов должны строго возрастать."
            )

        if not all(
            __import__("math").isfinite(value)
            for value in values
        ):
            raise ValueError(
                "Значения функции содержат NaN или бесконечность."
            )

        num_segments = len(self.points) - 1
        n = len(self.points)

        a = [0.0] * n
        b = [0.0] * n
        c = [0.0] * n

        alpha = [0.0] * n

        p = self.smooth

        for i in range(num_segments):
            for node, basis_number in (
                (i, 1),
                (i + 1, 2)
            ):
                ksi = self.transition_to_master_element(
                    i,
                    x_values[node]
                )
                basis = self.basis_function(
                    basis_number,
                    ksi
                )
                weight = self.omega[node]
                f = values[node]
                b[node] += (
                    (1.0 - p)
                    * weight
                    * basis
                    * basis
                )
                alpha[node] += (
                    (1.0 - p)
                    * weight
                    * basis
                    * f
                )
            ksi_left = self.transition_to_master_element(
                i,
                x_values[i]
            )
            ksi_right = self.transition_to_master_element(
                i,
                x_values[i + 1]
            )
            f1_left = self.basis_function(1, ksi_left)
            f2_left = self.basis_function(2, ksi_left)
            f1_right = self.basis_function(1, ksi_right)
            f2_right = self.basis_function(2, ksi_right)
            h = x_values[i + 1] - x_values[i]
            b[i] += p / h
            b[i + 1] += p / h
            a[i + 1] -= p / h
            c[i] -= p / h
        for j in range(1, n):
            if abs(b[j - 1]) < 1e-14:
                raise ArithmeticError(
                    "Нулевой ведущий элемент при прямом ходе прогонки."
                )

            factor = a[j] / b[j - 1]
            b[j] -= factor * c[j - 1]
            alpha[j] -= factor * alpha[j - 1]
        if abs(b[-1]) < 1e-14:
            raise ArithmeticError(
                "Нулевой ведущий элемент при обратном ходе прогонки."
            )
        alpha[-1] /= b[-1]
        for j in range(n - 2, -1, -1):
            if abs(b[j]) < 1e-14:
                raise ArithmeticError(
                    "Нулевой диагональный элемент матрицы."
                )
            alpha[j] = (
                alpha[j] - c[j] * alpha[j + 1]
            ) / b[j]

        self.alpha = alpha

    def get_value(self, point: Point) -> list[float]:
        if len(self.points) < 2 or not self.alpha:
            raise RuntimeError(
                "Сначала необходимо вызвать update_spline()."
            )

        x = point.x()
        eps = 1e-7
        num_segments = len(self.points) - 1

        for i in range(num_segments):
            x_left = self.points[i].x()
            x_right = self.points[i + 1].x()

            if (
                x_left - eps <= x <= x_right + eps
            ):
                h = x_right - x_left
                x_local = min(max(x, x_left), x_right)
                ksi = self.transition_to_master_element(
                    i,
                    x_local
                )
                f1 = self.basis_function(1, ksi)
                f2 = self.basis_function(2, ksi)
                value = (
                    self.alpha[i] * f1
                    + self.alpha[i + 1] * f2
                )
                derivative = (
                    self.alpha[i]
                    * self.der_basis_function(1, ksi)
                    + self.alpha[i + 1]
                    * self.der_basis_function(2, ksi)
                ) * 2.0 / h
                second_derivative = 0.0

                return [
                    value,
                    derivative,
                    second_derivative
                ]
        raise ValueError(
            f"Точка с x={x} находится вне диапазона сетки."
        )