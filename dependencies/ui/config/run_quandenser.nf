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

process quandenser_parallel_1 {
  // Parallel 1: Take 1 file, run it throught dinosaur. Exit when done. Parallel process
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/dinosaur/*"
  containerOptions "$params.custom_mounts"
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
  quandenser --batch modified_list.txt --max-missing ${params.max_missing} --parallel-1 true ${params.quandenser_additional_arguments}
	"""
}

process quandenser_parallel_2 {
  // Parallel 2: Take all dinosaur files and run maracluster. Exit when done. Non-parallel process
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/maracluster/*"
  containerOptions "$params.custom_mounts"
  input:
   file 'list.txt' from file_def
   file('mzML/*') from combined_channel_parallel_2.collect()
   file('Quandenser_output/dinosaur/*') from quandenser_out_1_to_2_dinosaur.collect()
  output:
	 file "Quandenser_output/*" into quandenser_out_2_to_3
  when:
    params.workflow == "Full" && params.parallel_quandenser == true
  script:
	"""
	quandenser --batch list.txt --max-missing ${params.max_missing} --parallel-2 true ${params.quandenser_additional_arguments}
	"""
}

// Parallel process 2 will output a tree which must be calculated IN ORDER. However, each level can be calculated in parallel.
// This means you first needs to get the maximum depth
process quandenser_parallel_3 {
  // Parallel 3: Take all dinosaur files and maracluster files. Run dinosaur + percolator on one specific filepair. Exit when done.
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/percolator/*"
  publishDir "work/params.random_hash", mode: 'symlink', overwrite: true,  pattern: "Quandenser_output/percolator/*"
  containerOptions "$params.custom_mounts"
  input:
   file 'list.txt' from file_def
   file('mzML/*') from combined_channel_parallel_3.collect()
   file("*") from quandenser_out_2_to_3
  output:
   file "Quandenser_output/*" into quandenser_out_3_to_4 includeInput true
  when:
    params.workflow == "Full" && params.parallel_quandenser == true
  script:
	"""
	quandenser --batch list.txt --max-missing ${params.max_missing} --parallel-3 true ${params.quandenser_additional_arguments}
	"""
}

process quandenser_Parallel_4 {
  // Parallel 4: Run through the whole process. Quandenser will skip all the files that has already completed
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/*"
  containerOptions "$params.custom_mounts"
  input:
   file 'list.txt' from file_def
   file('mzML/*') from combined_channel_parallel_3.collect()
   file('Quandenser_output/*') from quandenser_out_3_to_4.collect()
  output:
	 file("Quandenser_output/consensus_spectra/**") into spectra_parallel
	 file "Quandenser_output/*" into quandenser_out_parallel includeInput true
  when:
    params.workflow == "Full" && params.parallel_quandenser == true
  script:
	"""
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
