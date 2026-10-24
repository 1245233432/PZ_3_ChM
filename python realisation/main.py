import csv
import random
from pathlib import Path

from point import Point
from smoothing_spline import SmoothingSpline


def main():
    N = 1953
    M = 1.01
    S = 3.88
    p_values = [0.0, 0.4, 0.8, 0.99]
    rng = random.Random()
    func = [
        rng.gauss(M, S)
        for _ in range(N)
    ]

    mesh = [
        Point(float(i), 0.0, 0.0)
        for i in range(N)
    ]
    smooth_splines = []
    for p in p_values:
        spline = SmoothingSpline(p)
        spline.set_omega(func)
        spline.update_spline(mesh, func)
        smooth_splines.append(spline)
    output_dir = Path(__file__).resolve().parent
    data_path = output_dir / "data.csv"
    with data_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["n", "ksi"])
        for i in range(N):
            writer.writerow([
                mesh[i].x(),
                func[i]
            ])
    print(f"Записан data.csv: {data_path}")
    spline_path = output_dir / "splines_values.csv"

    with spline_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        header = ["x"] + [
            f"p={p:.1f}" if p != 0.99 else "p=0.99"
            for p in p_values
        ]
        writer.writerow(header)
        for point in mesh:
            row = [point.x()]

            for spline in smooth_splines:
                result = spline.get_value(point)
                row.append(result[0])

            writer.writerow(row)
    print(f"Записан splines_values.csv: {spline_path}")
if __name__ == "__main__":
    main()