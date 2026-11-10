"""Pruebas de correctitud de las tres versiones frente a una DP de referencia."""
import random

from lcs import lcs_recursiva, lcs_hirschberg, lcs_dp


def _reference(a: str, b: str) -> int:
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def run(trials: int = 300) -> None:
    rng = random.Random(0)
    cases = [("", ""), ("A", ""), ("", "A"), ("A", "A"), ("AB", "BA")]
    for _ in range(trials):
        a = "".join(rng.choice("ACGT") for _ in range(rng.randint(0, 12)))
        b = "".join(rng.choice("ACGT") for _ in range(rng.randint(0, 12)))
        cases.append((a, b))

    for a, b in cases:
        expected = _reference(a, b)
        for name, fn in [("A", lcs_recursiva),
                         ("B", lcs_hirschberg),
                         ("C", lcs_dp)]:
            got = fn(a, b)
            assert got == expected, (
                f"Version {name}: {a!r} {b!r} -> {got} != {expected}"
            )
    print(f"OK: {len(cases)} casos verificados en las 3 versiones.")


if __name__ == "__main__":
    run()
