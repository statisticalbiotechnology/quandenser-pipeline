#!/usr/bin/env nextflow
echo true

process queue {
  input:
    file "alignRetention_queue.txt" from file("test/alignRetention_queue.txt")
  output:
    file "*.txt" into alignRetention_queue includeInputs true
  script:
	"""
  touch alignRetention_queue.txt
	"""
}
total_spectras = 9

alignRetention_queue
    .collectFile()  // Get file, will wait for process to finish
    .map { it.text }  // Convert file to text
    .splitText()  // Split text, each line in a seperate loop
    .map { it -> it.tokenize('\t')[0] }  // Get first value, it contains the rounds
    .toInteger()  // Convert string to integer for max function
    .max()  // Maximum amount of rounds there is
    .subscribe { max_depth=it; }  // Add maximum_depth as a variable
    .map{ it -> 0 }
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

tree_map_reconstructed = [0:1]  // Initialize first value
processed_files = [0]
process sync_variables {
  exectutor = 'local'
  input:
    val alignRetention_file from alignRetention_queue  // Bug: Needs to be val
    val wait1 from wait_queue_1
    val wait2 from wait_queue_2
  output:
    val initial_range into sync_ch
  exec:
    current_depth = 0
    current_width = 0
    prev_files = []
    all_lines = alignRetention_file.toAbsolutePath().readLines()
    println("$alignRetention_file")
    for( line in all_lines ){
      file1 = line.tokenize('\t')[1].tokenize('/')[-1]
      file2 = line.tokenize('\t')[2].tokenize('/')[-1]
      if (prev_files.contains(file1) || prev_files.contains(file2) ) {
         tree_map_reconstructed[current_depth] = current_width
         println("WARNING!!! $file1 and $file2 in $prev_files")
         current_depth++
         current_width = 1
         prev_files.clear()
      } else {
        current_width++
        println("File1: $file1, File2: $file2")
      }
      prev_files << file1
      prev_files << file2
     }
     tree_map_reconstructed[current_depth] = current_width
     println("Treemap is $tree_map")
     println("Reconstructed treemap is $tree_map_reconstructed")

     end_depth = current_depth + 1
     tree_map_reconstructed[end_depth] = 1
     tree_map_reconstructed[-1] = tree_map_reconstructed[0]  // Initializiation of first values
     initial_range = 0..<tree_map_reconstructed[0]
     processed_files[0] = -tree_map_reconstructed[0]

     connections = 2*(total_spectras-1)
     speed_increase = connections/(current_depth+1) * 100 - 100
     println("Total connections = $connections")
     println("Total rounds with parallel = ${current_depth + 1}")
     println("With the current tree, you will get a ${speed_increase.round(1)}% increase in speed with parallelization")
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
Each process will submit a value, which is the next round that should be processed. The buffer command will wait for all processes
to finish before starting the next batch.
This is then piped to a function that creates list that is flattened, spawning the exact amount of processes needed before the next batch.

Note: ..< is needed, because if the value is 1 in tree map, I don't want 2 values, only 1 value
*/
// IT FUCKING WORKS, WHOAA!!!!!!!! SO MANY GODDAMNED HOURS WENT INTO THIS
current_depth = -1
current_width = 0
input_ch = sync_ch  // Syncronization, aka wait until tree_map is defined
.flatten()
.mix( feedback_ch.until(condition) )  // Continously add
.map { processed_files[0]++ }
.map { it -> current_width++; }  // Add 1 to current width
.buffer { it >= tree_map_reconstructed[current_depth] - 1}  // When width is more than width at tree
.map { it -> current_depth++; current_width = 0; current_depth}  // Add 1 to depth, pass on current depth
.flatMap { n -> 0..<tree_map_reconstructed[n] }  // Convert number to a list same size as amount of parallel processes
.map { it -> processed_files[0]}

process parallel {
  publishDir "work/percolator", mode: 'symlink', overwrite: true,  pattern: "*"
  publishDir "Quandenser_output", mode: 'copy', overwrite: true,  pattern: "*"
  input:
    set val(depth), val(filepair) from processing_tree
    // This will replace percolator directory with a link to work directory percolator
    each prev_percolator from Channel.fromPath("work/percolator")

    // This is the magic that makes the process loop
    val feedback_val from input_ch
  output:
    val depth into feedback_ch
  exec:
    depth++
  script:
  """
  echo "DEPTH ${depth - 1}"
  echo "FEEDBACK VAL ${feedback_val}"
  sleep 1
	"""
}
