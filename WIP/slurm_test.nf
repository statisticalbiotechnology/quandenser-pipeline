#!/usr/bin/env nextflow
echo true

process test1 {
  cpus 1
  time '3s'
  output:
	file("test.txt") into test_file
  script:
	"""
  touch test.txt
  sleep 1
	"""
}

process test2 {
  cpus 1
  time '5s'
  input:
	file("test.txt") from test_file
  output:
  file("test.txt") into test_file_processed
  script:
	"""
  echo "This is a test" >> test.txt
  sleep 3
  """
}


process test3 {
  cpus 1
  time '7s'
  input:
	file("test.txt") from test_file_processed
  script:
	"""
  echo "I'm waiting 5 seconds"
  sleep 5
  cat test.txt
  echo "DONE"
  """
}
