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


process sync_variables {
  exectutor = 'local'
  input:
    file alignRetention_file from alignRetention_queue
    val wait1 from wait_queue_1
    val wait2 from wait_queue_2
  exec:
   tree_map_reconstructed = [0:1]  // Initialize first value
   current_depth = 0
   current_width = 0
   prev_files = []
   all_lines = alignRetention_file.readLines()
   for( line in all_lines ){
     file1 = line.tokenize('\t')[1].tokenize('/')[-1]
     file2 = line.tokenize('\t')[2].tokenize('/')[-1]
     //println("File1: $file1, File2: $file2")
     if (prev_files.contains(file1) || prev_files.contains(file2) ) {
        tree_map_reconstructed[current_depth] = current_width
        //println("WARNING!!! $file1 and $file2 in $prev_files")
        current_depth++
        current_width = 1
        prev_files.clear()
     } else {
       current_width++
     }
     prev_files << file1
     prev_files << file2
   }
   tree_map_reconstructed[current_depth] = current_width
   println("Treemap is $tree_map")
   println("Reconstructed treemap is $tree_map_reconstructed")
   connections = 2*(total_spectras-1)
   speed_increase = connections/(current_depth+1) * 100 - 100
   println("Total connections = $connections")
   println("Total rounds with parallel = ${current_depth + 1}")
   println("With the current tree, you will get a ${speed_increase.round(1)}% increase in speed with parallelization")
}
