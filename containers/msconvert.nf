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
  export WINEARCH="win32"  # Set wine to handle 32 bit
  export WINEPREFIX=/.wine  # Get a clean prefix
  #wine regsvr32 /pwiz/*.dll
  wine /pwiz/msconvert.exe ${f} --mz5
  """
}
