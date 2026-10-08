#!/usr/bin/env python3
"""Aggregate per-sample QC JSON files into CSV and JSON summaries."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "sample_id",
    "paired_reads",
    "r1_mean_read_length",
    "r2_mean_read_length",
    "r1_gc_percent",
    "r2_gc_percent",
    "r1_n_percent",
    "r2_n_percent",
    "r1_q30_percent",
    "r2_q30_percent",
]


def flatten(record: dict) -> dict:
    """Convert nested QC output into one tabular row."""
    return {
        "sample_id": record["sample_id"],
        "paired_reads": record["paired_reads"],
        "r1_mean_read_length": record["read1"]["mean_read_length"],
        "r2_mean_read_length": record["read2"]["mean_read_length"],
        "r1_gc_percent": record["read1"]["gc_percent"],
        "r2_gc_percent": record["read2"]["gc_percent"],
        "r1_n_percent": record["read1"]["n_percent"],
        "r2_n_percent": record["read2"]["n_percent"],
        "r1_q30_percent": record["read1"]["q30_percent"],
        "r2_q30_percent": record["read2"]["q30_percent"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)

    args = parser.parse_args()

    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(args.input_dir.glob("*.json"))
    ]

    rows = [flatten(record) for record in records]

    with args.output_csv.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    args.output_json.write_text(
        json.dumps(rows, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
