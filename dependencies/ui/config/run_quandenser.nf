#!/usr/bin/env nextflow
echo true

// Since we can add labels to the directories, the output path of the files are
// different compared to work
publish_output_path = params.output_path + params.output_label

// Check if resume folder has been set
if (params.resume_directory != "") {
  resume_directory = file(params.resume_directory)
  println("Resuming from directory: ${resume_directory}")
} else {
  resume_directory = file("NULL")
}

file_def = file(params.batch_file)  // batch_file

// change the path to where the database is and the batch file is if you are only doing msconvert
if( params.workflow == "MSconvert" || params.workflow == "Quandenser" ) {
  db_file = params.batch_file  // Will not be used, so junk name
} else {
  db_file = params.db
}
db = file(db_file)  // Sets "db" as the file defined above
seq_index_name = "${db.getName()}.index"  // appends "index" to the db filename

if (params.workflow != "MSconvert") {
  // Preprocessing file_list
  Channel  // mzML files with proper labeling
    .from(file_def.readLines())
    .map { it -> it.tokenize('\t') }
    .filter { it.size() > 1 }  // filters any input that is not <path> <label>
    .filter { it[0].tokenize('.')[-1] == "mzML" }  // filters any input that is not .mzML
    .map { it -> file(it[0]) }
    .into { spectra_in; spectra_in_q }  // Puts the files into spectra_in
} else {
  spectra_in = Channel.from(1)  // This prevents name collision crash
}

if (params.workflow != "MSconvert") {
  Channel  // non-mzML files with proper labeling which will be converted
    .from(file_def.readLines())
    .map { it -> it.tokenize('\t') }
    .filter { it.size() > 1 }  // filters any input that is not <path> <X>
    .filter{ it[0].tokenize('.')[-1] != "mzML" }  // filters any input that is .mzML
    .map { it -> file(it[0]) }
    .into { spectra_convert; spectra_convert_bool }
} else {
  Channel  // non-mzML files with proper labeling which will be converted
    .from(file_def.readLines())
    .map { it -> it.tokenize('\t') }
    .filter { it.size() > 1 }  // filters any input that is not <path> <X>
    .map { it -> file(it[0]) }
    .into { spectra_convert; spectra_convert_bool }
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
  if( file_extension != "mzML" ){
    // Note: if you are running only msconvert on mzML files, the path will be wrong. However, since msconvert+quandenser
    // is not integrated yet, I can let it slide
    all_lines[count] = params.output_path + "/work/converted_${params.random_hash}/converted/" + file_name + ".mzML" + '\t' + file_label
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
  publishDir "$params.output_path/work/converted_${params.random_hash}", mode: 'symlink', overwrite: true, pattern: "converted/*"
  publishDir "$publish_output_path", mode: 'copy', overwrite: true, pattern: "converted/*"
  containerOptions "$params.custom_mounts"
  maxForks params.parallel_msconvert_max_forks
  input:
    file f from spectra_convert_channel
  output:
    file("converted/*.mzML") into spectra_converted
  script:
	"""
  mkdir -p converted
  wine msconvert ${f} --mzML --filter "peakPicking true 1-" -o converted ${params.msconvert_additional_arguments} | tee -a stdout.txt
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
}

// Normal, non-parallel process
process quandenser {
  // The normal process, no parallelization
  publishDir publish_output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/*"
  containerOptions "$params.custom_mounts"
  input:
    file 'list.txt' from file_def
    file('mzML/*') from combined_channel_normal.collect()
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
	quandenser --batch list.txt --max-missing ${params.max_missing} ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
	"""
}

process quandenser_parallel_1 {  // About 3 min/run
  // Parallel 1: Take 1 file, run it throught dinosaur. Exit when done. Parallel process
  publishDir publish_output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/dinosaur/*"
  containerOptions "$params.custom_mounts"
  maxForks params.parallel_quandenser_max_forks  // Defaults to infinite
  input:
    file 'list.txt' from file_def
    file('mzML/*') from combined_channel_parallel_1
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
	  file "Quandenser_output/dinosaur/*" into quandenser_out_1_to_2_dinosaur
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true
  script:
	"""
  if [ -n "${params.resume_directory}" ]; then
    mkdir -p Quandenser_output
    cp -as \$(pwd)/Quandenser_output_resume/* Quandenser_output/
    mzML_file=\$(basename -s .mzML mzML/*)
    echo "FILE IS \$mzML_file"
    find Quandenser_output/dinosaur/* ! -name "\$mzML_file*" -delete
  fi
  cp -L list.txt modified_list.txt  # Need to copy not link, but a copy of file which I can modify
  filename=\$(find mzML/* | xargs basename)
  sed -i "/\$filename/!d" modified_list.txt
  quandenser-modified --batch modified_list.txt --max-missing ${params.max_missing} --parallel-1 true ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
	"""
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

process quandenser_parallel_2 {  // About 30 seconds
  // Parallel 2: Take all dinosaur files and run maracluster. Exit when done. Non-parallel process
  publishDir publish_output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/maracluster/*"
  publishDir publish_output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/dinosaur/*"
  containerOptions "$params.custom_mounts"
  input:
    file 'list.txt' from file_def
    file('mzML/*') from combined_channel_parallel_2.collect()
    file('Quandenser_output/dinosaur/*') from quandenser_out_1_to_2_dinosaur.collect()
    file('Quandenser_output_resume') from resume_directory  // optional
  output:
	  file "Quandenser_output/*" into quandenser_out_2_to_3, quandenser_out_2_to_4 includeInputs true
    file "Quandenser_output/maracluster/featureAlignmentQueue.txt" into alignRetention_queue
    file "Quandenser_output/dinosaur/allFeatures.txt" into allFeatures_queue
    file "Quandenser_output/maracluster/*" into maracluster_publish
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true
  script:
	"""
  if [ -n "${params.resume_directory}" ]; then
    mkdir -p Quandenser_output
    cp -asf \$(pwd)/Quandenser_output_resume/* Quandenser_output/
  fi
	quandenser-modified --batch list.txt --max-missing ${params.max_missing} --parallel-2 true ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
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

  // Initialize first values, so they exist outside process
  tree_map_reconstructed = [0:1]  // Initialize first value
  processed_files = [0]  // Value needs to be in list, to preserve changes made in sync variables
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
     prev_files = []  // List to store files from previous rounds
     all_lines = alignRetention_file.readLines()  // Get all lines from maracluster tree
     for( line in all_lines ){
       file1 = line.tokenize('\t')[1].tokenize('/')[-1]  // Get file name from file 1
       file2 = line.tokenize('\t')[2].tokenize('/')[-1]  // Get file name from file 2
       // When the previous round contains any of the files, create a new round
       if (prev_files.contains(file1) || prev_files.contains(file2) ) {
          tree_map_reconstructed[current_depth] = current_width  // Add new round, with width
          current_depth++  // Add 1 to depth. The files in this loop will be added to that round
          current_width = 1  // Since we have 1 pair already, do not start from 0
          prev_files.clear()  // Clear previous files.
       } else {
         current_width++  // Just add 1 to width if they are not colliding
       }
       prev_files << file1
       prev_files << file2
     }
     tree_map_reconstructed[current_depth] = current_width
     println("Treemap is $tree_map")
     println("Reconstructed treemap is $tree_map_reconstructed")

     end_depth = current_depth + 1
     tree_map_reconstructed[end_depth] = 1  // Add 1 to the last value, to prevent premature stop
     tree_map_reconstructed[-1] = tree_map_reconstructed[0]  // Initializiation of first values
     initial_range = 0..<tree_map_reconstructed[0]  // Initial range

     // Note: since we are starting with 0 processed files and we initialize with a range,
     // set processed files to be exactly 0 for the first batch of files
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
  .flatten()  // Flatten input list
  .mix( feedback_ch.until(condition) )  // Continously add until files have run out
  .map { processed_files[0]++ }  // Add 1 to processed files for each emit from feedback_ch
  .map { it -> current_width++; }  // Add 1 to current width and emit value to buffer
  .buffer { it >= tree_map_reconstructed[current_depth] - 1}  // When width is more than width at tree
  .map { it -> current_depth++; current_width = 0; current_depth}  // Add 1 to depth, pass on current depth
  .flatMap { n -> 0..<tree_map_reconstructed[n] }  // Convert number to a list same size as amount of parallel processes
  .map { it -> processed_files[0] }  // Convert range 0,1,2.... to processed_files (ex 5,5,5,5...)
} else {
  // Empty dummy channels if not parallel
  processing_tree = Channel.create()
  feedback_ch = Channel.create()
  input_ch = Channel.create()
}

process quandenser_parallel_3 {  // About 3 min/run
  // Parallel 3: matchFeatures. Parallel
  containerOptions "$params.custom_mounts"
  maxForks params.parallel_quandenser_max_forks  // Defaults to infinite
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
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true
  output:
    val 0 into feedback_ch
    val 0 into percolator_1_completed
  script:
  """
  echo "FILES: ${filepair[0]} and ${filepair[1]}"
  echo "PROCESSED FILES BEFORE: ${feedback_val}"
  mkdir -p pair/file1; mkdir pair/file2
  ln -s ${filepair[0]} pair/file1/; ln -s ${filepair[1]} pair/file2/
  ln -s ${prev_percolator} Quandenser_output/percolator
  quandenser-modified --batch list.txt --max-missing ${params.max_missing} --parallel-3 ${feedback_val + 1} ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
  """
}

process quandenser_parallel_4 {  // About 30 seconds
  // Parallel 4: Run through maracluster extra features. Non-parallel
  publishDir publish_output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/maracluster_extra_features/*"
  containerOptions "$params.custom_mounts"
  input:
   file 'list.txt' from file_def
   each prev_percolator from Channel.fromPath("${params.output_path}/work/percolator_${params.random_hash}")
   file("Quandenser_output/*") from quandenser_out_2_to_4.collect()
   val percolator_1 from percolator_1_completed.collect()
  output:
	 file "Quandenser_output/*" into quandenser_out_4_to_5 includeInputs true
   file "Quandenser_output/maracluster_extra_features/*" into maracluster_extra_features_publish
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true
  script:
	"""
  ln -s ${prev_percolator} Quandenser_output/percolator  # Create link to publishDir
	quandenser-modified --batch list.txt --max-missing ${params.max_missing} --parallel-4 true ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
	"""
}

process quandenser_parallel_5 {
  // Parallel 5: Create the consensus_spectra + clustering. Non-parallel
  publishDir publish_output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/*"
  containerOptions "$params.custom_mounts"
  input:
   file 'list.txt' from file_def
   each prev_percolator from Channel.fromPath("${params.output_path}/work/percolator_${params.random_hash}")
   file("Quandenser_output/*") from quandenser_out_4_to_5.collect()  // Includes links to first percolator
  output:
	 file("Quandenser_output/consensus_spectra/**") into spectra_parallel
	 file "Quandenser_output/*" into quandenser_out_parallel includeInputs true
  when:
    (params.workflow == "Full" || params.workflow == "Quandenser") && params.parallel_quandenser == true
  script:
	"""
  rm -rf Quandenser_output/percolator
  ln -s ${prev_percolator} Quandenser_output/percolator
	quandenser-modified --batch list.txt --max-missing ${params.max_missing} ${params.quandenser_additional_arguments} 2>&1 | tee -a stdout.txt
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

process tide_search {
  publishDir publish_output_path, mode: 'copy', pattern: "crux-output/*", overwrite: true
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
  crux tide-index --missed-cleavages ${params.missed_clevages} --mods-spec ${params.mods_spec} --decoy-format protein-reverse seqdb.fa ${seq_index_name} ${params.crux_index_additional_arguments}
	crux tide-search --precursor-window ${params.precursor_window} --precursor-window-type ppm --overwrite T --concat T ${ms2_files} ${seq_index_name} ${params.crux_search_additional_arguments}
	crux percolator --top-match 1 crux-output/tide-search.txt ${params.crux_percolator_additional_arguments}
  """
}

process triqler {
  publishDir "$publish_output_path/triqler_output", mode: 'copy', pattern: "proteins.*",overwrite: true
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
