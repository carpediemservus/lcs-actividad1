"""Benchmarks de las tres versiones de LCS.

Para cada (version, n) lanza un subproceso que:
  - genera las cadenas con semilla fija,
  - calcula la LCS (la subsecuencia) y registra su longitud,
  - mide el tiempo de CPU (mediana de REPEATS),
  - mide la memoria pico de Python con tracemalloc.
El proceso padre aplica timeout, escribe un CSV, dos graficas (log-log) y
guarda las parejas de cadenas y las LCS obtenidas en results/datos/.

Uso:
    python3 src/benchmark.py --csv results/resultados.csv
"""
import argparse
import csv
import json
import random
import statistics
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ALPHABET = "ACGT"
SEED = 42
REPEATS = 5
TIMEOUT = 60  # segundos

CONFIGS = {
    "A": [8, 10, 12, 14, 16, 18, 20],
    "B": [50, 100, 250, 500, 1000],
    "C": [50, 100, 250, 500, 1000],
}


# ----------------------- worker -----------------------
def _gen(n: int, seed: int) -> tuple:
    rng = random.Random(seed)
    return (
        "".join(rng.choice(ALPHABET) for _ in range(n)),
        "".join(rng.choice(ALPHABET) for _ in range(n)),
    )


def worker(version: str, n: int, seed: int) -> None:
    from lcs import lcs_recursiva, lcs_hirschberg, lcs_dp
    fn = {"A": lcs_recursiva, "B": lcs_hirschberg, "C": lcs_dp}[version]

    a, b = _gen(n, seed)

    # tiempo (mediana de REPEATS)
    times, result = [], None
    for _ in range(REPEATS):
        t0 = time.process_time()
        result = fn(a, b)
        times.append(time.process_time() - t0)

    # memoria pico (asignaciones Python durante la llamada)
    tracemalloc.start()
    fn(a, b)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    print(json.dumps({
        "version": version,
        "n": n,
        "time_s": statistics.median(times),
        "mem_kb": peak / 1024.0,
        "lcs": len(result),
        "sub": result,
    }))


# ----------------------- driver -----------------------
def run_one(version: str, n: int) -> dict:
    cmd = [sys.executable, str(Path(__file__).resolve()),
           "--worker", version, str(n), str(SEED)]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=TIMEOUT, check=True)
        return json.loads(out.stdout)
    except subprocess.TimeoutExpired:
        return {"version": version, "n": n, "time_s": None,
                "mem_kb": None, "lcs": None, "status": "timeout"}


def write_csv(rows, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["version", "n", "time_ms", "mem_kb", "lcs", "status"])
        for r in rows:
            t = "" if r.get("time_s") is None else f"{r['time_s']*1000:.3f}"
            m = "" if r.get("mem_kb") is None else f"{r['mem_kb']:.2f}"
            w.writerow([r["version"], r["n"], t, m,
                        r.get("lcs", ""), r.get("status", "ok")])


def write_data(rows, outdir: Path) -> None:
    """Guarda cada pareja (X, Y) y la LCS obtenida por la version C."""
    d = outdir / "datos"
    d.mkdir(parents=True, exist_ok=True)
    for r in rows:
        if r["version"] != "C" or r.get("sub") is None:
            continue
        x, y = _gen(r["n"], SEED)
        (d / f"n{r['n']}.txt").write_text(
            f"X={x}\nY={y}\nLCS={r['sub']}\n", encoding="utf-8")
    print(f"[benchmark] datos -> {d}")


def write_plots(rows, outdir: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[benchmark] matplotlib no instalado: se omiten las graficas.")
        return

    outdir.mkdir(parents=True, exist_ok=True)
    colors = {"A": "tab:green", "B": "tab:blue", "C": "tab:red"}
    marks = {"A": "^", "B": "o", "C": "s"}

    for field, fname, ylabel, title in [
        ("time_s", "tiempo.png", "tiempo CPU (s)", "Tiempo de CPU"),
        ("mem_kb", "memoria.png", "memoria pico (KB)", "Memoria maxima"),
    ]:
        fig, ax = plt.subplots(figsize=(5.5, 4))
        for v in ("A", "B", "C"):
            pts = [(r["n"], r[field]) for r in rows
                   if r["version"] == v and r.get(field) is not None]
            if not pts:
                continue
            xs, ys = zip(*sorted(pts))
            ax.plot(xs, ys, marker=marks[v], color=colors[v],
                    label=f"Version {v}")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("n")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, which="both", ls=":", alpha=0.4)
        ax.legend()
        fig.tight_layout()
        fig.savefig(outdir / fname, dpi=150)
        plt.close(fig)
        print(f"[benchmark] grafica -> {outdir / fname}")


# ----------------------- main -----------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", nargs=3, metavar=("VERSION", "N", "SEED"))
    ap.add_argument("--csv", default="results/resultados.csv")
    args = ap.parse_args()

    if args.worker:
        v, n, s = args.worker
        worker(v, int(n), int(s))
        return

    rows = []
    for version, sizes in CONFIGS.items():
        for n in sizes:
            print(f"[benchmark] version {version}, n={n} ...", flush=True)
            r = run_one(version, n)
            rows.append(r)
            if r.get("status") == "timeout":
                print("   -> timeout")
            else:
                print(f"   -> t={r['time_s']*1000:8.2f} ms   "
                      f"mem={r['mem_kb']:8.1f} KB   LCS={r['lcs']}")

    csv_path = Path(args.csv)
    write_csv(rows, csv_path)
    print(f"[benchmark] CSV -> {csv_path}")
    write_data(rows, csv_path.parent)
    write_plots(rows, csv_path.parent)


if __name__ == "__main__":
    main()
