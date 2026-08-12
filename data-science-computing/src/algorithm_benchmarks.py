#!/usr/bin/env python3
"""Benchmark insertion sort and two-wall quicksort on reproducible inputs."""

from __future__ import annotations

import argparse
import random
import statistics
import time
from pathlib import Path
from typing import Callable


def insertion_sort(values: list[int]) -> None:
    for i in range(1, len(values)):
        key = values[i]
        j = i - 1
        while j >= 0 and values[j] > key:
            values[j + 1] = values[j]
            j -= 1
        values[j + 1] = key


def quicksort(values: list[int], start: int = 0, end: int | None = None) -> None:
    end = len(values) if end is None else end
    if end - start <= 1:
        return
    pivot_index = partition(values, start, end)
    quicksort(values, start, pivot_index)
    quicksort(values, pivot_index + 1, end)


def partition(values: list[int], start: int, end: int) -> int:
    pivot = values[start]
    left, right = start + 1, end - 1
    while True:
        while left <= right and values[left] <= pivot:
            left += 1
        while left <= right and values[right] >= pivot:
            right -= 1
        if left > right:
            values[start], values[right] = values[right], values[start]
            return right
        values[left], values[right] = values[right], values[left]


def benchmark(algorithm: Callable[[list[int]], None], base: list[int], repeats: int) -> float:
    samples = []
    for _ in range(repeats):
        values = base.copy()
        start = time.perf_counter()
        algorithm(values)
        samples.append(time.perf_counter() - start)
        if values != sorted(base):
            raise RuntimeError(f"{algorithm.__name__} returned an invalid result")
    return statistics.mean(samples)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-size", type=int, default=1_000)
    parser.add_argument("--step", type=int, default=100)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=1977)
    parser.add_argument("--plot", type=Path, default=Path("sorting-benchmark.png"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.max_size < args.step or args.step <= 0 or args.repeats <= 0:
        raise ValueError("Use positive values with max-size greater than or equal to step")
    rng = random.Random(args.seed)
    rows = []
    for size in range(args.step, args.max_size + 1, args.step):
        base = [rng.randint(0, 10_000) for _ in range(size)]
        rows.append((size, benchmark(insertion_sort, base, args.repeats), benchmark(quicksort, base, args.repeats)))
    print("size,insertion_seconds,quicksort_seconds")
    for row in rows:
        print(f"{row[0]},{row[1]:.8f},{row[2]:.8f}")

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib is not installed; timing table generated without a plot.")
        return
    plt.plot([r[0] for r in rows], [r[1] for r in rows], marker="o", label="Insertion sort")
    plt.plot([r[0] for r in rows], [r[2] for r in rows], marker="o", label="Quicksort")
    plt.xlabel("Array length")
    plt.ylabel("Mean runtime (seconds)")
    plt.title("Sorting algorithm benchmark")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.plot, dpi=160)
    print(f"Saved plot to {args.plot}")


if __name__ == "__main__":
    main()
