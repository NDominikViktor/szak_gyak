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

        # súlyozott (relatív hibát minimalizáló) lineáris regresszió:
        # idő = a + b*méret, az idő/méret = a/méret + b átalakításon
        # keresztül illesztve, hogy a nagyságrendek egyenlő súlyt kapjanak
        # (a közönséges OLS a legnagyobb méretű pont miatt torzítana,
        # ld. "Az üzenetméret és a titkosítási idő közötti összefüggés")
        n_pts = len(sizes)
        X = [1 / s for s in sizes]
        Y = [t / s for s, t in zip(sizes, avgs)]
        mean_x = sum(X) / n_pts
        mean_y = sum(Y) / n_pts
        a = sum((x - mean_x) * (y - mean_y) for x, y in zip(X, Y)) / sum((x - mean_x) ** 2 for x in X)
        b = mean_y - a * mean_x
        # A szaggatott vonalat csak addig a méretig rajzoljuk, ameddig a
        # modell ténylegesen érvényes (~1 MB-ig) - fölötte a modell
        # szándékosan alulbecsül (ld. dokumentáció), és a teljes
        # tartományra kihúzva félrevezető lenne az ábrán.
        valid_max = min(max(sizes), 1_000_000)
        fit_x = [min(sizes), valid_max]
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
    ax.legend(title="folytonos: mérés, szaggatott: súlyozott lin. illesztés")
    fig.tight_layout()
    out = HERE / "encryption-chart-v3.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Mentve: {out}")


def plot_regression_residuals():
    """A súlyozott illesztés becsült és a ténylegesen mért idők közötti
    előjeles, relatív eltérését ábrázolja méretenként - ugyanaz a
    'mennyire jó az illesztés' kérdés, mint az 5. táblázat, csak
    vizuálisan, minden ponthoz."""
    csv_path = latest_or_fallback("latest-run.csv", "encryption-v3-decimal.csv")
    rows = [normalize_row(r) for r in read_csv(csv_path)]

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    for runtime in ("node", "deno", "bun"):
        points = [r for r in rows if r["runtime"] == runtime]
        if not points:
            continue
        points.sort(key=lambda r: int(r["size_bytes"]))
        sizes = [int(r["size_bytes"]) for r in points]
        avgs = [float(r["avg_ms"]) for r in points]

        n_pts = len(sizes)
        X = [1 / s for s in sizes]
        Y = [t / s for s, t in zip(sizes, avgs)]
        mean_x = sum(X) / n_pts
        mean_y = sum(Y) / n_pts
        a = sum((x - mean_x) * (y - mean_y) for x, y in zip(X, Y)) / sum((x - mean_x) ** 2 for x in X)
        b = mean_y - a * mean_x

        rel_error = [100 * ((a + b * s) - t) / t for s, t in zip(sizes, avgs)]
        ax.plot(sizes, rel_error, "o-", color=RUNTIME_COLORS[runtime],
                label=RUNTIME_LABELS[runtime], markersize=6)

    ax.axhline(0, color="#888", linewidth=1, linestyle="-")
    ax.axvline(1_000_000, color="#888", linewidth=1, linestyle=":")
    ax.text(1_000_000, ax.get_ylim()[1] * 0.9, " illesztés\n érvényes\n tartománya\n vége →",
            fontsize=7, color="#888")
    ax.set_xscale("log")
    ax.set_xlabel("Üzenetméret (byte, log skála)")
    ax.set_ylabel("Előjeles relatív eltérés: (becsült - mért) / mért, %")
    ax.set_title("A súlyozott illesztés hibája méretenként (reziduálok)")
    ax.grid(True, which="both", linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend()
    fig.tight_layout()
    out = HERE / "regression-residuals-chart.png"
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


def _plot_distribution_for_size(rows, size, out_name):
    runtime = runtime_key(rows[0]["runtime"])
    series = [r for r in rows if int(r["size_bytes"]) == size]
    series.sort(key=lambda r: int(r["sample_index"]))
    times = [float(r["time_ms"]) for r in series]

    # ugyanaz a warm-up-cutoff logika, mint az illusztráció ábránál,
    # hogy csak a trimmelt (stabilizálódás utáni) mintákat vizsgáljuk
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
    trimmed = times[cutoff:]
    if len(trimmed) < 5:
        print(f"Kihagyva: {out_name} (túl kevés trimmelt minta: {len(trimmed)})")
        return

    n = len(trimmed)
    mean = sum(trimmed) / n
    variance = sum((t - mean) ** 2 for t in trimmed) / (n - 1)
    stddev = variance ** 0.5

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    ax.hist(trimmed, bins=20, density=True, color="#5fa052", alpha=0.6, label="trimmelt minták")

    xs = [mean - 4 * stddev + i * (8 * stddev / 200) for i in range(201)]
    xs = [x for x in xs if x > 0] or [mean * 0.01 * i for i in range(1, 201)]

    # normális (momentum-módszer: mu=átlag, sigma=tapasztalati szórás)
    ys_norm = [
        (1 / (stddev * (2 * math.pi) ** 0.5)) * math.exp(-((x - mean) ** 2) / (2 * stddev ** 2))
        for x in xs
    ]
    ax.plot(xs, ys_norm, "-", color=ARROW_COLOR, linewidth=1.8,
             label=f"normális (μ={mean:.3f}, σ={stddev:.3f})")

    # log-normális (momentum-módszer): a nyers átlag/szórásból vezetjük le
    # a log-térbeli mu/sigma paramétereket
    ln_sigma2 = math.log(1 + variance / mean ** 2)
    ln_sigma = ln_sigma2 ** 0.5
    ln_mu = math.log(mean) - ln_sigma2 / 2
    ys_lognorm = [
        (1 / (x * ln_sigma * (2 * math.pi) ** 0.5)) * math.exp(-((math.log(x) - ln_mu) ** 2) / (2 * ln_sigma2))
        for x in xs
    ]
    ax.plot(xs, ys_lognorm, "-", color="#2b6cb0", linewidth=1.8,
             label=f"log-normális (μ={ln_mu:.3f}, σ={ln_sigma:.3f})")

    # Gamma-eloszlás (momentum-módszer): shape k, scale theta
    k_shape = mean ** 2 / variance
    theta_scale = variance / mean
    ys_gamma = [
        (x ** (k_shape - 1) * math.exp(-x / theta_scale)) / (theta_scale ** k_shape * math.gamma(k_shape))
        for x in xs
    ]
    ax.plot(xs, ys_gamma, "-", color="#e0994f", linewidth=1.8,
             label=f"Gamma (k={k_shape:.3f}, θ={theta_scale:.3f})")

    ax.set_xlabel("Titkosítási idő (ms)")
    ax.set_ylabel("Sűrűség")
    ax.set_title(f"Mérési idők eloszlása ({RUNTIME_LABELS[runtime]}, {size} byte, n={n}, warm-up nélkül)")
    ax.legend()
    fig.tight_layout()
    out = HERE / out_name
    fig.savefig(out)
    plt.close(fig)
    print(f"Mentve: {out}")


def plot_distribution():
    """A mérési idők eloszlását szemlélteti (hisztogram + illesztett
    normális sűrűségfüggvény) a trimmelt (warm-up utáni) mintákon - a
    legkisebb méretre, valamint egy "nagy, de még kellő mintaszámú"
    méretre is (utóbbinál, ahol az idő már messze van a 0-tól,
    jellegzetesebben elválna egy log-normális/Gamma-eloszlástól a
    normális, ha az a helyesebb modell).

    Fontos: a *legnagyobb byte-méretű* mérési pont NEM feltétlenül a
    legjobb választás ehhez, mert a benchmark szkript a nagy méreteknél
    szándékosan kevesebb iterációt futtat (ld. `iterationsFor()`) - a
    100 MB-os pontnál pl. csak n=15 minta van, ami egy hisztogramhoz
    kevés. Ehelyett azt a méretet választjuk, ami a nagyobbik felében
    van a mérettartománynak, ÉS a legtöbb (trimmelt) mintával
    rendelkezik közülük.

    Csak akkor fut, ha van nyers minta-export."""
    raw_path = RESULTS / "latest-run-raw-samples.csv"
    if not raw_path.exists():
        print("Kihagyva: distribution-chart*.png (nincs nyers minta-export)")
        return

    rows = read_csv(raw_path)
    sizes = sorted({int(r["size_bytes"]) for r in rows})
    _plot_distribution_for_size(rows, sizes[0], "distribution-chart.png")

    if len(sizes) > 1:
        upper_half = sizes[len(sizes) // 2:]
        counts = {s: sum(1 for r in rows if int(r["size_bytes"]) == s) for s in upper_half}
        # az "elég sok mintával rendelkező" méretek közül a legnagyobbat
        # választjuk, hogy az idő is minél messzebb essen a 0-tól
        well_sampled = [s for s in upper_half if counts[s] >= 100]
        large_size = max(well_sampled) if well_sampled else max(upper_half, key=lambda s: counts[s])
        _plot_distribution_for_size(rows, large_size, "distribution-chart-large.png")


ARROW_COLOR = "#c0392b"

if __name__ == "__main__":
    plot_encryption_chart()
    plot_regression_residuals()
    plot_warmup_chart()
    plot_warmup_illustration()
    plot_distribution()
