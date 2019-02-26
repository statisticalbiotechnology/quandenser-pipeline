#!/usr/bin/env nextflow
echo true

file_def = file(params.batch_file)  // batch_file

// change the path to where the database is and the batch file is if you are only doing msconvert
if( params.workflow == "MSconvert" ) {
  db_file = params.batch_file  // Will not be used, so junk name
} else {
  db_file = params.db
}
db = file(db_file)  // Sets "db" as the file defined above
seq_index_name = "${db.getName()}.index"  // appends "index" to the db filename

// Preprocessing file_list
Channel  // mzML files with proper labeling
  .from(file_def.readLines())
  .map { it -> it.tokenize('\t') }
  .filter { it.size() > 1 }  // filters any input that is not <path> <X>
  .filter { it[0].tokenize('.')[-1] == "mzML" }  // filters any input that is not .mzML
  .map { it -> file(it[0]) }
  .into { spectra_in; spectra_in_q }  // Puts the files into spectra_in

Channel  // non-mzML files with proper labeling which will be converted
  .from(file_def.readLines())
  .map { it -> it.tokenize('\t') }
  .filter { it.size() > 1 }  // filters any input that is not <path> <X>
  .filter{ it[0].tokenize('.')[-1] != "mzML" }  // filters any input that is .mzML
  .map { it -> file(it[0]) }
  .into { spectra_convert; spectra_convert_bool }

// Replaces the lines of non-mzML with their corresponding converted mzML counterpart
count = 0
amount_of_non_mzML = 0
all_lines = file_def.readLines()
for( line in all_lines ){
  file_path = line.tokenize('\t')[0]
  file_label = line.tokenize('\t')[-1]
  file_name = (file_path.tokenize('/')[-1]).tokenize('.')[0]  // Split '/', take last. Split '.', take first
  file_extension = file_path.tokenize('.')[-1]
  if( file_extension != "mzML" ){
    all_lines[count] = params.output_path + "/work/converted_${params.random_hash}/" + file_name + ".mzML" + '\t' + file_label
    count++
    amount_of_non_mzML++
  } else {
    // add as is, no change
    count++
  }
}

// Create new batch file to use in work directory. Add the "corrected" raw to mzML paths here
file_def = file("$params.output_path/work/file_list_${params.random_hash}.txt")
file_def.text = ""  // Clear file, if it exists
total_spectras = 0
for( line in all_lines ){
  file_def << line + '\n'  // need to add \n
  total_spectras++
}


println("Total spectras = " + total_spectras)
println("Spectras that will be converted = " + amount_of_non_mzML)

if( params.parallel_msconvert == true ) {
  spectra_convert_channel = spectra_convert  // No collect = parallel processing, one file in each process
} else {
  spectra_convert_channel = spectra_convert.collect()  // Collect = everything is run in one process
}

process msconvert {
  /* Note: quandenser needs the file_list with paths to the files.
  Problem: We do not know the mzML file location during work and writing large files to publishDir is slow,
  so there might be a possibility that some strange issues with incomplete mzML files being inputted to quandenser.
  The solution is to have two publishdirs, one where the true files are being inserted for future use,
  while we point in the file_list to the files in the work directory with symlinks.
  The symlinks are fast to write + they point to complete files + we know the symlinks location --> fixed :)
  */
  publishDir "$params.output_path/work/converted_${params.random_hash}", mode: 'symlink', overwrite: true, pattern: "*"
  publishDir "$params.output_path/converted", mode: 'copy', overwrite: true, pattern: "*"
  containerOptions "$params.custom_mounts"
  maxForks params.parallel_msconvert_max_forks
  input:
    file f from spectra_convert_channel
  output:
    file("*mzML") into spectra_converted
  script:
	"""
  wine msconvert ${f} --mzML --zlib --filter peakPicking true 1- ${params.msconvert_additional_arguments}
  """
}

// Problem: We get a channel with proper mzML files and non mzML file
// Solution: Concate these channel, even if one channel is empty, you get the contents either way
c1 = spectra_in
c2 = spectra_converted
combined_channel = c1.concat(c2)  // This will mix the spectras into one channel

// Clone channel we created to use in multiple processes (one channel per process, no more)
combined_channel.into {
  combined_channel_normal
  combined_channel_parallel_1
  combined_channel_parallel_2
  combined_channel_parallel_3
}

// Normal, non-parallel process
process quandenser {
  // The normal process, no parallelization
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/*"
  containerOptions "$params.custom_mounts"
  input:
  file 'list.txt' from file_def
  file('mzML/*') from combined_channel_normal.collect()
  output:
	file("Quandenser_output/consensus_spectra/**") into spectra_normal
	file "Quandenser_output/*" into quandenser_out_normal
  when:
    params.workflow == "Full" && params.parallel_quandenser == false
  script:
	"""
	quandenser --batch list.txt --max-missing ${params.max_missing} ${params.quandenser_additional_arguments}
	"""
}


process quandenser_parallel_1 {  // About 3 min/run
  // Parallel 1: Take 1 file, run it throught dinosaur. Exit when done. Parallel process
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/dinosaur/*"
  containerOptions "$params.custom_mounts"
  maxForks params.parallel_quandenser_max_forks  // Defaults to the amount of cores
  input:
   file 'list.txt' from file_def
   file('mzML/*') from combined_channel_parallel_1
  output:
	 file "Quandenser_output/dinosaur/*" into quandenser_out_1_to_2_dinosaur
  when:
    params.workflow == "Full" && params.parallel_quandenser == true
  script:
	"""
  cp -L list.txt modified_list.txt  # Need to copy not link, but a copy of file which I can modify
  filename=\$(find mzML/* | xargs basename)
  sed -i "/\$filename/!d" modified_list.txt
  quandenser-modified --batch modified_list.txt --max-missing ${params.max_missing} --parallel-1 true ${params.quandenser_additional_arguments}
	"""
}

percolator_workdir = file("${params.output_path}/work/percolator_${params.random_hash}")  // Path to working percolator directory
result = percolator_workdir.mkdir()  // Create the directory
process quandenser_parallel_2 {  // About 30 seconds
  // Parallel 2: Take all dinosaur files and run maracluster. Exit when done. Non-parallel process
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/maracluster/*"
  containerOptions "$params.custom_mounts"
  input:
   file 'list.txt' from file_def
   file('mzML/*') from combined_channel_parallel_2.collect()
   file('Quandenser_output/dinosaur/*') from quandenser_out_1_to_2_dinosaur.collect()
  output:
	 file "Quandenser_output/*" into quandenser_out_2_to_3, quandenser_out_2_to_4 includeInputs true
   file "alignRetention_queue.txt" into alignRetention_queue
  when:
    params.workflow == "Full" && params.parallel_quandenser == true
  script:
	"""
	quandenser-modified --batch list.txt --max-missing ${params.max_missing} --parallel-2 true ${params.quandenser_additional_arguments}
	"""
}

if (params.parallel_quandenser == true){
  // This queue will define maximum depth of the processing tree
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
    exectutor = 'local'  // This takes 1 ms, no real calculations
    input:
      val wait1 from wait_queue_1
      val wait2 from wait_queue_2
    output:
      val 0 into sync_ch
    exec:
      end_depth = max_depth + 1  // Need to add last value in map to prevent crash
      tree_map[end_depth] = 1  // tree_map should be defined by now
      println("Processor tree is ${tree_map}")
      println("Maximum depth = $max_depth")
      println("Syntax: round_nr:amount_of_parallel_files")  // A map is kind of like a dict in python
  }

  condition = { 1 == 0 }  // Never stop. It will do so automatically when the files run out
  feedback_ch = Channel.create()  // This channel loop until max_depth has been reached
  feedback_ch_copy = Channel.create()  // This channel loop until max_depth has been reached

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
  input_ch = sync_ch  // Syncronization, aka wait until tree_map is defined and last round added
  .mix( feedback_ch.until(condition).unique() )  // Continously add
  .flatMap { n -> 0..<tree_map[n] }  // Convert number to parallel processes

} else {
  // Empty dummy channels if not parallel
  processing_tree = Channel.create()
  feedback_ch = Channel.create()
  input_ch = Channel.create()
}

process quandenser_parallel_3 {  // About 3 min/run
  // Parallel 3: matchFeatures. Parallel
  publishDir params.output_path, mode: 'copy', overwrite: false,  pattern: "Quandenser_output/percolator/*"
  containerOptions "$params.custom_mounts"
  input:
    file 'list.txt' from file_def
    set val(depth), val(filepair) from processing_tree  // Get a filepair from a round
    // This will replace percolator directory with a link to work directory percolator
    each prev_percolator from Channel.fromPath("${params.output_path}/work/percolator_${params.random_hash}")

    // Access previous files from quandenser. Consider maracluster files as links, takes time to publish
    file "Quandenser_output/*" from quandenser_out_2_to_3.collect()

    // This is the magic that makes the process loop
    val feedback_val from input_ch
  when:
    params.workflow == "Full" && params.parallel_quandenser == true
  output:
    val depth into feedback_ch
    val 0 into percolator_1_completed
  exec:
    depth++
  script:
  """
  echo "DEPTH ${depth - 1}"
  echo "FILES ${filepair[0]} and ${filepair[1]}"
  mkdir -p pair/file1; mkdir pair/file2
  ln -s ${filepair[0]} pair/file1/; ln -s ${filepair[1]} pair/file2/;
  ln -s ${prev_percolator} Quandenser_output/percolator
  quandenser-modified --batch list.txt --max-missing ${params.max_missing} --parallel-3 ${depth} ${params.quandenser_additional_arguments}
	"""
}

process quandenser_parallel_4 {  // About 30 seconds
  // Parallel 4: Run through maracluster extra features. Non-parallel
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/maracluster_extra_features/*"
  containerOptions "$params.custom_mounts"
  input:
   file 'list.txt' from file_def
   each prev_percolator from Channel.fromPath("${params.output_path}/work/percolator_${params.random_hash}")
   file("Quandenser_output/*") from quandenser_out_2_to_4.collect()
   val percolator_1 from percolator_1_completed.collect()
  output:
	 file "Quandenser_output/*" into quandenser_out_4_to_5 includeInputs true
  when:
    params.workflow == "Full" && params.parallel_quandenser == true
  script:
	"""
  ln -s ${prev_percolator} Quandenser_output/percolator  # Create link to publishDir
	quandenser-modified --batch list.txt --max-missing ${params.max_missing} --parallel-4 true ${params.quandenser_additional_arguments}
	"""
}

process quandenser_parallel_5 {
  // Parallel 5: Create the consensus_spectra + clustering. Non-parallel
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/*"
  containerOptions "$params.custom_mounts"
  input:
   file 'list.txt' from file_def
   each prev_percolator from Channel.fromPath("${params.output_path}/work/percolator_${params.random_hash}")
   file("Quandenser_output/*") from quandenser_out_4_to_5.collect()  // Includes links to first percolator
  output:
	 file("Quandenser_output/consensus_spectra/**") into spectra_parallel
	 file "Quandenser_output/*" into quandenser_out_parallel includeInputs true
  when:
    params.workflow == "Full" && params.parallel_quandenser == true
  script:
	"""
  rm -rf Quandenser_output/percolator
  ln -s ${prev_percolator} Quandenser_output/percolator
	quandenser-modified --batch list.txt --max-missing ${params.max_missing} ${params.quandenser_additional_arguments}
	"""
}

// Concate quandenser_out. We don't know which the user did, so we mix them
c1 = quandenser_out_normal
c2 = quandenser_out_parallel
quandenser_out = c1.concat(c2)

// Do the same thing with the consensus spectra
c1 = spectra_normal
c2 = spectra_parallel
spectra = c1.concat(c2)

process tide_perc_search {
  publishDir params.output_path, mode: 'copy', pattern: "crux-output/*", overwrite: true
  containerOptions "$params.custom_mounts"
  input:
	file 'seqdb.fa' from db
	file ms2_files from spectra.collect()  // PS: Sensitive to naming (no blankspace, paranthesis and such)
  output:
	file("crux-output/*") into id_files
  file("${seq_index_name}") into index_files
  when:
    params.workflow == "Full"
  script:
	"""
  crux tide-index --missed-cleavages ${params.missed_clevages} --mods-spec 2M+15.9949 --decoy-format protein-reverse seqdb.fa ${seq_index_name} ${params.crux_index_additional_arguments}
	crux tide-search --precursor-window ${params.precursor_window} --precursor-window-type ppm --overwrite T --concat T ${ms2_files} ${seq_index_name} ${params.crux_search_additional_arguments}
	crux percolator --top-match 1 crux-output/tide-search.txt ${params.crux_percolator_additional_arguments}
  """
}

process triqler {
  publishDir params.output_path, mode: 'copy', pattern: "proteins.*",overwrite: true
  containerOptions "$params.custom_mounts"
  input:
	file("Quandenser_output/*") from quandenser_out.collect()
	file("crux-output/*") from id_files.collect()
	file 'list.txt' from file_def
  output:
	file("proteins.*") into triqler_output
  when:
    params.workflow == "Full"
  script:
	"""
	prepare_input.py -l list.txt -f Quandenser_output/Quandenser.feature_groups.tsv -i crux-output/percolator.target.psms.txt,crux-output/percolator.decoy.psms.txt -q triqler_input.tsv
	triqler --fold_change_eval ${params.fold_change_eval} triqler_input.tsv ${params.triqler_additional_arguments}
  """
}

triqler_output.flatten().subscribe{ println "Received: " + it.getName() }
