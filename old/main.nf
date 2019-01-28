#!/usr/bin/env nextflow

echo true

params.db = "/media/hdd/timothy/MSfiles/iprg2016_with_labels.fasta"
params.file_def = "/media/hdd/timothy/MSfiles/file_list.txt"

db = file(params.db)
seq_index_name = "${db.getName()}.index"
file_def = file(params.file_def)

Channel
  .from(file_def.readLines())
  .map { it -> it.tokenize('\t') }
  .map { it -> file(it[0]) }
  .into{ spectra_in; spectra_in_q }
 

process quandense {
  publishDir ".", mode: 'copy', overwrite: true,  pattern: "Quandenser_output/*"
  input:
	file 'list.txt' from file_def
	file('mzML/*') from spectra_in.collect() 
  output:
	file "Quandenser_output/consensus_spectra/MaRaCluster.consensus.part1.ms2" into spectra
	file "Quandenser_output/*" into quandenser_out
  script:
	"""
	quandenser --batch list.txt --max-missing 3 --dinosaur-memory 16G
	"""
}

process tide_indexing {
  input:
	file 'seqdb.fa' from db
  output:
	file "${seq_index_name}/*" into db_index
  script:
	"""
	crux tide-index --missed-cleavages 2 --mods-spec 2M+15.9949 --decoy-format protein-reverse seqdb.fa ${seq_index_name}
	"""
}

process tide_perc_search {
  publishDir ".", mode: 'copy', pattern: "crux-output/*", overwrite: true 
  input:
	file("${seq_index_name}/*") from db_index.collect()
	file "spec.ms2"  from spectra
  output:
	file("crux-output/*") into id_files
  script:
	"""
	echo "${seq_index_name}"
	crux tide-search --precursor-window 20 --precursor-window-type ppm --overwrite T --concat T spec.ms2 *.index
	crux percolator --top-match 1 crux-output/tide-search.txt
     	"""
}

process triqle {
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
