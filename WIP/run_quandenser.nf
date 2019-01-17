#!/usr/bin/env nextflow
echo true

/* Important:
change the path to where the database is and the batch file is
*/
params.db = "/media/hdd/timothy/MSfiles/iprg2016_with_labels.fasta"
params.batch_file = "/media/hdd/timothy/MSfiles/file_list.txt"
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
	file "Quandenser_output/consensus_spectra/MaRaCluster.consensus.part1.ms2" into spectra
	file "Quandenser_output/*" into quandenser_out
  script:
	"""
	quandenser --batch list.txt --max-missing 3 --dinosaur-memory 16G
	"""
}

