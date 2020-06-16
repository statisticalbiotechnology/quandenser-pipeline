#!/usr/bin/env nextflow

params.str = 'Hello world!'

process createAlignment {
  input:
    file x from Channel.fromPath("featureAlignmentQueue.txt")
  output:
    file "featureAlignmentQueue2.txt" into feature_alignRetention_queue
  script:
    """
    cp ${x} "featureAlignmentQueue2.txt"
    """
}

// This queue will create the file pairs
feature_alignRetention_queue
    .collectFile()  // Get file, will wait for process to finish
    .map { it.text }  // Convert file to text
    .splitText()  // Split text by line
    .map { it -> [it.tokenize('\t')[0].toInteger(), [file(it.tokenize('\t')[1]),
                                                     file(it.tokenize('\t')[2])]] }
    .into { processing_tree; processing_tree_copy }

/*
All alignments in a round can be processed in parallel, but we need to wait 
for all the processes in the previous round to finish before starting the next.
For this, we create a tree object, which countains all the rounds and how 
many processes can run in parallel per round. We then create a feedback loop,
which runs until the alignment queue is empty. All processes in a round run 
async and will each input a value into the feedback channel. The buffer command 
waits for all processes in a round to finish before starting the next round. 
This is then piped to a function that spawns the exact amount of processes 
needed for the next round.
*/
class Tree {
  private int processed_alignments = -1; // set processed_alignments to be 0 after the dummy round
  private int processed_alignments_current_round = 0;
  private int current_round = -1; // Dummy round to get tree started
  private Map tree_map;
  public int num_rounds;
  
  int initialize(tree) {
    tree_map = tree.countBy { it }; // create map with number of alignments per round
    
    num_rounds = tree_map.size();
    tree_map[-1] = 0;  // Dummy round to get tree started
    tree_map[num_rounds] = 0;  // Dummy round at end of the tree, prevents nextRound() to fail after last round
    return 0;
  }
  
  int alignmentFinished() {
    processed_alignments++;
    return ++processed_alignments_current_round;
  }
  
  List nextRound() {
    current_round++;
    processed_alignments_current_round = 0;
    return [processed_alignments] * tree_map[current_round];
  }
  
  int currentRoundAlignments() {
    return tree_map[current_round];
  }
}

tree = new Tree()

feedback_ch = Channel.create()  // This channel loops until max_rounds has been reached

input_ch = processing_tree_copy
  .collect{ it[0] } // Collect alignment round indexes in a list
  .map{ it -> tree.initialize(it) }
  .mix( feedback_ch )
  .map { tree.alignmentFinished(); }  // Increment and return finished alignments
  .buffer { it >= tree.currentRoundAlignments() }  // Check if all alignments in this round are done
  .flatMap { tree.nextRound(); }

process quandenser_parallel_3 {
  errorStrategy 'retry'  // If actor cell does something stupid, this should retry it once on clusters when the time run out
  input:
    set val(depth), val(filepair) from processing_tree  // Get a filepair from a round

    // This is the magic that makes the process loop
    val feedback_val from input_ch
  output:
    val 0 into feedback_ch
    val depth into percolator_1_completed
  script:
    """
    echo "Hello ${depth} ${filepair} ${feedback_val}"; sleep 1;
    """
}

percolator_1_completed.view { it }
