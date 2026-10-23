
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Настройки отображения
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["legend.fontsize"] = 9
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.dpi"] = 200

# Загрузка данных
data = pd.read_csv("data.csv")
splines_values = pd.read_csv("splines_values.csv")

# Сортируем точки по x на случай, если порядок нарушен
data = data.sort_values("n")
splines_values = splines_values.sort_values("x")

x = splines_values["x"].to_numpy()
y_original = data["ksi"].to_numpy()

# Сетка исходных наблюдений совпадает с сеткой сплайнов
x_data = data["n"].to_numpy()

# Настройки трех графиков
settings = [
    ("p=0.4", "Сглаживающий сплайн, p = 0.4",
     "royalblue", "--", "График 1"),

    ("p=0.8", "Сглаживающий сплайн, p = 0.8",
     "darkorange", "-.", "График 2"),

    ("p=0.99", "Сглаживающий сплайн, p = 0.99",
     "seagreen", ":", "График 3"),
]

def draw_graph(ax, column, title, color, style):
    # Исходные наблюдения
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

    # Интерполяционный сплайн p = 0
    ax.plot(
        x,
        splines_values["p=0.0"],
        color="black",
        linewidth=1.0,
        alpha=0.8,
        label="Интерполяция p = 0.0",
        zorder=3
    )

    # Сглаживающий сплайн
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
    ax.grid(True, linestyle="--", linewidth=0.6, alpha=0.3)
    ax.legend(loc="best", framealpha=0.9)
    ax.margins(x=0.01, y=0.08)

    # Единый формат оси x
    ax.set_xlim(x.min(), x.max())


# --------------------------------------------------
# 1. Три отдельных графика
# --------------------------------------------------

for column, title, color, style, filename in settings:
    fig, ax = plt.subplots(figsize=(12, 5.5))

    draw_graph(ax, column, title, color, style)

    fig.tight_layout()
    fig.savefig(
        filename.replace(" ", "_").lower() + ".png",
        bbox_inches="tight"
    )

    plt.show()
    plt.close(fig)


# --------------------------------------------------
# 2. Общая картинка с тремя графиками
# --------------------------------------------------

fig, axes = plt.subplots(
    3, 1,
    figsize=(13, 12),
    sharex=True
)

for ax, (column, title, color, style, filename) in zip(
    axes, settings
):
    draw_graph(ax, column, title, color, style)

fig.suptitle(
    "Сравнение сглаживающих сплайнов с интерполяцией",
    fontsize=15,
    y=1.005
)

fig.tight_layout()
fig.savefig(
    "all_splines_comparison.png",
    bbox_inches="tight"
)

plt.show()
plt.close(fig)

print("Все графики построены и сохранены.")
