#!/usr/bin/env python3
"""
Streaming FASTQ quality-control metrics.

Works with FASTQ or FASTQ.GZ and reports read count, mean read length,
GC content, N content, and Q30 base percentage.
"""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from typing import Iterator, TextIO


def open_text(path: Path) -> TextIO:
    """Open plain-text or gzipped FASTQ as text."""
    if path.suffix == ".gz":
        return gzip.open(path, "rt")  # type: ignore[return-value]
    return path.open("r")


def fastq_records(path: Path) -> Iterator[tuple[str, str, str]]:
    """Yield (header, sequence, quality) records from a FASTQ file."""
    with open_text(path) as handle:
        while True:
            header = handle.readline()
            if not header:
                break

            sequence = handle.readline().rstrip("\n")
            plus = handle.readline().rstrip("\n")
            quality = handle.readline().rstrip("\n")

            if not sequence or not plus or not quality:
                raise ValueError(f"Incomplete FASTQ record in {path}")

            if not header.startswith("@"):
                raise ValueError(
                    f"Invalid FASTQ header in {path}: {header.strip()}"
                )

            if not plus.startswith("+"):
                raise ValueError(f"Invalid FASTQ separator in {path}")

            if len(sequence) != len(quality):
                raise ValueError(
                    f"Sequence/quality length mismatch in {path}: "
                    f"{len(sequence)} vs {len(quality)}"
                )

            yield header.rstrip("\n"), sequence, quality


def summarize(path: Path) -> dict:
    """Calculate streaming QC metrics for one FASTQ file."""
    reads = 0
    bases = 0
    gc_bases = 0
    n_bases = 0
    q30_bases = 0

    for _, sequence, quality in fastq_records(path):
        reads += 1
        bases += len(sequence)

        gc_bases += sum(
            base in {"G", "C", "g", "c"} for base in sequence
        )

        n_bases += sum(
            base in {"N", "n"} for base in sequence
        )

        q30_bases += sum(
            (ord(char) - 33) >= 30 for char in quality
        )

    return {
        "file": path.name,
        "reads": reads,
        "total_bases": bases,
        "mean_read_length": (
            round(bases / reads, 2) if reads else 0
        ),
        "gc_percent": (
            round(100 * gc_bases / bases, 2) if bases else 0
        ),
        "n_percent": (
            round(100 * n_bases / bases, 2) if bases else 0
        ),
        "q30_percent": (
            round(100 * q30_bases / bases, 2) if bases else 0
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--sample", required=True)
    parser.add_argument("--r1", type=Path, required=True)
    parser.add_argument("--r2", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()

    result = {
        "sample_id": args.sample,
        "read1": summarize(args.r1),
        "read2": summarize(args.r2),
    }

    result["paired_reads"] = min(
        result["read1"]["reads"],
        result["read2"]["reads"],
    )

    args.output.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
