#!/usr/bin/env nextflow
echo true

process queue {
  input:
    file "alignRetention_queue.txt" from file("alignRetention_queue.txt")
  output:
    file "alignRetention_queue.txt" into alignRetention_queue
  script:
	"""
  touch alignRetention_queue.txt
	"""
}

// This queue will define maximum depth
alignRetention_queue
    .collectFile()  // Get file, will wait for process to finish
    .map { it.text }  // Convert file to text
    .splitText()  // Split text, each line in a seperate loop
    .map { it -> [it.tokenize('\t')[0], [file(it.tokenize('\t')[1]), file(it.tokenize('\t')[2])]] }
    .groupTuple()
    //.println()
    .into { processing_groups; processing_groups_copy }


process process {
  input:
    set val(depth), set file('*'), file('*') from processing_groups
  script:
	"""
  ls
	"""
}

// https://groups.google.com/forum/#!topic/nextflow/eUWMzrEm0IY
// https://groups.google.com/forum/#!topic/nextflow/kmX5ueuhViE
