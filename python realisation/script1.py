import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["legend.fontsize"] = 9
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.dpi"] = 200


def main():
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent

    data = pd.read_csv(base_dir / "data.csv")
    splines_values = pd.read_csv(
        base_dir / "splines_values.csv"
    )
    data = data.sort_values("n")
    splines_values = splines_values.sort_values("x")

    x = splines_values["x"].to_numpy()
    x_data = data["n"].to_numpy()
    y_original = data["ksi"].to_numpy()
    settings = [
        (
            "p=0.4",
            "Сглаживающий сплайн, p = 0.4",
            "royalblue",
            "--",
            "graph_1.png"
        ),
        (
            "p=0.8",
            "Сглаживающий сплайн, p = 0.8",
            "darkorange",
            "-.",
            "graph_2.png"
        ),
        (
            "p=0.99",
            "Сглаживающий сплайн, p = 0.99",
            "seagreen",
            ":",
            "graph_3.png"
        ),
    ]

    def draw_graph(ax, column, title, color, style):
        ax.scatter(
            x_data,
            y_original,
            color="lightcoral",
            s=9,
            alpha=0.35,
            label="Исходные данные",
            zorder=2,
            edgecolors="none"
        )

        ax.plot(
            x,
            splines_values["p=0.0"],
            color="black",
            linewidth=1.0,
            alpha=0.8,
            label="Интерполяция p = 0.0",
            zorder=3
        )

        ax.plot(
            x,
            splines_values[column],
            color=color,
            linestyle=style,
            linewidth=2.0,
            label=title,
            zorder=4
        )

        ax.set_title(title)
        ax.set_xlabel("Номер наблюдения x")
        ax.set_ylabel("Значение функции")

        ax.grid(
            True,
            linestyle="--",
            linewidth=0.6,
            alpha=0.3
        )

        ax.legend(loc="best", framealpha=0.9)
        ax.margins(x=0.01, y=0.08)
        ax.set_xlim(x.min(), x.max())
    for column, title, color, style, filename in settings:
        fig, ax = plt.subplots(figsize=(12, 5.5))

        draw_graph(
            ax,
            column,
            title,
            color,
            style
        )

        fig.tight_layout()

        fig.savefig(
            base_dir / filename,
            bbox_inches="tight"
        )

        plt.show()
        plt.close(fig)

        print(f"Сохранён график: {base_dir / filename}")
    fig, axes = plt.subplots(
        3,
        1,
        figsize=(13, 12),
        sharex=True
    )

    for ax, (
        column,
        title,
        color,
        style,
        filename
    ) in zip(axes, settings):

        draw_graph(
            ax,
            column,
            title,
            color,
            style
        )

    fig.suptitle(
        "Сравнение сглаживающих сплайнов с интерполяцией",
        fontsize=15,
        y=1.005
    )

    fig.tight_layout()

    output_path = base_dir / "all_splines_comparison.png"

    fig.savefig(
        output_path,
        bbox_inches="tight"
    )

    plt.show()
    plt.close(fig)

    print(f"Сохранён общий график: {output_path}")
    print("Все графики построены и сохранены.")


if __name__ == "__main__":
    main()