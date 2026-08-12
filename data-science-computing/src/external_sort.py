#!/usr/bin/env python3
"""Memory-bounded external merge sort adapted from graduate coursework."""

from __future__ import annotations

import argparse
import heapq
import random
import tempfile
from pathlib import Path
from typing import Iterable, Iterator


def write_random_integers(path: Path, count: int, seed: int = 1977) -> None:
    rng = random.Random(seed)
    with path.open("w", encoding="utf-8") as stream:
        for _ in range(count):
            stream.write(f"{rng.randint(0, count * 2)}\n")


def read_integers(path: Path) -> Iterator[int]:
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            value = line.strip()
            if value:
                yield int(value)


def write_chunk(values: list[int], directory: Path, index: int) -> Path:
    values.sort()
    chunk_path = directory / f"chunk-{index:04d}.txt"
    with chunk_path.open("w", encoding="utf-8") as stream:
        stream.writelines(f"{value}\n" for value in values)
    return chunk_path


def create_sorted_chunks(input_path: Path, directory: Path, chunk_size: int) -> list[Path]:
    chunks: list[Path] = []
    values: list[int] = []
    for value in read_integers(input_path):
        values.append(value)
        if len(values) == chunk_size:
            chunks.append(write_chunk(values, directory, len(chunks)))
            values = []
    if values:
        chunks.append(write_chunk(values, directory, len(chunks)))
    return chunks


def merge_chunks(chunks: Iterable[Path], output_path: Path) -> None:
    iterators = [read_integers(path) for path in chunks]
    with output_path.open("w", encoding="utf-8") as output:
        output.writelines(f"{value}\n" for value in heapq.merge(*iterators))


def is_sorted(path: Path) -> bool:
    iterator = read_integers(path)
    try:
        previous = next(iterator)
    except StopIteration:
        return True
    for value in iterator:
        if value < previous:
            return False
        previous = value
    return True


def external_sort(input_path: Path, output_path: Path, chunk_size: int) -> None:
    with tempfile.TemporaryDirectory(prefix="external-sort-") as temporary:
        chunks = create_sorted_chunks(input_path, Path(temporary), chunk_size)
        merge_chunks(chunks, output_path)
    if not is_sorted(output_path):
        raise RuntimeError("Output verification failed: values are not sorted")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100_000)
    parser.add_argument("--chunk-size", type=int, default=10_000)
    parser.add_argument("--input", type=Path, default=Path("input-integers.txt"))
    parser.add_argument("--output", type=Path, default=Path("sorted-integers.txt"))
    parser.add_argument("--seed", type=int, default=1977)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.count < 0 or args.chunk_size <= 0:
        raise ValueError("count must be non-negative and chunk-size must be positive")
    write_random_integers(args.input, args.count, args.seed)
    external_sort(args.input, args.output, args.chunk_size)
    print(f"Sorted {args.count:,} integers into {args.output}")


if __name__ == "__main__":
    main()
