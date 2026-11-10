# Actividad 1 — Subsecuencia Común Más Larga (LCS)

Tres implementaciones que calculan la LCS de dos cadenas (devuelven la subsecuencia, no solo su longitud), con su comparación experimental de tiempo de CPU y memoria:

- **Versión A**: recursión directa, sin memorización.
- **Versión B**: divide y vencerás de Hirschberg (memoria lineal).
- **Versión C**: programación dinámica tabular.

El informe completo está en `informe/informe.pdf` (fuente en `informe/informe.tex`).

## Requisitos

- Python 3.9 o superior (sin dependencias para las pruebas ni para las mediciones).
- `make`.
- Opcional: `matplotlib` para regenerar las gráficas (`pip install matplotlib`).

## Uso

```bash
make test      # comprueba que cada resultado es subsecuencia común y de longitud óptima
make run       # ejecuta los benchmarks: CSV, gráficas y datos en results/
make analyze   # genera results/tablas.tex con las Tablas 2 y 3 del informe
make clean     # elimina los resultados generados
```

`make run` tarda unos 2–3 minutos. De ese tiempo, 120 s corresponden a los dos puntos de la Versión A que superan el timeout de 60 s (n = 18 y n = 20).

## Estructura

```
.
|-- Makefile
|-- src/
|   |-- lcs.py          # implementaciones A, B y C
|   |-- benchmark.py    # experimentos, CSV y gráficas
|   |-- test_lcs.py     # pruebas de correctitud
|   `-- analyze.py      # tablas LaTeX a partir del CSV
|-- results/            # resultados de referencia incluidos en el informe
|   `-- datos/          # parejas X, Y y LCS de cada n
`-- informe/
    |-- informe.tex
    `-- informe.pdf
```

## Datos

Las cadenas se generan sobre el alfabeto {A, C, G, T} con semilla fija 42, así que cada ejecución reproduce exactamente los mismos pares y las mismas longitudes de LCS. Las parejas usadas y la LCS obtenida están en `results/datos/`. Los tiempos absolutos dependen del equipo.
