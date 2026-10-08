nextflow.enable.dsl=2

params.samplesheet = "assets/samplesheet.csv"
params.outdir = "results"


process FASTQ_QC {

    tag "$sample_id"

    cpus 2
    memory "1 GB"

    container "python:3.12-slim"

    publishDir "${params.outdir}/per_sample", mode: "copy"

    input:
    tuple val(sample_id), path(read1), path(read2)

    output:
    path "${sample_id}.json", emit: qc_json

    script:
    """
    python ${projectDir}/bin/fastq_qc.py \
        --sample "${sample_id}" \
        --r1 "${read1}" \
        --r2 "${read2}" \
        --output "${sample_id}.json"
    """
}


process AGGREGATE_QC {

    tag "aggregate"

    cpus 1
    memory "512 MB"

    container "python:3.12-slim"

    publishDir "${params.outdir}/summary", mode: "copy"

    input:
    path qc_files

    output:
    path "qc_summary.csv"
    path "qc_summary.json"

    script:
    """
    python ${projectDir}/bin/aggregate_qc.py \
        --input-dir . \
        --output-csv qc_summary.csv \
        --output-json qc_summary.json
    """
}


workflow {

    samples = Channel
        .fromPath(
            params.samplesheet,
            checkIfExists: true
        )
        .splitCsv(header: true)
        .map { row ->

            if (!row.sample_id || !row.fastq_1 || !row.fastq_2) {
                error "Each row must contain sample_id, fastq_1 and fastq_2"
            }

            tuple(
                row.sample_id.toString(),
                file(
                    row.fastq_1.toString(),
                    checkIfExists: true
                ),
                file(
                    row.fastq_2.toString(),
                    checkIfExists: true
                )
            )
        }

    qc = FASTQ_QC(samples)

    AGGREGATE_QC(qc.qc_json.collect())
}