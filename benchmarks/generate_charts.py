"""generate_charts.py

A docs/research/node-deno-bun.md oldalba ágyazott két ábrát állítja elő:

  1. encryption-chart-v3.png - AES-GCM titkosítási idő üzenetméret és
     futtatókörnyezet szerint, log-log skálán, 95%-os konfidencia-
     intervallummal (ahol a szórás ismert).
  2. warmup-cutoff-chart.png - a warm-up-becslő által eldobott minták
     aránya méretenként és futtatókörnyezetenként (csoportosított
     oszlopdiagram).

Bemenet: docs/benchmarks/results/*.csv
  Ezeket a fájlokat a benchmark szkriptek (encrypt-benchmark-v2.mjs,
  encrypt-benchmark-v3-pow2.mjs) --csv kapcsolóval automatikusan
  előállítják egy futtatás után (ld. a szkriptek --help kimenetét).
  A jelenlegi CSV-k a docs/research/node-deno-bun.md-ben már publikált
  összesített értékekből lettek visszafejtve (n = összes - eldobott,
  ld. a warm-up táblázatot); ahol a nyers szórás nem lett annak idején
  fájlba mentve, ott a stddev_ms mező üresen marad, és az adott pontnál
  a diagram nem rajzol konfidencia-sávot.

Futtatás:
    pip install -r requirements.txt
    python docs/benchmarks/generate_charts.py
"""

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).parent
RESULTS = HERE / "results"

RUNTIME_COLORS = {
    "node": "#5fa052",
    "deno": "#2b6cb0",
    "bun": "#e0994f",
}
RUNTIME_LABELS = {
    "node": "Node.js",
    "deno": "Deno",
    "bun": "Bun",
}


def runtime_key(raw_name):
    """'Node.js v22.22.2' / 'Deno 2.9.1' / 'Bun 1.3.14' -> 'node' / 'deno' / 'bun'.
    A dokumentált (történeti) CSV-kben már eleve a rövid alak szerepel."""
    lower = raw_name.lower()
    if "deno" in lower:
        return "deno"
    if "bun" in lower:
        return "bun"
    return "node"


def read_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            rows.append(line)
    return list(csv.DictReader(rows))


def normalize_row(row):
    """A benchmark szkript élő CSV-kimenete (trimmed_avg_ms/trimmed_stddev_ms)
    és a dokumentációból visszafejtett történeti CSV (avg_ms/stddev_ms) közötti
    oszlopnév-eltérést egységesíti."""
    avg = row.get("avg_ms") or row.get("trimmed_avg_ms")
    stddev = row.get("stddev_ms") or row.get("trimmed_stddev_ms") or ""
    return {"runtime": runtime_key(row["runtime"]), "size_bytes": row["size_bytes"], "n": row["n"],
            "avg_ms": avg, "stddev_ms": stddev}


def latest_or_fallback(latest_name, fallback_name):
    latest = RESULTS / latest_name
    if latest.exists():
        print(f"Friss mérési adat használva: {latest.name}")
        return latest
    fallback = RESULTS / fallback_name
    print(f"Nincs friss mérés ({latest_name}), a dokumentált értékekre esik vissza: {fallback.name}")
    return fallback


def plot_encryption_chart():
    csv_path = latest_or_fallback("latest-run.csv", "encryption-v3-decimal.csv")
    rows = [normalize_row(r) for r in read_csv(csv_path)]
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=150)

    for runtime in ("node", "deno", "bun"):
        points = [r for r in rows if r["runtime"] == runtime]
        if not points:
            continue
        points.sort(key=lambda r: int(r["size_bytes"]))
        sizes = [int(r["size_bytes"]) for r in points]
        avgs = [float(r["avg_ms"]) for r in points]

        ax.plot(
            sizes, avgs, "o", color=RUNTIME_COLORS[runtime],
            label=RUNTIME_LABELS[runtime], markersize=5,
        )

        # lineáris regresszió (idő = a + b * méret), szaggatott vonallal
        n_pts = len(sizes)
        mean_x = sum(sizes) / n_pts
        mean_y = sum(avgs) / n_pts
        b = sum((x - mean_x) * (y - mean_y) for x, y in zip(sizes, avgs)) / sum((x - mean_x) ** 2 for x in sizes)
        a = mean_y - b * mean_x
        fit_x = [min(sizes), max(sizes)]
        fit_y = [a + b * x for x in fit_x]
        ax.plot(fit_x, fit_y, "--", color=RUNTIME_COLORS[runtime], linewidth=1.2, alpha=0.7)

        # 95%-os CI csak azoknál a pontoknál, ahol van rögzített szórás
        for r in points:
            if r["stddev_ms"]:
                n = int(r["n"])
                avg = float(r["avg_ms"])
                stddev = float(r["stddev_ms"])
                ci95 = 1.96 * stddev / math.sqrt(n)
                ax.errorbar(
                    int(r["size_bytes"]), avg, yerr=ci95,
                    color=RUNTIME_COLORS[runtime], capsize=3, linewidth=1.2,
                )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Üzenetméret (byte, log skála)")
    ax.set_ylabel("Titkosítási idő (ms, log skála)")
    ax.set_title("AES-GCM titkosítási idő üzenetméret és futtatókörnyezet szerint")
    ax.grid(True, which="both", linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(title="folytonos: mérés, szaggatott: lineáris illesztés")
    fig.tight_layout()
    out = HERE / "encryption-chart-v3.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Mentve: {out}")


def read_warmup_rows():
    latest = RESULTS / "latest-run.csv"
    if latest.exists():
        print("Friss mérési adat használva: latest-run.csv")
        rows = []
        for r in read_csv(latest):
            dropped = int(r["cutoff"])
            total = int(r["n"]) + dropped
            rows.append({"runtime": runtime_key(r["runtime"]), "size_bytes": r["size_bytes"],
                         "total_n": str(total), "dropped_n": str(dropped)})
        return rows
    print("Nincs friss mérés (latest-run.csv), a dokumentált értékekre esik vissza: warmup-cutoff.csv")
    return read_csv(RESULTS / "warmup-cutoff.csv")


def plot_warmup_chart():
    rows = read_warmup_rows()
    sizes = sorted({int(r["size_bytes"]) for r in rows}, key=int)
    runtimes = sorted({r["runtime"] for r in rows})

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)
    x = range(len(sizes))
    width = 0.8 / max(len(runtimes), 1)

    for i, runtime in enumerate(runtimes):
        pct = []
        for size in sizes:
            row = next(r for r in rows if r["runtime"] == runtime and int(r["size_bytes"]) == size)
            pct.append(100 * int(row["dropped_n"]) / int(row["total_n"]))
        offsets = [xi + (i - (len(runtimes) - 1) / 2) * width for xi in x]
        ax.bar(offsets, pct, width=width, label=RUNTIME_LABELS[runtime], color=RUNTIME_COLORS[runtime])

    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{s:,}".replace(",", " ") for s in sizes], rotation=30, ha="right")
    ax.set_xlabel("Üzenetméret (byte)")
    ax.set_ylabel("Eldobott (warm-up) minták aránya (%)")
    ax.set_title("Warm-up-becslő által eldobott minták aránya méret és futtatókörnyezet szerint")
    ax.grid(True, axis="y", linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend()
    fig.tight_layout()
    out = HERE / "warmup-cutoff-chart.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Mentve: {out}")


def plot_warmup_illustration():
    """A warm-up-becslő tényleges hatását szemlélteti egy konkrét
    (futtatókörnyezet, méret) idősoron: a nyers mérési idők iterációnként,
    a becsült cutoff-vonallal és a 2%-os stabilizációs küszöbbel.
    Csak akkor fut, ha van nyers minta-export (--raw-samples)."""
    raw_path = RESULTS / "latest-run-raw-samples.csv"
    if not raw_path.exists():
        print(
            "Kihagyva: warmup-illustration-chart.png (nincs nyers minta-export - "
            "futtasd újra a benchmarkot --raw-samples=... kapcsolóval)"
        )
        return

    rows = read_csv(raw_path)
    # egy jellemző, kis méretű pontot választunk, ahol a warm-up jól látszik
    candidate_sizes = sorted({int(r["size_bytes"]) for r in rows})
    size = candidate_sizes[0]
    runtime = runtime_key(rows[0]["runtime"])
    series = [r for r in rows if int(r["size_bytes"]) == size]
    series.sort(key=lambda r: int(r["sample_index"]))
    times = [float(r["time_ms"]) for r in series]

    window = 20
    window_avgs = [
        sum(times[i:i + window]) / window
        for i in range(0, len(times) - len(times) % window, window)
    ]
    cutoff = 0
    for i in range(1, len(window_avgs) - 1):
        change = abs(window_avgs[i] - window_avgs[i - 1]) / window_avgs[i - 1]
        if change < 0.02:
            cutoff = i * window
            break

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    ax.plot(range(len(times)), times, ".", color="#999", markersize=4, alpha=0.6, label="nyers minta")
    ax.axvline(cutoff, color=ARROW_COLOR, linestyle="--", linewidth=1.6,
                label=f"becsült warm-up cutoff (i={cutoff})")
    fig.tight_layout()
    ax.set_xlabel("Iteráció sorszáma")
    ax.set_ylabel("Titkosítási idő (ms)")
    ax.set_title(f"Warm-up hatás szemléltetése ({RUNTIME_LABELS[runtime]}, {size} byte)")
    ax.legend()
    out = HERE / "warmup-illustration-chart.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Mentve: {out}")


ARROW_COLOR = "#c0392b"

if __name__ == "__main__":
    plot_encryption_chart()
    plot_warmup_chart()
    plot_warmup_illustration()
