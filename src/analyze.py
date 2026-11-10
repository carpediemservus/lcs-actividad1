"""Convierte results/resultados.csv en las Tablas 2 y 3 del informe (LaTeX).

Uso:
    python3 src/analyze.py
    python3 src/analyze.py --csv otro.csv
    python3 src/analyze.py --out tablas.tex
"""
import argparse
import csv
from pathlib import Path


def fmt_time(ms):
    """Tiempo en ms, con 2 decimales y separador decimal LaTeX (coma)."""
    if ms is None or ms == "":
        return "---"
    v = float(ms)
    if v >= 1000:
        s = f"{v/1000:.2f}".rstrip("0").rstrip(".")
        s = s.replace(".", "{,}")
        return f"{s}\\,s"
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s.replace(".", "{,}")


def fmt_mem(kb):
    """Memoria: KB si <1024, MB en otro caso (con 2 decimales)."""
    if kb is None or kb == "":
        return "---"
    v = float(kb)
    if v >= 1024:
        s = f"{v/1024:.1f}".rstrip("0").rstrip(".")
        return s.replace(".", "{,}") + "\\,MB"
    s = f"{v:.1f}" if v < 10 else f"{v:.0f}"
    return s.replace(".", "{,}") + "\\,KB"


def fmt_lcs(v):
    return "---" if v in (None, "") else str(v)


def load(csv_path):
    rows = []
    with open(csv_path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "version": r["version"],
                "n": int(r["n"]),
                "time_ms": None if r["time_ms"] == "" else float(r["time_ms"]),
                "mem_kb":  None if r["mem_kb"] == ""  else float(r["mem_kb"]),
                "lcs":     None if r["lcs"] == ""     else r["lcs"],
                "status":  r.get("status", "ok"),
            })
    return rows


def by_version(rows, v):
    return sorted([r for r in rows if r["version"] == v], key=lambda r: r["n"])


def table_A(rows):
    out = [
        r"\begin{table}[h]", r"\centering", r"\small",
        r"\begin{tabular}{@{}rrrr@{}}", r"\toprule",
        r"$n$ & Tiempo CPU (mediana) & Memoria pico & LCS \\",
        r"\midrule",
    ]
    for r in by_version(rows, "A"):
        t = "\\textit{timeout}" if r["status"] == "timeout" else fmt_time(r["time_ms"])
        m = fmt_mem(r["mem_kb"])
        l = fmt_lcs(r["lcs"])
        out.append(f"{r['n']:<4} & {t:<20} & {m:<10} & {l} \\\\")
    out += [r"\bottomrule", r"\end{tabular}",
            r"\caption{Version A.}\label{tab:A}", r"\end{table}"]
    return "\n".join(out)


def table_BC(rows):
    b = {r["n"]: r for r in by_version(rows, "B")}
    c = {r["n"]: r for r in by_version(rows, "C")}
    ns = sorted(set(b) | set(c))
    out = [
        r"\begin{table}[h]", r"\centering", r"\small",
        r"\begin{tabular}{@{}rrrrrr@{}}", r"\toprule",
        r"& \multicolumn{2}{c}{\textbf{B - Hirschberg}} "
        r"& \multicolumn{2}{c}{\textbf{C - DP tabular}} & \\",
        r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}",
        r"$n$ & tiempo (ms) & memoria & tiempo (ms) & memoria & LCS\\",
        r"\midrule",
    ]
    for n in ns:
        rb, rc = b.get(n, {}), c.get(n, {})
        out.append(
            f"{n:<5} & {fmt_time(rb.get('time_ms')):<10} & "
            f"{fmt_mem(rb.get('mem_kb')):<9} & "
            f"{fmt_time(rc.get('time_ms')):<10} & "
            f"{fmt_mem(rc.get('mem_kb')):<9} & "
            f"{fmt_lcs(rb.get('lcs') or rc.get('lcs'))} \\\\"
        )
    out += [r"\bottomrule", r"\end{tabular}",
            r"\caption{Versiones B y C.}\label{tab:BC}", r"\end{table}"]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="results/resultados.csv")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rows = load(Path(args.csv))
    text = ("% === Tabla 2 ===\n" + table_A(rows)
            + "\n\n% === Tabla 3 ===\n" + table_BC(rows) + "\n")
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Tablas escritas en {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
