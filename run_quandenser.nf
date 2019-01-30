#!/usr/bin/env nextflow
echo true

/* Important:
change the path to where the database is and the batch file is
*/
db = file(params.db)  // Sets "db" as the file defined above
file_def = file(params.batch_file)  // batch_file
seq_index_name = "${db.getName()}.index"  // appends "index" to the db filename

Channel
  .from(file_def.readLines())
  .map { it -> it.tokenize('\t') }
  .filter{ it.size() > 1 }  // filters any input that is not <path> <X>
  .map { it -> file(it[0]) }
  .into{ spectra_in; spectra_in_q }

process quandenser {
  publishDir ".", mode: 'copy', overwrite: true,  pattern: "Quandenser_output/*"
  input:
	file 'list.txt' from file_def
	file('mzML/*') from spectra_in.collect()   // spectra_in_q for parallel run
  output:
	file("Quandenser_output/consensus_spectra/**") into spectra
	file "Quandenser_output/*" into quandenser_out
  script:
	"""
	quandenser --batch list.txt --max-missing 3 --dinosaur-memory 16G
	"""
}

/*
process test {
  input:
  file ms2_files from Channel.fromPath("/media/storage/timothy/quandenser-pipeline/WIP/Quandenser_output/consensus_spectra/*")
  file q_out from Channel.fromPath("/media/storage/timothy/quandenser-pipeline/WIP/Quandenser_output/*")
  output:
  file ms2_files into spectra
  file q_out into quandenser_out
  """
  echo Done
  """
}
*/

process tide_perc_search {
  publishDir ".", mode: 'copy', pattern: "crux-output/*", overwrite: true
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
  publishDir ".", mode: 'copy', pattern: "proteins.*",overwrite: true
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
