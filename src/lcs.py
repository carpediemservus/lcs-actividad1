"""Tres implementaciones de la Subsecuencia Comun Mas Larga (LCS).

Version A: recursion directa, sin memorizacion.
Version B: divide y venceras de Hirschberg (memoria lineal).
Version C: programacion dinamica tabular con reconstruccion.

Las tres devuelven la propia subsecuencia (una cadena); su longitud se
obtiene con len().
"""
import sys

sys.setrecursionlimit(10000)


# ---------- Version A: recursiva directa ----------
def lcs_recursiva(a: str, b: str) -> str:
    def rec(i: int, j: int) -> str:
        if i == 0 or j == 0:
            return ""
        if a[i - 1] == b[j - 1]:
            return rec(i - 1, j - 1) + a[i - 1]
        x = rec(i - 1, j)
        y = rec(i, j - 1)
        return x if len(x) >= len(y) else y

    return rec(len(a), len(b))


# ---------- Version B: Hirschberg ----------
def _last_row(a: str, b: str) -> list:
    """Ultima fila de la DP (longitudes LCS(a, b[:j])) en O(|b|) memoria."""
    n = len(b)
    prev = [0] * (n + 1)
    for ca in a:
        curr = [0] * (n + 1)
        for j in range(1, n + 1):
            if ca == b[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = prev[j] if prev[j] >= curr[j - 1] else curr[j - 1]
        prev = curr
    return prev


def lcs_hirschberg(a: str, b: str) -> str:
    if not a or not b:
        return ""
    if len(a) == 1:
        return a if a in b else ""

    mid = len(a) // 2
    l1 = _last_row(a[:mid], b)
    l2 = _last_row(a[mid:][::-1], b[::-1])[::-1]

    # punto de corte k que maximiza L1(k) + L2(k)
    k, best = 0, -1
    for j in range(len(b) + 1):
        s = l1[j] + l2[j]
        if s > best:
            best, k = s, j

    return lcs_hirschberg(a[:mid], b[:k]) + lcs_hirschberg(a[mid:], b[k:])


# ---------- Version C: DP tabular ----------
def lcs_dp(a: str, b: str) -> str:
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        ai = a[i - 1]
        row, prev = dp[i], dp[i - 1]
        for j in range(1, n + 1):
            if ai == b[j - 1]:
                row[j] = prev[j - 1] + 1
            else:
                row[j] = prev[j] if prev[j] >= row[j - 1] else row[j - 1]

    # reconstruccion: recorrido inverso desde dp[m][n]
    out = []
    i, j = m, n
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(out))
