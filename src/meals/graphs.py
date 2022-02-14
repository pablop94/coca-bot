import matplotlib.pyplot as plt
import random
from io import BytesIO
from os import remove


def send_history_chart(graph, image_callback):
    image_name = get_image_name()
    save_graph_image(graph, image_name)
    with open(image_name, "rb") as image:
        image_callback(image, caption="Hice un grafiquito")

    remove(image_name)


def get_image_name():
    return f"history_chart{random.randint(0, 10000)}.png"


def save_graph_image(graph, image_name):
    labels = graph["names"]
    sizes = [value / graph["total"] for value in graph["values"]]
    explode = (0,) * len(graph["names"])

    fig1, ax1 = plt.subplots()
    ax1.pie(
        sizes,
        explode=explode,
        labels=labels,
        autopct="%1.1f%%",
        shadow=False,
        startangle=90,
    )
    ax1.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

    f = BytesIO()
    plt.savefig(f)

    with open(image_name, "wb") as ff:
        ff.write(f.getbuffer())
