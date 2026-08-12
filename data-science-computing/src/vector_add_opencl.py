#!/usr/bin/env python3
"""Compare Python, NumPy, and optional OpenCL vector addition."""

from __future__ import annotations

import argparse
import time

import numpy as np


KERNEL = """
__kernel void vector_add(
    __global const float *a,
    __global const float *b,
    __global float *result)
{
    int i = get_global_id(0);
    result[i] = a[i] + b[i];
}
"""


def timed_python(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, float]:
    start = time.perf_counter()
    result = np.asarray([float(x + y) for x, y in zip(a, b)], dtype=np.float32)
    return result, time.perf_counter() - start


def timed_numpy(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, float]:
    start = time.perf_counter()
    result = a + b
    return result, time.perf_counter() - start


def timed_opencl(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, float, str]:
    import pyopencl as cl

    context = cl.create_some_context(interactive=False)
    queue = cl.CommandQueue(context)
    flags = cl.mem_flags
    a_buffer = cl.Buffer(context, flags.READ_ONLY | flags.COPY_HOST_PTR, hostbuf=a)
    b_buffer = cl.Buffer(context, flags.READ_ONLY | flags.COPY_HOST_PTR, hostbuf=b)
    result_buffer = cl.Buffer(context, flags.WRITE_ONLY, a.nbytes)
    program = cl.Program(context, KERNEL).build()
    result = np.empty_like(a)

    start = time.perf_counter()
    program.vector_add(queue, a.shape, None, a_buffer, b_buffer, result_buffer)
    cl.enqueue_copy(queue, result, result_buffer).wait()
    elapsed = time.perf_counter() - start
    return result, elapsed, context.devices[0].name


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=1_000_000)
    parser.add_argument("--seed", type=int, default=1977)
    args = parser.parse_args()
    if args.size <= 0:
        raise ValueError("size must be positive")

    rng = np.random.default_rng(args.seed)
    a = rng.random(args.size, dtype=np.float32)
    b = rng.random(args.size, dtype=np.float32)
    python_result, python_seconds = timed_python(a, b)
    numpy_result, numpy_seconds = timed_numpy(a, b)
    np.testing.assert_allclose(python_result, numpy_result, rtol=1e-6)
    print(f"Python loop: {python_seconds:.6f} seconds")
    print(f"NumPy:       {numpy_seconds:.6f} seconds")

    try:
        opencl_result, opencl_seconds, device = timed_opencl(a, b)
    except (ImportError, RuntimeError) as exc:
        print(f"OpenCL unavailable: {exc}")
        return
    np.testing.assert_allclose(opencl_result, numpy_result, rtol=1e-6)
    print(f"OpenCL:      {opencl_seconds:.6f} seconds ({device})")


if __name__ == "__main__":
    main()
