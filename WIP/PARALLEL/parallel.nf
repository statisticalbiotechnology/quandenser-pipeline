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
  sleep 2
	"""
}

process test {
  input:
    file "alignRetention_queue.txt" from file("alignRetention_queue.txt")
  output:
    file "*.txt" into test_queue
  script:
	"""
  touch test.txt
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
    .map { it -> 0 }  // Depth has now been defined, add 0 to queue to initialize sync
    .into { wait_queue_1; wait_queue_1_copy }

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
  .subscribe{ tree_map=it; }
  .map { it -> 0 }  // Tree map has now been defined, add 0 to queue to initialize tree_map channel
  .into { wait_queue_2; wait_queue_2_copy }
// Note: all these channels run async, while tree queue needs max_depth from first queue. Check if this can cause errors

process sync_variables {
  exectutor = 'local'
  input:
    val wait1 from wait_queue_1
    val wait2 from wait_queue_2
  output:
    val 0 into sync_ch
  exec:
  end_depth = max_depth + 1
  tree_map[end_depth] = 1
}

condition = { 1 == 0 }  // Stop when reaching max_depth. Defined in channel above
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
the next batch.

Note: ..< is needed, because I if the value is 1, I don't want 2 values, only 1
*/
// IT FUCKING WORKS, WHOAA!!!!!!!! SO MANY GODDAMNED HOURS WENT INTO THIS
input_ch = sync_ch  // Syncronization, aka wait until tree_map is defined
.mix( feedback_ch.until(condition).unique() )  // Continously add
.flatMap { n -> 0..<tree_map[n] }  // Convert number to parallel processes

percolator_workdir = file("work/percolator")  // Path to working percolator directory
result = percolator_workdir.mkdir()  // Create the directory
process parallel {
  publishDir "work/percolator", mode: 'symlink', overwrite: true,  pattern: "*"
  publishDir "Quandenser_output", mode: 'copy', overwrite: true,  pattern: "*"
  input:
    set val(depth), val(filepair) from processing_tree
    // This will replace percolator directory with a link to work directory percolator
    each prev_percolator from Channel.fromPath("work/percolator")

    // Access previous files from quandenser. Consider maracluster files as links, takes time to publish
    //each prev_dinosaur from Channel.fromPath("Quandenser_output/dinosaur")  // Published long before, should not be a problem
    //each prev_maracluster from Channel.fromPath("Quandenser_output/maracluster")  // Async + publish time might make this problematic
    file ("*.txt") from test_queue.collect()

    // This is the magic that makes the process loop
    val feedback_val from input_ch
  output:
    val depth into feedback_ch
    // Just dump the files. This will need rework, since the percolator files are directly written directly to workdir.
    // Perhaps remove output files completely
    file("*.txt") into file_completed
  exec:
    depth++
  script:
  """
  echo "DEPTH ${depth - 1}"
  echo "FILES ${filepair[0]} and ${filepair[1]}"
  mkdir -p pair/file1; mkdir pair/file2
  ln -s ${filepair[0]} pair/file1/; ln -s ${filepair[1]} pair/file2/;
  mkdir Quandenser_output
  ln -s ${prev_percolator} Quandenser_output/percolator
  touch ${depth}.txt
  #tree
  #cd Quandenser_output/percolator
  #ls
  sleep 2
	"""
}
