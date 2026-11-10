"""Pruebas de correctitud de las tres versiones.

Para cada caso se comprueba que la cadena devuelta:
  1. es subsecuencia de ambas entradas, y
  2. tiene la longitud optima, calculada con una DP de referencia.
"""
import random

from lcs import lcs_recursiva, lcs_hirschberg, lcs_dp


def _reference_len(a: str, b: str) -> int:
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def es_subsecuencia(s: str, t: str) -> bool:
    it = iter(t)
    return all(c in it for c in s)


def run(trials: int = 300) -> None:
    rng = random.Random(0)
    cases = [("", ""), ("A", ""), ("", "A"), ("A", "A"), ("AB", "BA"),
             ("ACGT", "ACGT"), ("AAAA", "CCCC"), ("ABCBDAB", "BDCABA")]
    for _ in range(trials):
        a = "".join(rng.choice("ACGT") for _ in range(rng.randint(0, 12)))
        b = "".join(rng.choice("ACGT") for _ in range(rng.randint(0, 12)))
        cases.append((a, b))
    # algunos casos mayores solo para B y C
    big = []
    for n in (100, 300):
        a = "".join(rng.choice("ACGT") for _ in range(n))
        b = "".join(rng.choice("ACGT") for _ in range(n))
        big.append((a, b))

    versiones = [("A", lcs_recursiva), ("B", lcs_hirschberg), ("C", lcs_dp)]
    total = 0
    for a, b in cases + big:
        expected = _reference_len(a, b)
        for name, fn in versiones:
            if name == "A" and (a, b) in big:
                continue
            got = fn(a, b)
            assert len(got) == expected, (
                f"Version {name}: {a!r} {b!r} -> longitud {len(got)} != {expected}"
            )
            assert es_subsecuencia(got, a) and es_subsecuencia(got, b), (
                f"Version {name}: {got!r} no es subsecuencia comun de {a!r} y {b!r}"
            )
            total += 1
    print(f"OK: {len(cases)} casos en las 3 versiones y {len(big)} casos "
          f"grandes en B y C ({total} comprobaciones).")


if __name__ == "__main__":
    run()
