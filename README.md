# nextflow-omics-qc

A small, reproducible Nextflow DSL2 workflow for paired-end FASTQ quality control.

## What it does

The workflow:

1. Reads a CSV samplesheet.
2. Runs streaming QC on each paired-end FASTQ sample.
3. Computes read count, mean read length, GC%, N%, and Q30%.
4. Aggregates sample-level metrics into CSV and JSON summaries.

The Python implementation is deliberately lightweight and dependency-minimal. Runtime dependencies are provided through a Python container.

## Run

Requirements: Nextflow and Docker.

```bash
nextflow run main.nf \
  --samplesheet assets/samplesheet.csv \
  --outdir results \
  -profile docker
```

For the included test data:
```bash
nextflow run main.nf -profile test
```

## Input format
```csv
sample_id,fastq_1,fastq_2
SAMPLE_A,data/SAMPLE_A_R1.fastq.gz,data/SAMPLE_A_R2.fastq.gz
```
## Reproducibility

The workflow separates orchestration from analysis code, uses a containerized runtime, exposes parameters through Nextflow, and includes a GitHub Actions test that executes the pipeline on every push and pull request.

## Design choices

The analysis step is streaming so that QC metrics can be computed without loading an entire FASTQ file into memory. The repository is intentionally small, but the workflow structure is designed to be extended with established QC tools and downstream modules.

## Scope

This repository is a compact engineering example rather than a replacement for established production QC tools. In a production setting, I would benchmark the metrics against trusted tools, add richer validation and test coverage, and integrate the workflow with institutional/HPC or cloud execution profiles.
