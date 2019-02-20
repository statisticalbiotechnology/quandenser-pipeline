#!/usr/bin/env nextflow
echo true

/* Important:
change the path to where the database is and the batch file is
*/
file_def = file(params.batch_file)  // batch_file
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
  .filter{ it.size() > 1 }  // filters any input that is not <path> <X>
  .filter{ it[0].tokenize('.')[-1] == "mzML" }  // filters any input that is not .mzML
  .map { it -> file(it[0]) }
  .into{ spectra_in; spectra_in_q }  // Puts the files into spectra_in

Channel  // non-mzML files with proper labeling which will be converted
  .from(file_def.readLines())
  .map { it -> it.tokenize('\t') }
  .filter{ it.size() > 1 }  // filters any input that is not <path> <X>
  .filter{ it[0].tokenize('.')[-1] != "mzML" }  // filters any input that is .mzML
  .map { it -> file(it[0]) }
  .into{ spectra_convert; spectra_convert_bool }

// Replaces the lines in the file_list with the new paths (will only change file if non-mzML)
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
file_def = file("$params.output_path/work/file_list_${params.random_hash}.txt")  // Create new file for in work directory
file_def.text = ""  // Clear file, if it exists
total_spectras = 0
for( line in all_lines ){
  file_def << line + '\n'  // need to add \n
  total_spectras++
}
println("Total spectras = " + total_spectras)
println("Spectras that will be converted = " + amount_of_non_mzML)

if( params.parallell_msconvert == true ) {
  spectra_convert_channel = spectra_convert  // No collect = parallell processing
} else {
  spectra_convert_channel = spectra_convert.collect()
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

c1 = spectra_in
c2 = spectra_converted
combined_channel = c1.concat(c2)  // This will mix the spectras into one channel

combined_channel.into {  // Clone channel
  combined_channel_normal
  combined_channel_parallell_1
  combined_channel_parallell_2
  combined_channel_parallell_3
}

process quandenser {
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/*"
  containerOptions "$params.custom_mounts"
  input:
  file 'list.txt' from file_def
  file('mzML/*') from combined_channel_normal.collect()
  output:
	file("Quandenser_output/consensus_spectra/**") into spectra_normal
	file "Quandenser_output/*" into quandenser_out_normal
  when:
    params.workflow == "Full" && params.parallell_quandenser == false
  script:
	"""
	quandenser --batch list.txt --max-missing ${params.max_missing} ${params.quandenser_additional_arguments}
	"""
}

process quandenser_parallell_1 {
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/*"
  containerOptions "$params.custom_mounts"
  input:
   file 'list.txt' from file_def
   file('mzML/*') from combined_channel_parallell_1
  output:
	 file "Quandenser_output/dinosaur/*" into quandenser_out_1
  when:
    params.workflow == "Full" && params.parallell_quandenser == true
  script:
	"""
  cp -L list.txt modified_list.txt  # Need to copy not link, but a copy of file which I can modify
  filename=\$(find mzML/* | xargs basename)
  sed -i "/\$filename/!d" modified_list.txt
  quandenser-modified --batch modified_list.txt --max-missing ${params.max_missing} --parallell-1 true ${params.quandenser_additional_arguments}
	"""
}

process quandenser_parallell_end {
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/*"
  containerOptions "$params.custom_mounts"
  input:
   file 'list.txt' from file_def
   file('mzML/*') from combined_channel_parallell_2.collect()
   file('Quandenser_output/dinosaur/*') from quandenser_out_1.collect()
  output:
	 file("Quandenser_output/consensus_spectra/**") into spectra_parallell
	 file "Quandenser_output/*" into quandenser_out_parallell
  when:
    params.workflow == "Full" && params.parallell_quandenser == true
  script:
	"""
	quandenser --batch list.txt --max-missing ${params.max_missing} ${params.quandenser_additional_arguments}
	"""
}

// Mix quandenser_out
c1 = quandenser_out_normal
c2 = quandenser_out_parallell
quandenser_out = c1.concat(c2)

// Mix spectra
c1 = spectra_normal
c2 = spectra_parallell
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
