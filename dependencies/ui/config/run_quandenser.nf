#!/usr/bin/env nextflow
echo true
println(params)
// Since we can add labels to the directories, the output path of the files are
// different compared to work
publish_output_path = params.output_path + params.output_label

// Check if resume folder has been set
resume_directory = file("NULL")
if (params.resume_directory != "") {
  resume_directory = file(params.resume_directory)
  println("Resuming from directory: ${resume_directory}")
}

file_def = file(params.batch_file)  // batch_file
file_def.copyTo("$publish_output_path/file_list.txt")

Channel  // non-mzML files with proper labeling which will be converted
    .from(file_def.readLines())
    .map { it -> it.tokenize('\t') }
    .filter { it.size() > 1 }  // filters any input that is not <path> <X>
    .map { it -> file(it[0]) }  // Will index correcly, skips empty rows
    .set{ file_list }

if (params.workflow == "MSconvert") {  
  spectra_in = Channel.from(1)  // This prevents name collision crash
  file_list.set { spectra_convert }
} else {
  file_list.into { file_list_mzML; file_list_non_mzML }
  
  // Preprocessing file_list
  file_list_mzML
    .filter { it.getExtension() == "mzML" }  // filters any input that is not .mzML
    .set { spectra_in }  // Puts the files into spectra_in  
  
  file_list_non_mzML  // non-mzML files with proper labeling which will be converted
    .filter{ it.getExtension() != "mzML" }  // filters any input that is .mzML
    .set { spectra_convert }
}

// Replaces the lines of non-mzML with their corresponding converted mzML counterpart
count = 0
amount_of_non_mzML = 0
all_lines = file_def.readLines()
for( line in all_lines ){
  file_path = line.tokenize('\t')[0]
  file_label = line.tokenize('\t')[-1]
  file_name = (file_path.tokenize('/')[-1]).tokenize('.')[0]  // Split '/', take last. Split '.', take first
  file_extension = file_path.tokenize('.')[-1]
  if ( params.boxcar_convert == true ) {
    all_lines[count] = params.output_path + "/work/boxcar_converted_${params.random_hash}/mzML/boxcar_converted/" + file_name + ".mzML" + '\t' + file_label
  } else if ( file_extension != "mzML" ) {
    // Note: if you are running only msconvert on mzML files, the path will be wrong. However, since msconvert+quandenser
    // is not integrated yet, I can let it slide
    all_lines[count] = params.output_path + "/work/converted_${params.random_hash}/converted/" + file_name + ".mzML" + '\t' + file_label
    amount_of_non_mzML++
  } else {
    // add as is, no change
  }
  count++
}

// Create new batch file to use in work directory. Add the "corrected" raw to mzML paths here
file_def = file("$params.output_path/work/file_list_${params.random_hash}.txt")
file_def.text = ""  // Clear file, if it exists
for( line in all_lines ){
  file_def << line + '\n'  // need to add \n
}

println("Total files = " + count)
//println("Files that will be converted = " + amount_of_non_mzML)

// change the path to where the database is and the batch file is if you are only doing msconvert
if( params.workflow == "MSconvert" || params.workflow == "Quandenser" ) {
  db_file = params.batch_file  // Will not be used, so junk name
} else {
  db_file = params.db
}
db = file(db_file)  // Sets "db" as the file defined above
seq_index_name = "${db.getName()}.index"  // appends "index" to the db filename

file_params = file("$publish_output_path/params.txt")
file_params << "$params" + '\n'  // need to add \n

spectra_convert_channel = spectra_convert  // No collect = parallel processing, one file in each process
//spectra_convert_channel = spectra_convert  // Collect = everything is run in one process BETTER WITH PARALLEL, DEFAULT

process msconvert {
  /* Note: quandenser needs the file_list with paths to the files.
  Problem: We do not know the mzML file location during work and writing large files to publishDir is slow,
  so there might be a possibility that some strange issues with incomplete mzML files being inputted to quandenser.
  The solution is to have two publishdirs, one where the true files are being inserted for future use,
  while we point in the file_list to the files in the work directory with symlinks.
  The symlinks are fast to write + they point to complete files + we know the symlinks location --> fixed :)
  */
  errorStrategy 'retry'  // If wine crashes for some reason, try again once
  publishDir "$params.output_path/work/converted_${params.random_hash}", mode: 'symlink', overwrite: true, pattern: "converted/*"
  maxForks params.parallel_msconvert_max_forks  // Defaults to infinite
  if( params.publish_msconvert == true ){
    publishDir "$publish_output_path", mode: 'copy', overwrite: true, pattern: "converted/*"
  }
  containerOptions "$params.custom_mounts"
  maxForks params.parallel_msconvert_max_forks
  input:
    file(f) from spectra_convert_channel
  output:
    file("converted/*") into spectra_converted
  script:
  """
  mkdir -p converted
  python -s /usr/local/bin/command_wrapper.py 'wine msconvert ${f} --verbose --filter "peakPicking true 1-" -o converted ${params.msconvert_additional_arguments} | tee -a stdout.txt'
  """
}

// Concatenate these channels, even if one channel is empty, you get the contents either way
combined_channel = spectra_in.concat(spectra_converted)

if ( params.boxcar_convert == true) {
  process boxcar_convert {
    publishDir "$params.output_path/work/boxcar_converted_${params.random_hash}", mode: 'symlink', overwrite: true
    maxForks params.parallel_boxcar_max_forks  // Defaults to infinite
    if( params.publish_boxcar_convert == true ){
      publishDir "$publish_output_path", mode: 'copy', overwrite: true
    }
    containerOptions "$params.custom_mounts"
    input:
      file('mzML/*') from combined_channel
    output:
      file("mzML/boxcar_converted/*") into boxcar_channel
    script:
    """
    python -s /usr/local/bin/boxcar_converter.py mzML/ -p non-parallel ${params.boxcar_convert_additional_arguments} 2>&1 | tee -a stdout.txt
    """
  }
} else {
  boxcar_channel = combined_channel
}

sync_channel = boxcar_channel.collect()

// Clone channel we created to use in multiple processes (one channel per process, no more)
sync_channel.into {
  mzml_input_non_parallel
  index_channel
}

// Index parallel channel
index = 1
index_channel
  .flatten()
  .map { it -> [it, index++] }
  .view { "it = $it "}
  .set { mzml_input_parallel }

// Normal, non-parallel process
process quandenser {
  // The normal process, no parallelization
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/*"
  }
  containerOptions "$params.custom_mounts"
  input:
    file 'list.txt' from file_def
    file('mzML/*') from mzml_input_non_parallel.collect()
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
    file("Quandenser_output/consensus_spectra/**") into spectra_normal includeInputs true
    file("Quandenser_output/*") into quandenser_out_normal includeInputs true
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == false
  script:
  """
  if [ -n "${params.resume_directory}" ]; then
    mkdir -p Quandenser_output
    cp -as \$(pwd)/Quandenser_output_resume/* Quandenser_output/
  fi
  quandenser --batch list.txt ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
  """
}

process quandenser_parallel_1_dinosaur {  // About 3 min/run
  // Parallel 1: Take 1 file, run it throught dinosaur. Exit when done. Parallel process
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', overwrite: false,  pattern: "Quandenser_output/dinosaur/*"
  }
  containerOptions "$params.custom_mounts"
  maxForks params.parallel_quandenser_max_forks  // Defaults to infinite
  errorStrategy 'retry'  // If actor cell does something stupid, this should retry it once on clusters when the time runs out
  input:
    file 'list.txt' from file_def
    set file('mzML/*'), val(file_idx) from mzml_input_parallel
    each prev_tmp from Channel.fromPath("${params.output_path}/work/tmp_${params.random_hash}")
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
    file "Quandenser_output/dinosaur/*" into quandenser_out_1 includeInputs true
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true
  script:
  """
  mkdir -p Quandenser_output/dinosaur
  if [ -n "${params.resume_directory}" ]; then
    mzML_file=\$(basename -s .mzML mzML/*)
    if [ -e "\$(pwd)/Quandenser_output_resume/dinosaur/\$mzML_file.features.tsv" ]; then
      cp -as \$(pwd)/Quandenser_output_resume/dinosaur/\$mzML_file.features.tsv Quandenser_output/dinosaur/
    fi
    if [ -e "\$(pwd)/Quandenser_output_resume/dinosaur/features.${file_idx-1}.dat" ]; then
      cp -as \$(pwd)/Quandenser_output_resume/dinosaur/features.${file_idx-1}.dat Quandenser_output/dinosaur/
    fi
    echo "FILE IS \$mzML_file"
  fi
  rm -rf Quandenser_output/tmp
  ln -s ${prev_tmp} Quandenser_output/tmp
  python -s /usr/local/bin/command_wrapper.py 'quandenser --batch list.txt --partial-1-dinosaur ${file_idx} ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt'
  """
}

quandenser_out_1.into {
  quandenser_out_1_to_2_normal
  quandenser_out_1_to_2_parallel
  quandenser_out_1_to_3
  quandenser_out_1_to_4_normal
  quandenser_out_1_to_4_parallel_1
  quandenser_out_1_to_4_parallel_2
  quandenser_out_1_to_4_parallel_3
  quandenser_out_1_to_4_parallel_4
}

percolator_workdir = file("${params.output_path}/work/percolator_${params.random_hash}")  // Path to working percolator directory
result = percolator_workdir.mkdir()  // Create the directory

// Copy old percolator files to work directory
if (params.resume_directory != "") {
  percolator_resume_files = file("${resume_directory}/percolator/*")  // Path to working percolator directory
  if ( percolator_resume_files.isEmpty() ) {
    // pass
  } else {
    percolator_resume_dir = file("${resume_directory}/percolator")  // Path to working percolator directory
    percolator_workdir.deleteDir()  // Delete workdir
    percolator_resume_dir.copyTo("${params.output_path}/work/percolator_${params.random_hash}")
  }
}
if (params.parallel_quandenser == false){
  percolator_workdir.deleteDir()  // Delete workdir
}


// necessary for --use-tmp-files flag, don't copy this from the resume directory since this prevents reindexing of the matching files
tmp_workdir = file("${params.output_path}/work/tmp_${params.random_hash}")  // Path to working tmp directory
tmp_workdir.deleteDir()  // Delete workdir
result = tmp_workdir.mkdir()  // Create the directory



process quandenser_parallel_2_maracluster {
  // Parallel 2: Take all dinosaur files and run maracluster. Exit when done. Non-parallel process
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', overwrite: false,  pattern: "Quandenser_output/maracluster/*"
  }
  containerOptions "$params.custom_mounts"
  input:
    file 'list.txt' from file_def
    file('Quandenser_output/dinosaur/*') from quandenser_out_1_to_2_normal.collect()
    each prev_tmp from Channel.fromPath("${params.output_path}/work/tmp_${params.random_hash}")
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
    file "Quandenser_output/maracluster/*" into quandenser_out_2_to_3_normal, quandenser_out_2_to_4_normal includeInputs true
    file "Quandenser_output/maracluster/featureAlignmentQueue.txt" into feature_alignRetention_queue_normal
    file "Quandenser_output/maracluster/*" into maracluster_publish
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true && params.parallel_maracluster == false
  script:
  """
  if [ -n "${params.resume_directory}" ]; then
    mkdir -p Quandenser_output
    cp -asf \$(pwd)/Quandenser_output_resume/* Quandenser_output/
  fi
  rm -rf Quandenser_output/tmp
  ln -s ${prev_tmp} Quandenser_output/tmp
  quandenser --batch list.txt --partial-2-maracluster batch ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
  """
}

process quandenser_parallel_2_maracluster_parallel_1_index {
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', overwrite: false,  pattern: "Quandenser_output/maracluster/*"
  }
  containerOptions "$params.custom_mounts"
  input:
    file 'list.txt' from file_def
    file('Quandenser_output/dinosaur/*') from quandenser_out_1_to_2_parallel.collect()
    each prev_tmp from Channel.fromPath("${params.output_path}/work/tmp_${params.random_hash}")
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
    file "Quandenser_output/maracluster/*.dat_file_list.txt" into dat_file_queue, dat_file_queue_for_overlaps
    file "Quandenser_output/maracluster/*" into maracluster_out_1_to_2, maracluster_out_1_to_3, maracluster_out_1_to_4 includeInputs true
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true && params.parallel_maracluster == true
  script:
  """
  mkdir -p Quandenser_output
  if [ -n "${params.resume_directory}" ]; then
    cp -asf \$(pwd)/Quandenser_output_resume/* Quandenser_output/
    rm Quandenser_output/maracluster/*.pvalue_tree.tsv
  fi
  rm -rf Quandenser_output/tmp
  ln -s ${prev_tmp} Quandenser_output/tmp
  quandenser --batch list.txt --partial-2-maracluster index ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
  """
}

dat_file_queue
  .collectFile()  // Get file, will wait for process to finish
  .map { it.text }  // Convert file to text
  .splitText()  // Split text by line
  .map { it -> it.tokenize('\n')[0].tokenize('/')[-1] }
  .set { processing_tree }

process quandenser_parallel_2_maracluster_parallel_2_pvalue {
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', overwrite: false,  pattern: "Quandenser_output/maracluster/*"
  }
  containerOptions "$params.custom_mounts"
  maxForks params.parallel_maracluster_max_forks  // Defaults to infinite
  input:
    file 'list.txt' from file_def
    val datFile from processing_tree
    file('Quandenser_output/maracluster/*') from maracluster_out_1_to_2.collect()
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
    file "Quandenser_output/maracluster/${datFile}.pvalue*" into maracluster_out_2_to_3, maracluster_out_2_to_4
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true && params.parallel_maracluster == true
  script:
  """
  if [ -n "${params.resume_directory}" ]; then
    mkdir -p Quandenser_output
    cp -asf \$(pwd)/Quandenser_output_resume/* Quandenser_output/
  fi
  quandenser --batch list.txt --partial-2-maracluster pvalue:${datFile} ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
  """
}

dat_file_queue_for_overlaps
  .collectFile()  // Get file, will wait for process to finish
  .map { it.text }  // Convert file to text
  .splitText()  // Split text by line
  .count()
  .flatMap { it -> 0..it }
  .set { overlap_processing_tree }

process quandenser_parallel_2_maracluster_parallel_3_overlap {
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', overwrite: false,  pattern: "Quandenser_output/maracluster/*"
  }
  containerOptions "$params.custom_mounts"
  maxForks params.parallel_maracluster_max_forks  // Defaults to infinite
  input:
    file 'list.txt' from file_def
    val overlapBatchIdx from overlap_processing_tree
    file("Quandenser_output/maracluster/*") from maracluster_out_1_to_3.collect()
    file("Quandenser_output/maracluster/*") from maracluster_out_2_to_3.collect()
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
    file "Quandenser_output/maracluster/overlap.${overlapBatchIdx}.pvalue_tree.tsv" into maracluster_out_3_to_4
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true && params.parallel_maracluster == true
  script:
  """
  if [ -n "${params.resume_directory}" ]; then
    mkdir -p Quandenser_output
    cp -asf \$(pwd)/Quandenser_output_resume/* Quandenser_output/
  fi
  quandenser --batch list.txt --partial-2-maracluster overlap:${overlapBatchIdx} ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
  """
}

process quandenser_parallel_2_maracluster_parallel_4_cluster {
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', overwrite: false,  pattern: "Quandenser_output/maracluster/*"
  }
  containerOptions "$params.custom_mounts"
  input:
    file 'list.txt' from file_def
    file("Quandenser_output/maracluster/*") from maracluster_out_1_to_4.collect()
    file("Quandenser_output/maracluster/*") from maracluster_out_2_to_4.collect()
    file("Quandenser_output/maracluster/*") from maracluster_out_3_to_4.collect()
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
    file "Quandenser_output/maracluster/*" into quandenser_out_2_to_3_parallel, quandenser_out_2_to_4_parallel includeInputs true
    file "Quandenser_output/maracluster/featureAlignmentQueue.txt" into feature_alignRetention_queue_parallel
    file "Quandenser_output/maracluster/*" into maracluster_publish_parallel includeInputs true
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true && params.parallel_maracluster == true
  script:
  """
  if [ -n "${params.resume_directory}" ]; then
    mkdir -p Quandenser_output
    cp -asf \$(pwd)/Quandenser_output_resume/* Quandenser_output/
  fi
  quandenser --batch list.txt --partial-2-maracluster cluster ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
  """
}

feature_alignRetention_queue = feature_alignRetention_queue_normal.concat(feature_alignRetention_queue_parallel)
quandenser_out_2_to_3 = quandenser_out_2_to_3_normal.concat(quandenser_out_2_to_3_parallel)

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
  private int processed_alignments_current_round = 0;
  private int current_round = 0; // Dummy round to get tree started
  private Map tree_map;
  public int num_rounds;
  
  int initialize(tree) {
    tree_map = tree.countBy { it }; // create map with number of alignments per round
    
    num_rounds = tree_map.size();
    tree_map[0] = 0;  // Dummy round to get tree started
    tree_map[num_rounds+1] = 0;  // Dummy round at end of the tree, prevents nextRound() to fail after last round
    return 0;
  }
  
  int alignmentFinished() {
    return ++processed_alignments_current_round;
  }
  
  List nextRound() {
    current_round++;
    processed_alignments_current_round = 0;
    return [current_round] * tree_map[current_round];
  }
  
  int currentRoundAlignments() {
    return tree_map[current_round];
  }
}

// Empty dummy channels if not parallel
processing_tree = Channel.create()
feedback_ch = Channel.create()  // This channel loops until max_rounds has been reached
input_ch = Channel.create()
if (params.parallel_quandenser == true){
  // This queue will create the file pairs
  feature_alignRetention_queue
      .collectFile()  // Get file, will wait for process to finish
      .map { it.text }  // Convert file to text
      .splitText()  // Split text by line
      .map { it -> [it.tokenize('\t')[0].toInteger(), [file(it.tokenize('\t')[1]),
                                                       file(it.tokenize('\t')[2])]] }
      .into { processing_tree; processing_tree_copy }

  tree = new Tree()

  input_ch = processing_tree_copy
    .collect{ it[0] } // Collect alignment round indexes in a list
    .map{ it -> tree.initialize(it) }
    .mix( feedback_ch )
    .map { tree.alignmentFinished(); }  // Increment and return finished alignments
    .buffer { it >= tree.currentRoundAlignments() }  // Check if all alignments in this round are done
    .flatMap { tree.nextRound(); }
}

processing_tree_changed = Channel.from( 1 )
input_ch_changed = Channel.from( 1 )
if (params.parallel_quandenser_tree == true && params.parallel_quandenser == true) {
  processing_tree_changed = processing_tree
  input_ch_changed = input_ch
} else if (params.parallel_quandenser == true) {
  processing_tree_changed = processing_tree.collect()
}

process quandenser_parallel_3_match_features {  // About 3 min/run
  // Parallel 3: matchFeatures. Parallel
  containerOptions "$params.custom_mounts"
  maxForks params.parallel_quandenser_max_forks  // Defaults to infinite
  errorStrategy 'retry'  // If actor cell does something stupid, this should retry it once on clusters when the time run out
  input:
    file 'list.txt' from file_def
    set val(depth), val(filepair) from processing_tree_changed  // Get a filepair from a round
    // This will replace percolator directory with a link to work directory percolator
    each prev_percolator from Channel.fromPath("${params.output_path}/work/percolator_${params.random_hash}")
    each prev_tmp from Channel.fromPath("${params.output_path}/work/tmp_${params.random_hash}")

    // Access previous files from quandenser as links, takes time to publish.
    file "Quandenser_output/maracluster/*" from quandenser_out_2_to_3.collect()
    file 'Quandenser_output/dinosaur/*' from quandenser_out_1_to_3.collect()
    
    // This is the magic that makes the process loop
    val feedback_val from input_ch_changed
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true
  output:
    val 0 into feedback_ch
    val 0 into percolator_1_completed, percolator_1_completed_parallel
  script:
  if (params.parallel_quandenser_tree == false)
    """
    echo "FILES: All of them"
    ln -s ${prev_percolator} Quandenser_output/percolator
    ln -s ${prev_tmp} Quandenser_output/tmp
    quandenser --batch list.txt --partial-3-match-round 0 ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
    """
  else
    """
    echo "FILES: ${filepair[0]} and ${filepair[1]}"
    echo "PROCESSED FILES BEFORE: ${feedback_val}"
    mkdir -p pair/file1; mkdir pair/file2
    ln -s ${filepair[0]} pair/file1/; ln -s ${filepair[1]} pair/file2/
    rm -rf Quandenser_output/percolator
    ln -s ${prev_percolator} Quandenser_output/percolator
    rm -rf Quandenser_output/tmp
    ln -s ${prev_tmp} Quandenser_output/tmp
    python -s /usr/local/bin/command_wrapper.py 'quandenser --batch list.txt --partial-3-match-round ${feedback_val} ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt'
    """
}

process quandenser_parallel_4_consensus {
  // Parallel 4: Run through maracluster extra features. Non-parallel
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', overwrite: false,  pattern: "Quandenser_output/*"
  }
  containerOptions "$params.custom_mounts"
  input:
   file 'list.txt' from file_def
   each prev_percolator from Channel.fromPath("${params.output_path}/work/percolator_${params.random_hash}")
   each prev_tmp from Channel.fromPath("${params.output_path}/work/tmp_${params.random_hash}")
   file("Quandenser_output/dinosaur/*") from quandenser_out_1_to_4_normal.collect()
   file("Quandenser_output/maracluster/*") from quandenser_out_2_to_4_normal.collect()
   val percolator_1 from percolator_1_completed.collect()
   
   file('Quandenser_output_resume') from resume_directory  // optional
  output:
   file("Quandenser_output/consensus_spectra/*") into spectra_parallel
   file "Quandenser_output/*" into quandenser_out_parallel includeInputs true
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true && params.parallel_maracluster == false
  script:
  """
  if [ -n "${params.resume_directory}" ]; then
    mkdir -p Quandenser_output\$(pwd)/Quandenser_output_resume/dinosaur/\$mzML_file.features.tsv
    cp -asf \$(pwd)/Quandenser_output_resume/* Quandenser_output/
  fi
  rm -rf Quandenser_output/tmp
  ln -s ${prev_tmp} Quandenser_output/tmp
  rm -rf Quandenser_output/percolator
  ln -s ${prev_percolator} Quandenser_output/percolator  # Create link to publishDir
  quandenser --batch list.txt --partial-4-consensus batch ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
  """
}

quandenser_out_2_to_4_parallel.into {
  quandenser_out_2_to_4_parallel_1
  quandenser_out_2_to_4_parallel_2
  quandenser_out_2_to_4_parallel_3
  quandenser_out_2_to_4_parallel_4
}

process quandenser_parallel_4_consensus_parallel_1_index {
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', overwrite: false,  pattern: "Quandenser_output/maracluster_extra_features/*"
  }
  containerOptions "$params.custom_mounts"
  input:
    val percolator_1 from percolator_1_completed_parallel.collect()
    
    file 'list.txt' from file_def
    
    file("Quandenser_output/dinosaur/*") from quandenser_out_1_to_4_parallel_1.collect()
    file("Quandenser_output/maracluster/*") from quandenser_out_2_to_4_parallel_1.collect()
    each prev_percolator from Channel.fromPath("${params.output_path}/work/percolator_${params.random_hash}")
    each prev_tmp from Channel.fromPath("${params.output_path}/work/tmp_${params.random_hash}")
    
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
    file "Quandenser_output/maracluster_extra_features/*.dat_file_list.txt" into consensus_dat_file_queue, consensus_dat_file_queue_for_overlaps
    file "Quandenser_output/maracluster_extra_features/*" into consensus_out_1_to_2, consensus_out_1_to_3, consensus_out_1_to_4 includeInputs true
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true && params.parallel_maracluster == true
  script:
  """
  if [ -n "${params.resume_directory}" ]; then
    mkdir -p Quandenser_output
    cp -asf \$(pwd)/Quandenser_output_resume/* Quandenser_output/
    rm Quandenser_output/maracluster_extra_features/*.pvalue_tree.tsv
  fi
  rm -rf Quandenser_output/tmp
  ln -s ${prev_tmp} Quandenser_output/tmp
  rm -rf Quandenser_output/percolator
  ln -s ${prev_percolator} Quandenser_output/percolator
  quandenser --batch list.txt --partial-4-consensus index ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
  """
}

consensus_dat_file_queue
  .collectFile()  // Get file, will wait for process to finish
  .map { it.text }  // Convert file to text
  .splitText()  // Split text by line
  .map { it -> it.tokenize('\n')[0].tokenize('/')[-1] }
  .set { consensus_processing_tree }

process quandenser_parallel_4_consensus_parallel_2_pvalue {
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', overwrite: false,  pattern: "Quandenser_output/maracluster_extra_features/*"
  }
  containerOptions "$params.custom_mounts"
  maxForks params.parallel_maracluster_max_forks  // Defaults to infinite
  input:
    val datFile from consensus_processing_tree
    
    file 'list.txt' from file_def
    
    file("Quandenser_output/dinosaur/*") from quandenser_out_1_to_4_parallel_2.collect()
    file("Quandenser_output/maracluster/*") from quandenser_out_2_to_4_parallel_2.collect()
    each prev_percolator from Channel.fromPath("${params.output_path}/work/percolator_${params.random_hash}")
    each prev_tmp from Channel.fromPath("${params.output_path}/work/tmp_${params.random_hash}")
    
    file('Quandenser_output/maracluster_extra_features/*') from consensus_out_1_to_2.collect()
    
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
    file "Quandenser_output/maracluster_extra_features/${datFile}.pvalue*" into consensus_out_2_to_3, consensus_out_2_to_4
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true && params.parallel_maracluster == true
  script:
  """
  if [ -n "${params.resume_directory}" ]; then
    mkdir -p Quandenser_output
    cp -asf \$(pwd)/Quandenser_output_resume/* Quandenser_output/
  fi
  rm -rf Quandenser_output/tmp
  ln -s ${prev_tmp} Quandenser_output/tmp
  rm -rf Quandenser_output/percolator
  ln -s ${prev_percolator} Quandenser_output/percolator
  quandenser --batch list.txt --partial-4-consensus pvalue:${datFile} ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
  """
}

consensus_dat_file_queue_for_overlaps
  .collectFile()  // Get file, will wait for process to finish
  .map { it.text }  // Convert file to text
  .splitText()  // Split text by line
  .count()
  .flatMap { it -> 0..it }
  .set { consensus_overlap_processing_tree }

process quandenser_parallel_4_consensus_parallel_3_overlap {
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', overwrite: false,  pattern: "Quandenser_output/maracluster_extra_features/*"
  }
  containerOptions "$params.custom_mounts"
  maxForks params.parallel_maracluster_max_forks  // Defaults to infinite
  input:
    val overlapBatchIdx from consensus_overlap_processing_tree
    
    file 'list.txt' from file_def
    
    file("Quandenser_output/dinosaur/*") from quandenser_out_1_to_4_parallel_3.collect()
    file("Quandenser_output/maracluster/*") from quandenser_out_2_to_4_parallel_3.collect()
    each prev_percolator from Channel.fromPath("${params.output_path}/work/percolator_${params.random_hash}")
    each prev_tmp from Channel.fromPath("${params.output_path}/work/tmp_${params.random_hash}")
    
    file("Quandenser_output/maracluster_extra_features/*") from consensus_out_1_to_3.collect()
    file("Quandenser_output/maracluster_extra_features/*") from consensus_out_2_to_3.collect()
    
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
    file "Quandenser_output/maracluster_extra_features/overlap.${overlapBatchIdx}.pvalue_tree.tsv" into consensus_out_3_to_4
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true && params.parallel_maracluster == true
  script:
  """
  if [ -n "${params.resume_directory}" ]; then
    mkdir -p Quandenser_output
    cp -asf \$(pwd)/Quandenser_output_resume/* Quandenser_output/
  fi
  rm -rf Quandenser_output/tmp
  ln -s ${prev_tmp} Quandenser_output/tmp
  rm -rf Quandenser_output/percolator
  ln -s ${prev_percolator} Quandenser_output/percolator
  quandenser --batch list.txt --partial-4-consensus overlap:${overlapBatchIdx} ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
  """
}

process quandenser_parallel_4_consensus_parallel_4_cluster {
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', overwrite: false,  pattern: "Quandenser_output/*"
  }
  containerOptions "$params.custom_mounts"
  input:
    file 'list.txt' from file_def
    
    file("Quandenser_output/dinosaur/*") from quandenser_out_1_to_4_parallel_4.collect()
    file("Quandenser_output/maracluster/*") from quandenser_out_2_to_4_parallel_4.collect()
    each prev_percolator from Channel.fromPath("${params.output_path}/work/percolator_${params.random_hash}")
    each prev_tmp from Channel.fromPath("${params.output_path}/work/tmp_${params.random_hash}")
    
    file("Quandenser_output/maracluster_extra_features/*") from consensus_out_1_to_4.collect()
    file("Quandenser_output/maracluster_extra_features/*") from consensus_out_2_to_4.collect()
    file("Quandenser_output/maracluster_extra_features/*") from consensus_out_3_to_4.collect()
    
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
    file("Quandenser_output/consensus_spectra/*") into spectra_parallel_2
    file "Quandenser_output/*" into quandenser_out_parallel_2 includeInputs true
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true && params.parallel_maracluster == true
  script:
  """
  if [ -n "${params.resume_directory}" ]; then
    mkdir -p Quandenser_output
    cp -asf \$(pwd)/Quandenser_output_resume/* Quandenser_output/
  fi
  rm -rf Quandenser_output/tmp
  ln -s ${prev_tmp} Quandenser_output/tmp
  rm -rf Quandenser_output/percolator
  ln -s ${prev_percolator} Quandenser_output/percolator
  quandenser --batch list.txt --partial-4-consensus cluster ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
  """
}


// Concatenate quandenser_out. We don't know which the user did, so we mix them
quandenser_out = quandenser_out_normal.concat(quandenser_out_parallel).concat(quandenser_out_parallel_2)

// Do the same thing with the consensus spectra
spectra = spectra_normal.concat(spectra_parallel).concat(spectra_parallel_2)

process tide_search {
  if( params.publish_quandenser == true ){
    publishDir publish_output_path, mode: 'copy', pattern: "crux-output/*", overwrite: true
  }
  containerOptions "$params.custom_mounts"
  input:
  file 'seqdb.fa' from db
  file ms2_files from spectra.collect()  // N.B.: Sensitive to naming (no blankspace, parenthesis and such)
  output:
  file("crux-output/*") into id_files
  file("${seq_index_name}") into index_files
  when:
    params.workflow == "Full"
  script:
  """
  crux tide-index --missed-cleavages ${params.missed_cleavages} --mods-spec ${params.mods_spec} --decoy-format protein-reverse ${params.crux_index_additional_arguments} seqdb.fa ${seq_index_name}
  crux tide-search --precursor-window ${params.precursor_window} --precursor-window-type ppm --overwrite T --concat T ${ms2_files} ${seq_index_name} ${params.crux_search_additional_arguments}
  crux percolator --top-match 1 crux-output/tide-search.txt ${params.crux_percolator_additional_arguments}
  """
}

process triqler {
  if( params.publish_triqler == true ){
    publishDir "$publish_output_path/triqler_output", mode: 'copy', pattern: "*proteins.*",overwrite: true
  }
  containerOptions "$params.custom_mounts"
  input:
    file("Quandenser_output/*") from quandenser_out.collect()
    file("crux-output/*") from id_files.collect()
    file 'list.txt' from file_def
  output:
    file("*proteins.*") into triqler_output
    file("triqler.zip") into triqler_zip_output
  when:
    params.workflow == "Full"
  script:
  """
  python -s /usr/local/bin/prepare_input.py -l list.txt -f Quandenser_output/Quandenser.feature_groups.tsv -i crux-output/percolator.target.psms.txt,crux-output/percolator.decoy.psms.txt -q triqler_input.tsv
  python -sm triqler --fold_change_eval ${params.fold_change_eval} triqler_input.tsv ${params.triqler_additional_arguments} 2>&1 | tee -a stdout.txt
  zip triqler.zip *.tsv *.csv -x "triqler_input*"
  """
}

triqler_output.flatten().subscribe{ println "Received: " + it.getName() }

workflow.onComplete {
    println("QUANDENSER PIPELINE COMPLETED")
    if (params.email != "" && params.sendfiles == true && params.workflow == "Full") {
      sendMail{to params.email
               subject "Workflow ${workflow.runName} output files"
               body "$params"
               attach triqler_zip_output.getVal()
               attach file_def_publish}
    }
}
