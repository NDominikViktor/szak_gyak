"""generate_diagrams.py

A dokumentációban szereplő, kézzel rajzolt (nem mérési adatból származó)
sematikus ábrákat állítja elő:

  - architecture-diagram.png  (docs/architecture.md)
  - omemo-flow-diagram.png    (docs/research/chat-alternatives.md)
  - matrix-flow-diagram.png   (docs/research/chat-alternatives.md)

Futtatás:
    pip install -r requirements.txt
    python docs/generate_diagrams.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).parent

CLIENT_FILL = "#2b3b52"
SUB_FILL = "#3d5573"
SERVER_FILL = "#5a4030"
EDGE = "#c9d4e0"
TEXT = "#f0f3f7"
ARROW = "#e0994f"


def box(ax, xy, w, h, label, fill, fontsize=10, sub=False):
    x, y = xy
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            linewidth=1.2, edgecolor=EDGE, facecolor=fill,
        )
    )
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
             color=TEXT, fontsize=fontsize, wrap=True)


def dbl_arrow(ax, p1, p2, color=ARROW, style="<->", lw=1.6, connectionstyle="arc3,rad=0"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, color=color,
                                  linewidth=lw, mutation_scale=14,
                                  connectionstyle=connectionstyle))


def plot_architecture():
    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

    # -- Kliens A (bal) --
    box(ax, (0.4, 3.4), 3.0, 3.3, "", CLIENT_FILL)
    ax.text(1.9, 6.4, "Kliens A (böngésző)", ha="center", color=TEXT, fontsize=11, weight="bold")
    box(ax, (0.7, 5.5), 2.4, 0.7, "UI", SUB_FILL)
    box(ax, (0.7, 4.55), 2.4, 0.7, "WebCrypto API", SUB_FILL)
    box(ax, (0.7, 3.6), 2.4, 0.7, "Kulcstároló\n(IndexedDB)", SUB_FILL)
    dbl_arrow(ax, (1.9, 5.5), (1.9, 5.25))
    dbl_arrow(ax, (1.9, 4.55), (1.9, 4.3))

    # -- Kliens B (jobb, tükrözve) --
    box(ax, (6.6, 3.4), 3.0, 3.3, "", CLIENT_FILL)
    ax.text(8.1, 6.4, "Kliens B (böngésző)", ha="center", color=TEXT, fontsize=11, weight="bold")
    box(ax, (6.9, 5.5), 2.4, 0.7, "UI", SUB_FILL)
    box(ax, (6.9, 4.55), 2.4, 0.7, "WebCrypto API", SUB_FILL)
    box(ax, (6.9, 3.6), 2.4, 0.7, "Kulcstároló\n(IndexedDB)", SUB_FILL)
    dbl_arrow(ax, (8.1, 5.5), (8.1, 5.25))
    dbl_arrow(ax, (8.1, 4.55), (8.1, 4.3))

    # -- Szerver (alul, középen) --
    box(ax, (3.5, 0.5), 3.0, 1.4, "Szerver (Node.js)", SERVER_FILL, fontsize=11)

    # -- Kapcsolatok: mindkét kliens <-> szerver, oda-vissza --
    dbl_arrow(ax, (1.9, 3.4), (4.3, 1.9), connectionstyle="arc3,rad=-0.15")
    dbl_arrow(ax, (8.1, 3.4), (5.7, 1.9), connectionstyle="arc3,rad=0.15")

    ax.text(2.7, 2.55, "titkosított\nüzenet +\nesemény", ha="center", color=EDGE, fontsize=8, style="italic")
    ax.text(7.3, 2.55, "titkosított\nüzenet +\nesemény", ha="center", color=EDGE, fontsize=8, style="italic")

    ax.set_title("Rendszerarchitektúra — komponensek és adatfolyam", color="#1a1a1a", fontsize=12, pad=14)
    fig.tight_layout()
    out = HERE / "architecture-diagram.png"
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print(f"Mentve: {out}")


def step_arrow(ax, y, label, note=""):
    dbl_arrow(ax, (0.9, y), (7.1, y), style="->", lw=1.4)
    ax.text(4.0, y + 0.18, label, ha="center", color="#333", fontsize=9)
    if note:
        ax.text(4.0, y - 0.22, note, ha="center", color="#777", fontsize=7.5, style="italic")


def plot_omemo_flow():
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=150)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 6.6)
    ax.axis("off")

    box(ax, (0.2, 0.2), 1.4, 0.8, "Küldő\nkliens", "#3d5573", fontsize=9)
    box(ax, (6.4, 0.2), 1.4, 0.8, "Címzett\nkliens", "#3d5573", fontsize=9)
    box(ax, (3.1, 0.2), 1.8, 0.8, "XMPP szerver\n(PubSub/PEP)", "#5a4030", fontsize=8.5)

    steps = [
        (5.7, "1. Címzett publikálja a kulcscsomagját (bundle)", "identitáskulcs + aláírt PreKey + ~100 egyszeri PreKey"),
        (4.7, "2. Küldő lekéri a bundle-t a PubSub-on keresztül", "XEP-0060 / XEP-0163"),
        (3.7, "3. X3DH kulcscsere a bundle alapján", "közös titok létrehozása, PreKey elhasználása"),
        (2.7, "4. Double Ratchet inicializálása, első üzenet", "AES-256-CBC + HMAC-SHA256 titkosítással"),
        (1.7, "5. Minden további üzenetnél új ratchet-lépés", "forward secrecy: régi kulcs nem fejt vissza újat"),
    ]
    for y, label, note in steps:
        step_arrow(ax, y, label, note)

    ax.set_title("OMEMO (XMPP) — üzenetküldés folyamata", fontsize=12, pad=10)
    fig.tight_layout()
    out = HERE / "research" / "omemo-flow-diagram.png"
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print(f"Mentve: {out}")


def plot_matrix_flow():
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=150)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 6.6)
    ax.axis("off")

    box(ax, (0.2, 0.2), 1.4, 0.8, "Küldő\nkliens", "#3d5573", fontsize=9)
    box(ax, (6.4, 0.2), 1.4, 0.8, "Szoba\ntöbbi tagja", "#3d5573", fontsize=9)
    box(ax, (3.1, 0.2), 1.8, 0.8, "Home szerver\n(esemény-DAG)", "#5a4030", fontsize=8.5)

    steps = [
        (5.7, "1. Olm páronkénti munkamenet minden eszközzel", "Double Ratchet, 1:1, ha még nincs"),
        (4.7, "2. Küldő generál egy Megolm session-kulcsot", "szobánként + küldő eszközönként egy"),
        (3.7, "3. A session-kulcsot Olm-on titkosítva megosztja", "minden résztvevő eszközzel, egyszer"),
        (2.7, "4. Üzenetek Megolm-mal titkosítva, egy közös racsnival", "csak-előre-forgatható (one-way ratchet)"),
        (1.7, "5. Szerver az eseményt terjeszti (replikálja)", "tartalmat nem látja, csak a DAG-ba fűzi"),
    ]
    for y, label, note in steps:
        step_arrow(ax, y, label, note)

    ax.set_title("Matrix (Olm/Megolm) — csoportos üzenetküldés folyamata", fontsize=12, pad=10)
    fig.tight_layout()
    out = HERE / "research" / "matrix-flow-diagram.png"
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print(f"Mentve: {out}")


if __name__ == "__main__":
    plot_architecture()
    plot_omemo_flow()
    plot_matrix_flow()
