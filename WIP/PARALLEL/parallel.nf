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

// This queue will define maximum depth of the processing tree
alignRetention_queue
    .collectFile()  // Get file, will wait for process to finish
    .map { it.text }  // Convert file to text
    .splitText()  // Split text, each line in a seperate loop
    .map { it -> it.tokenize('\t')[0] }  // Get first value, it contains the rounds
    .toInteger()  // Convert string to integer for max function
    .max()  // Maximum amount of rounds there is
    .subscribe { max_depth=it; println("Maximum depth = $max_depth") }  // Add maximum_depth as a variable

// This queue will create the file pairs
alignRetention_queue
    .collectFile()  // Get file, will wait for process to finish
    .map { it.text }  // Convert file to text
    .splitText()  // Split text, each line in a seperate loop
    // This is tricky. Split each line into a tuple, first which contains the rounds and the second with file pairs
    .map { it -> [it.tokenize('\t')[0].toInteger(), [file(it.tokenize('\t')[1]),
                                                     file(it.tokenize('\t')[2].replaceAll(/\n/, ''))]] }
    .groupTuple()  // Combines the rounds into a nested tuple, aka all round 1 are in a tuple of tuples
    .transpose()  // transpose the order, so it will be round 0 first, then round 1 in the correct queue
    .into { processing_tree; processing_tree_copy }  // Add queue to channel

// This queue will create the tree
alignRetention_queue
  .collectFile()  // Get file, will wait for process to finish
  .map { it.text }  // Convert file to text
  .splitText()  // Split text, each line in a seperate loop
  .map { it -> it.tokenize('\t')[0].toInteger() }  // Get first value, it contains the rounds. Convert to int!
  .countBy()  // Count depths and put into a map. Will output ex [0:1, 1:1, 2:2, 3:4, 4:1, 5:3 ...] Depends on tree
  .view()  // view the map. Syntax: [round_nr:amount_of_parallel_files]. A map is kind of like a dict in python
  .subscribe{ end_depth = max_depth + 1; it[end_depth] = 1; tree_map=it }
// Note: all these channels run async, while tree queue needs max_depth from first queue. Check if this can cause errors

tree_map = [0:1]  // Need to initialize treemap, since input_ch will start when the nf script is started. It will then wait
condition = { it == max_depth++ }  // Stop when reaching max_depth. Defined in channel above
feedback_ch = Channel.create()  // This channel loop until max_depth has been reached

/* Okay, this one is tricky and needs an explanation
The problem was that I need to create a processing tree. Any amount of files in each round can be processed in parallel,
but we need to wait for all the previous processes to finish before we do the next batch of files. The files from previous rounds
needs to be accessible to the next rounds.
The solution is to create a feedback loop, so the process will loop until the file queue is empty (until command). However, since all processes
run async and will each input a value into the feedback channel, it will spawn the exact amount of processes which were started from
the beginning. I solved the issue by creating a tree map, which countains all the rounds and how many processes it can run in parallel.
Each process will submit a value, which is the next round that should be processed. The unique command takes the list and outputs only 1
value (important). This is then piped to a function that creates list that is flattened, spawning the exact amount of processes needed before
the next batch
*/
// IT FUCKING WORKS, WHOAA!!!!!!!! SO MANY GODDAMNED HOURS
input_ch = Channel.from(0).mix( feedback_ch.until(condition).unique() ).flatMap { n -> 0..<tree_map[n] }

process parallel {
  input:
    set val(depth), val(filepair) from processing_tree
    val feedback_val from input_ch
  output:
    val depth into feedback_ch
  exec:
    depth++
  script:
  """
  echo "DEPTH ${depth - 1}"
  echo "FILES ${filepair[0]} and ${filepair[1]}"
  #mkdir -p pair/file1; mkdir pair/file2
  #ln -s ${filepair[0]} pair/file1/; ln -s ${filepair[1]} pair/file2/; 
  sleep 2
	"""
}
