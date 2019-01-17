#!/usr/bin/env nextflow
echo true

params.file_def = "test.txt"
params.out_dir = "Output"

process test {
  publishDir params.out_dir
  input:
	file 'test.txt' from params.file_def
  output:
	file 'test_dir/test.txt'
  script:
	"""
	echo "Started"
	cat test.txt
	mkdir test_dir
	touch test_dir/test.txt
	"""
}

