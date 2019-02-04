#!/usr/bin/env nextflow

echo true

params.mzML = "example_data/small.RAW"
mzML = file(params.mzML)

process msconvert {
  publishDir "./converted", mode: 'copy', overwrite: true, pattern: "*"
  input:
	file f from mzML
  output:
  file("*mz5") into converted_files
  script:
	"""
  wine msconvert ${f} --mz5
  """
}
