# Data science computing

Selected graduate coursework demonstrating algorithmic reasoning and computing foundations relevant to data pipelines and machine learning workloads.

## Topics represented

- asymptotic complexity and empirical benchmarking;
- insertion sort and quicksort;
- brute-force, memoized, and bottom-up dynamic programming;
- producer-consumer coordination and synchronization;
- threading versus multiprocessing;
- external sorting for data larger than memory;
- CPU/GPU vector-computation concepts.

## Portfolio-ready implementations

### `src/external_sort.py`

A portable, tested external merge-sort pipeline. It generates a large integer file, sorts bounded chunks, and merges them with a heap. Parameters replace the original machine-specific paths.

### `src/algorithm_benchmarks.py`

Reproducible comparison of insertion sort and quicksort across increasing input sizes, including a saved timing plot when Matplotlib is installed.

### `src/vector_add_opencl.py`

Parameter-driven CPU/NumPy/OpenCL comparison. OpenCL is optional and the script reports clearly when no compatible runtime is available.

## Original notebooks

- `notebooks/algorithm-analysis.ipynb`: submitted work on complexity, sorting, and knapsack strategies
- `notebooks/concurrency-experiments.ipynb`: submitted work on synchronization, threading, and runtime comparison

The original notebooks are retained as historical coursework. The scripts in `src/` are the recommended entry points because they are reorganized, portable, and easier to review.

## Run

```bash
python src/algorithm_benchmarks.py
python src/external_sort.py --count 100000 --chunk-size 10000
python src/vector_add_opencl.py --size 1000000
```

## Skills demonstrated

Python, performance measurement, complexity analysis, memory-aware processing, concurrency concepts, defensive interfaces, and reproducible command-line execution.
