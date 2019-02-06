#!/usr/bin/env nextflow
echo true

file_def = file("file_list.txt")  // batch_file

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
  .into{ spectra_convert; spectra_bool }


// Replaces the lines in the batchfile with the new paths
count = 0
all_lines = file_def.readLines()
for( line in all_lines ){
  file_path = line.tokenize('\t')[0]
  file_label = line.tokenize('\t')[-1]
  file_name = (file_path.tokenize('/')[-1]).tokenize('.')[0]  // Split '/', take last. Split '.', take first
  file_extension = file_path.tokenize('.')[-1]
  if( file_extension != "mzML" ){
    all_lines[count] = params.output_path + "/converted/" + file_name + ".mzML" + '\t' + file_label
    count++
  } else {
    // add as is, no change
    count++
  }
}

file_def.text = ''  // clear file
for( line in all_lines ){
  file_def << line + '\n'  // need to add \n
}

process msconvert {
  publishDir "./converted", mode: 'copy', overwrite: true, pattern: "*"
  input:
	file f from spectra_convert
  output:
  file("*mzML") into converted_files
  when:
    spectra_bool.collect().length() > 1
  script:
	"""
  wine msconvert ${f}s --mzML
  """
}
