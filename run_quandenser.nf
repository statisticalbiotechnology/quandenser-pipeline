#!/usr/bin/env nextflow
echo true

/* Important:
change the path to where the database is and the batch file is
*/
db = file(params.db)  // Sets "db" as the file defined above
file_def = file(params.batch_file)  // batch_file
seq_index_name = "${db.getName()}.index"  // appends "index" to the db filename

// Preprocessing file_list
Channel  // Files to run
  .from(file_def.readLines())
  .map { it -> it.tokenize('\t') }
  .filter{ it.size() > 1 }  // filters any input that is not <path> <X>
  .filter{ it[0].tokenize('.')[-1] == "mzML" }  // filters any input that is not .mzML
  .map { it -> file(it[0]) }
  .into{ spectra_in; spectra_in_q }  // Puts the files into spectra_in

Channel  // Files to convert
  .from(file_def.readLines())
  .map { it -> it.tokenize('\t') }
  .filter{ it.size() > 1 }  // filters any input that is not <path> <X>
  .filter{ it[0].tokenize('.')[-1] != "mzML" }  // filters any input that is .mzML
  .map { it -> file(it[0]) }
  .into{ spectra_convert; spectra_convert_bool }

// Replaces the lines in the batchfile with the new paths
count = 0
amount_of_non_mzML = 0
all_lines = file_def.readLines()
for( line in all_lines ){
  file_path = line.tokenize('\t')[0]
  file_label = line.tokenize('\t')[-1]
  file_name = (file_path.tokenize('/')[-1]).tokenize('.')[0]  // Split '/', take last. Split '.', take first
  file_extension = file_path.tokenize('.')[-1]
  if( file_extension != "mzML" ){
    all_lines[count] = params.output_path + "/converted/" + file_name + ".mzML" + '\t' + file_label
    count++
    amount_of_non_mzML++
  } else {
    // add as is, no change
    count++
  }
}
file_def.text = ''  // clear file
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
  publishDir "$params.output_path/converted", mode: 'copy', overwrite: true, pattern: "*"
  input:
    file f from spectra_convert_channel
  output:
    file("*mzML") into spectra_converted
  script:
	"""
  wine msconvert ${f} --mzML --zlib
  """
}

c1 = spectra_in
c2 = spectra_converted

combined_channel = c1.concat(c2)

process quandenser {
  publishDir params.output_path, mode: 'copy', overwrite: true,  pattern: "Quandenser_output/*"
  input:
	//
  file 'list.txt' from file_def
  file('mzML/*') from combined_channel.collect()
	//file('mzML/*') from spectra_in.collect()
  //file('mzML/*') from spectra_converted.collect()
  output:
	file("Quandenser_output/consensus_spectra/**") into spectra
	file "Quandenser_output/*" into quandenser_out
  script:
	"""
  #--dinosaur-memory 16G
	quandenser --batch list.txt --max-missing 3
	"""
}

process tide_perc_search {
  publishDir params.output_path, mode: 'copy', pattern: "crux-output/*", overwrite: true
  input:
	file 'seqdb.fa' from db
	file ms2_files from spectra.collect()  // PS: Sentistive to nameing (no blankspace, paranthesis and such)
  output:
	file("crux-output/*") into id_files
  file("${seq_index_name}") into index_files
  script:
	"""
  crux tide-index --missed-cleavages 2 --mods-spec 2M+15.9949 --decoy-format protein-reverse seqdb.fa ${seq_index_name}
	crux tide-search --precursor-window 20 --precursor-window-type ppm --overwrite T --concat T ${ms2_files} ${seq_index_name}
	crux percolator --top-match 1 crux-output/tide-search.txt
  """
}


process triqler {
  publishDir params.output_path, mode: 'copy', pattern: "proteins.*",overwrite: true
  input:
	file("Quandenser_output/*") from quandenser_out.collect()
	file("crux-output/*") from id_files.collect()
	file 'list.txt' from file_def
  output:
	file("proteins.*") into triqler_output
  script:
	"""
	prepare_input.py -l list.txt -f Quandenser_output/Quandenser.feature_groups.tsv -i crux-output/percolator.target.psms.txt,crux-output/percolator.decoy.psms.txt -q triqler_input.tsv
	triqler --fold_change_eval 0.8 triqler_input.tsv
  """
}

triqler_output.flatten().subscribe{ println "Received: " + it.getName() }
