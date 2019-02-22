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
    .map { it -> it.tokenize('\t')[0] }  // Get first value, it contains the rounds
    .toInteger()  // String to integer
    .max()  // Maximum amount of rounds
    .subscribe { max_depth=it }

condition = { it >= max_depth + 10 }  // max_depth is not defined until previous queue has been gone through
feedback_ch = Channel.create()
input_ch = Channel.from(0).mix( feedback_ch.until(condition) )

process parallel {
  publishDir "files/", mode: 'copy', overwrite: true, pattern: "*.txt"
  input:
    file "alignRetention_queue.txt" from alignRetention_queue  // Will wait for previous process to finish
    file("*") from file_input_ch
    file("*") from Channel.fromPath('files/*').collect()
    val depth from input_ch
  output:
    val depth into feedback_ch
    file("*") into file_feedback_ch
  script:
  depth = depth + 1
	"""
  ls
  echo ${depth}
  touch ${depth}_1.txt
  touch ${depth}_2.txt
  touch ${depth}_3.txt
  sleep 1
  echo DONE
  find . -exec touch {} \\;
	"""
}


/*
params.input = 'hello.txt'

condition = { it.readLines().size()>3 }
feedback_ch = Channel.create()
input_ch = Channel.fromPath(params.input).mix( feedback_ch.until(condition) )

process foo {
    input:
    file x from input_ch
    output:
    file 'foo.txt' into foo_ch
    script:
    """
    cat $x > foo.txt
    """
}

process bar {
    input:
    file x from foo_ch
    output:
    file 'bar.txt' into feedback_ch
    file 'bar.txt' into result_ch
    script:
    """
    cat $x > bar.txt
    echo World >> bar.txt
    """
}

result_ch.last().println { "Result:\n${it.text.indent(' ')}" }
*/
