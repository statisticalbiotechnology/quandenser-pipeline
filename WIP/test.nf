#!/usr/bin/env nextflow
echo true

params.file_def = "test.txt"

process test {
  input:
	file 'test.txt' from params.file_def
  output:
	file 'test_dir/test.txt'
  script:
	"""
	cat test.txt
	mkdir test_dir
	touch test_dir/test.txt
	"""
}

