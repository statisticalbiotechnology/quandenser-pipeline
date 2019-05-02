import xml.etree.ElementTree as ET
import glob
import argparse
import numpy as np
import multiprocessing
from multiprocessing import Pool, Process, Queue, freeze_support, RLock
from multiprocessing.pool import ThreadPool
import sys
import shutil
import os
import re
import zlib
import pdb
import time
import copy
import math
import base64

# Parser
parser = argparse.ArgumentParser()
parser.add_argument("dir",
                    help="Directory to boxcar mzML files")
parser.add_argument('--verbose',
                    action='store_true',
                    help='Show progressbar')
parser.add_argument('-p',
                    default='parallel',
                    nargs='?',
                    help="""Parallel type.
                    non-parallel: no parallelization = low ram usage (default)
                    parallel: Regular parallel, each file is run in parallel = medium ram usage""")
parser.add_argument('-c',
                    type=int,
                    default=multiprocessing.cpu_count(),
                    help="""Amount of parallel processes (defaults to amount of cores in system)""")
parser.add_argument('--exclude',
                    default='',
                    nargs='?',
                    help="""Exclude files with substring""")
parser.add_argument('-m',
                    '--merge',
                    default='sliding_window',
                    help="""Merging method.
                    sliding_window: Slow but higher resolution and no overlaps (default)
                    merge_and_sort: Very fast but overlaps exist. Will not use ms1 spectra
                    matrix_merge: Medium speed, will merge with a custom algorithm""")
parser.add_argument('-s',
                    "--window_size",
                    type=int,
                    default=2,
                    help="""Sliding window range (defaults to 2 m/z)""")
args = parser.parse_args()

if args.verbose:
    try:
        import tqdm
    except:
        print("tqdm not found. Disabling verbosity")
        args.verbose = False

def main():
    assert(args.p in ['non-parallel', 'parallel'])
    assert(args.merge in ['sliding_window', 'merge_and_sort', 'matrix_merge'])
    files = glob.glob(f"{args.dir}/*.mzML")
    files = list(files)
    if args.exclude != '':
        files_remove = [i for i in files if args.exclude in i]  # REMOVE!!
        files = [i for i in files if i not in files_remove]
    files = [(id+1, file) for (id, file) in enumerate(files)]
    start_time = time.time()
    if args.p == 'non-parallel':
        for id, file in files:
            start_convert((id, file))
    elif args.p == 'parallel':
        if args.verbose: p = Pool(args.c, initializer=tqdm.tqdm.set_lock, initargs=(RLock(),))
        else: p = Pool(args.c)
        p.map(start_convert, files)
    end_time = time.time()
    print('\n')
    print("It took {0} seconds".format(round(end_time-start_time, 2)))

def start_convert(t):
    id = t[0]
    file = t[1]
    start_time = time.time()
    # Fix file parameters
    new_directory = os.path.dirname(file) + '/boxcar_converted'
    if not os.path.exists(new_directory):
        os.mkdir(new_directory)
    new_filename = new_directory + '/' + os.path.basename(file)

    """Main conversion function"""
    if args.verbose: progress = tqdm.tqdm(total=4, desc='Loading mzML (1/4)', postfix=os.path.basename(file), position=id)
    # Fix spectrum
    tree, mapped_spectra = parse_mzML(file)

    # Check if non boxcar file, no need to change anything
    if not check_if_boxcar(mapped_spectra):
        shutil.copyfile(file, new_filename)
        if args.verbose: progress.desc=f'Done. Elapsed {round(time.time()-start_time,2)} seconds'; progress.update(4)
        return 0

    mapped_spectra_filtered = merge_spectra(file, mapped_spectra, id=id)

    fix_spectrum_indices(mapped_spectra_filtered)
    spectrumList = find_spectraList(tree.getroot())
    modify_spectrumList(spectrumList, mapped_spectra_filtered)

    # Fix indexlist
    spectrum_indexList = find_indexList(tree.getroot())[0]
    fix_offsets(spectrum_indexList, mapped_spectra_filtered, tree, file=os.path.basename(file), id=id)

    # Create file
    if args.verbose: progress.desc='Writing mzML (4/4)'; progress.update(3)
    new_filename = new_directory + '/' + os.path.basename(file)
    with open(file) as input_file:
        first_line = input_file.readline()
    with open(new_filename, 'w') as output_file:
        output_file.write(first_line + ET.tostring(tree.getroot()).decode('utf-8'))
    if args.verbose: progress.desc=f'Done. Elapsed {round(time.time()-start_time,2)} seconds'; progress.update(1)

def parse_mzML(file):
    """Parses mzml and extracts useful data"""
    """Input: mzml file name (string)
    Output: list with all spectrum"""
    # Find where header starts/ends
    start_index = 0
    for i, line in enumerate(open(file, 'r')):
        if "<run" in line:
            start_index = i
            break
    assert(start_index != 0)
    tree = ET.parse(file)
    tree = clear_namespace(tree)  # Remove bad tags
    root = tree.getroot()  # second line, indexedmzML
    spectrumList = find_spectraList(root)
    amount_of_spectrum = spectrumList.attrib['count']
    all_spectrum = [i for i in spectrumList]  # Extract spectrum
    mapped_spectra = []
    for i in all_spectrum:
        mapped_spectra.append(map_spectrum(i))
    return tree, mapped_spectra

def merge_spectra(file, mapped_spectra, id=0):
    """Filters and merges spectra to use"""
    ms1_scan = 0
    msx_scan = 0
    ms2_scan = 0
    output_spectra = []
    ms1_spectra = []
    amount_of_spectrum = len(mapped_spectra)
    if args.verbose: progress = tqdm.tqdm(total=amount_of_spectrum, desc='Parsing spectrum (2/4)', postfix=os.path.basename(file), position=id)

    for index, spectrum in enumerate(mapped_spectra):
        parameters = spectrum.parameters
        if "Full ms " in parameters['filter string']:
            ms1_scan += 1
            ms1_spectra.append(spectrum)
        elif "Full msx " in parameters['filter string']:
            msx_scan += 1
            ms1_spectra.append(spectrum)
        elif "Full ms2 " in parameters['filter string']:
            ms2_scan += 1
            if check_if_boxcar(ms1_spectra) and ms1_spectra != []:
                combined = check_missing_ms2(ms1_spectra)
                for match in combined:
                    #merged_ms1 = merge_channels(match)
                    output_spectra.append(match[0])
                    saved_ms1 = match[0] # Will always be the latest ms1
            elif ms1_spectra != []:
                ms1_spectra = filter_spectra(ms1_spectra, filter_boxcar=True)
                output_spectra.extend(ms1_spectra)  # Could be multiple MS1
                saved_ms1 = ms1_spectra[-1]  # Will always be the latest ms1
            spectrum.change_precursor_spectrumRef(saved_ms1)
            output_spectra.append(spectrum)  # THIS IS MS2 spectra
            ms1_spectra = []
        else:
            print("ERROR: Something wrong in the filter string in spectrum {}".format(index))
            quit()
        if args.verbose: progress.update(1)
    if args.verbose: progress.close()  # Do not close
    if args.verbose and 1 == 0:
        progress.close()
        print("In file {0}, ms1 scans {1}, msx scans {2}, ms2 scans {3}".format(
        file, ms1_scan, msx_scan, ms2_scan
        ))
    return output_spectra

def merge_channels(spectrum_list):
    """Merges spectra"""
    intensity_arrays = []
    mz_arrays = []
    for index, spectrum in enumerate(spectrum_list):
        intensity = np.array(spectrum.parameters['intensity array'])
        mz = np.array(spectrum.parameters['m/z array'])
        mz_arrays.append(mz)
        intensity_arrays.append(intensity)

    if args.merge == 'sliding_window':
        merged_mz, merged_intensity = sliding_window(mz_arrays,
                                                     intensity_arrays)
    elif args.merge == 'matrix_merge':
        merged_mz, merged_intensity = matrix_merge(mz_arrays,
                                                   intensity_arrays)
    elif args.merge == 'merge_and_sort':
        mz_arrays.pop(0); intensity_arrays.pop(0)  # Remove ms1
        merged_mz, merged_intensity = merge_and_sort(mz_arrays,
                                                     intensity_arrays)
    new_spectrum = Spectrum()
    new_spectrum.parse_xml(copy.deepcopy(spectrum_list[0].spectrum_xml))  # Use first spectrum as template
    new_spectrum.parameters['intensity array'] = merged_intensity
    new_spectrum.parameters['m/z array'] = merged_mz
    new_spectrum.modify_xml()
    return new_spectrum  # Needs to be in list

def sliding_window(mz_arrays, intensity_arrays):
    merged_mz = []
    merged_intensity = []
    #channels = []
    window_size = args.window_size
    min_mz = min([item for sublist in mz_arrays for item in sublist])  # Min in all arrays
    max_mz = max([item for sublist in mz_arrays for item in sublist])  # Max in all arrays
    slide_start = int(math.floor(min_mz/5.0)*5.0)  # Round to closest 5
    slide_end = int(math.ceil(max_mz/5.0)*5.0)  # Round to closest 5
    while True:
        mz_range = (slide_start, slide_start + window_size)
        chunks = []
        for mz, i in zip(mz_arrays, intensity_arrays):
            chunk = getchunk(mz_range, mz, i)
            chunks.append(chunk)
        sum_intensities = [sum(i[1]) for i in chunks]
        if any([i[0] != [] for i in chunks[1:]]):
            sum_intensities[0] = 0  # Remove first
        channel = sum_intensities.index(max(sum_intensities))
        merged_mz.extend(chunks[channel][0])  # mz
        merged_intensity.extend(chunks[channel][1])  # intensity
        #channels.append(channel)
        slide_start += window_size
        if slide_start >= slide_end:
            break
    #plt.plot(channels)
    #plt.show()
    merged_mz = np.array(merged_mz)
    merged_intensity = np.array(merged_intensity)
    return merged_mz, merged_intensity

def merge_and_sort(mz_arrays, intensity_arrays):
    merged_mz_array, merged_i_array = mz_arrays[0], intensity_arrays[0]
    for mz, i in zip(mz_arrays[1:], intensity_arrays[1:]):
        merged_mz_array = np.append(merged_mz_array, mz)
        merged_i_array = np.append(merged_i_array, i)
    sort_indices = np.argsort(merged_mz_array)
    merged_mz = merged_mz_array[sort_indices]
    merged_intensity = merged_i_array[sort_indices]
    # Optional, clear very low intensities
    merged_mz, merged_intensity = remove_low_intensities(merged_mz, merged_intensity)
    return merged_mz, merged_intensity

def matrix_merge(mz_arrays, intensity_arrays):
    merged_mz, merged_intensity = merge_and_sort(mz_arrays, intensity_arrays)
    return merged_mz, merged_intensity

def sum_chunk(mz_range, mz, intensity):
    i_sum = 0
    for index, mz_value in enumerate(mz):
        if mz_range[0] <= mz_value <= mz_range[1]:
            i_sum += mz_value
        elif mz_value > mz_range[1]:
            break
    return i_sum

def getchunk(mz_range, mz, intensity):
    mz_chunk = []
    intensity_chunk = []
    for index, mz_value in enumerate(mz):
        if mz_range[0] <= mz_value <= mz_range[1]:
            mz_chunk.append(mz[index])
            intensity_chunk.append(intensity[index])
        elif mz_value > mz_range[1]:
            break
    return mz_chunk, intensity_chunk

def merged_boxcar_to_ms1(ms1, merged_boxcar):
    intensity = merged_boxcar.parameters['intensity array']
    mz = merged_boxcar.parameters['m/z array']
    ms1.parameters['intensity array'] = intensity
    ms1.parameters['m/z array'] = mz
    ms1.modify_xml()

def fix_spectrum_indices(spectrum_list):
    """All indices has to be in order. This functions fixes that"""
    for index, spectrum in enumerate(spectrum_list):
        spectrum.change_xml_index(index)

def remove_low_intensities(mz, intensity):
    """Finds boxcar boundaries and puts everything outside to 0"""
    indices = []
    for index, i in enumerate(intensity):
        if abs(i) < 2000:  # Clear very low peaks
            indices.append(index)
    indices = list(set(indices))  # Remove duplicates
    mz = np.delete(mz, indices)
    intensity = np.delete(intensity, indices)
    return mz, intensity

def filter_spectra(spectrum_list, filter_boxcar=False):
    """Filters boxcar spectrum in a list of  spectrums"""
    boxcar = []
    ms1 = []
    for spectrum in spectrum_list:
        if "Full msx " in spectrum.parameters['filter string']:
            boxcar.append(spectrum)
        else:
            ms1.append(spectrum)
    if filter_boxcar:
        return ms1
    else:
        return boxcar

def check_missing_ms2(ms1_spectra):
    """If there are two full ms1 scans, there are missing ms2,
    split boxcar spectra to prevent overlapping ms1.
    You can either discard them or use them either way."""
    output_matrix = []
    output_list = []
    ms1_found = False
    for spectrum in ms1_spectra:
        if "Full ms " in spectrum.parameters['filter string'] and ms1_found == False:
            ms1_found = True
        elif "Full ms " in spectrum.parameters['filter string']:
            output_matrix.append(output_list)
            output_list = []  # Reset
            ms1_found = False
        output_list.append(spectrum)
    output_matrix.append(output_list)
    # Discard the previous run with missing ms2
    output_matrix = [output_matrix[-1]]
    return output_matrix

def check_if_boxcar(spectrum_list):
    """Simple function to check if boxcar exists in spectrum list"""
    for spectrum in spectrum_list:
        if "Full msx " in spectrum.parameters['filter string']:
            return True
    return False

def map_spectrum(spectrum):
    """ Input: xml spectrum tag
    Output: Spectrum class with all values"""
    spectrum_class = Spectrum()
    spectrum_class.parse_xml(spectrum)
    return spectrum_class

def clear_namespace(tree):
    """ PROBLEM: tags are in this format:'
    {url}tag
    ex: {http://psi.hupo.org/ms/mzml}indexedmzML
    This clears all the namespaces, which are not really needed
    """
    for element in tree.iter():
        if '}' in element.tag:
            element.tag = element.tag.split('}')[1]  # strip all namespaces
    return tree

def find_spectraList(root):
    """Goes stepwise in xml to find spectrumlist"""
    root_mzml = root.findall('mzML')[0]
    root_lists = root_mzml.findall('run')[0]
    root_spectra = root_lists.findall('spectrumList')[0]
    return root_spectra

def find_indexList(root):
    root_indexList = root.findall('indexList')[0]
    root_index = root_indexList.findall('index')  # 2 index, first is for spectrum, second is chromatogram
    return root_index

def modify_spectrumList(spectrumList, new_spectra):
    """Clears all spectra and replaces it with the "new" spectra"""
    # Remove old spectra
    all_spectrum = spectrumList.findall('spectrum')
    for spectrum in list(all_spectrum):
        spectrumList.remove(spectrum)
    # Replace with new spectra
    spectrumList.attrib['count'] = str(len(new_spectra))
    for spectrum in new_spectra:
        spectrumList.append(spectrum.spectrum_xml)

def fix_offsets(spectrum_indexList, spectrum_list, tree, file="", id=0):
    """Fix pointers at the end of mzML file"""
    if args.verbose: progress = tqdm.tqdm(total=4, desc='Modifying pointers (3/4)', postfix=os.path.basename(file), position=id)
    # Clear unused offsets
    all_offsets = spectrum_indexList.findall('offset')
    used_offsets = [s.parameters['id'] for s in spectrum_list]
    offset_templates = [list(all_offsets)[0]]*len(used_offsets)
    for offset in list(all_offsets):  # Copy
        spectrum_indexList.remove(offset)
    for offset, offset_id in zip (offset_templates, used_offsets):
        offset = copy.deepcopy(offset)
        offset.attrib['idRef'] = offset_id
        spectrum_indexList.append(offset)
    if args.verbose: progress.update(1)

    # Fix pointers for spectrum
    indices = [m.start() for m in re.finditer('<spectrum ', ET.tostring(tree.getroot()).decode('utf-8'))]
    all_offsets = spectrum_indexList.findall('offset')
    for distance, offset in zip(indices, all_offsets):  # Do not copy
        offset.text = str(distance)
    if args.verbose: progress.update(1)

    # Not really needed tbh....
    # Fix chromatogram
    chromatogram_indexList = find_indexList(tree.getroot())[1]
    indices = [m.start() for m in re.finditer('<chromatogram ', ET.tostring(tree.getroot()).decode('utf-8'))]
    all_chromatograms = chromatogram_indexList.findall('offset')
    for distance, offset in zip(indices, all_chromatograms):  # Do not copy
        offset.text = str(distance)
    if args.verbose: progress.update(1)

    # Fix indexlist
    root = tree.getroot()
    indexListOffset = root.findall('indexListOffset')[0]
    indices = [m.start() for m in re.finditer('<indexListOffset>', ET.tostring(tree.getroot()).decode('utf-8'))]
    indexListOffset.text = str(indices[0])
    if args.verbose: progress.update(1)

"""This could be in a different file, but that will only make things more complicated when putting it into the image..."""
class Spectrum():
    def __init__(self):
        self.parameters = {}

    def parse_xml(self, spectrum_xml):
        """Parse xml and store everything in a dict"""
        self.spectrum_xml = spectrum_xml
        header = spectrum_xml.attrib
        self.parameters['index'] = header['index']
        self.parameters['id'] = header['id']
        self.parameters['defaultArrayLength'] = header['defaultArrayLength']
        array_list = False  # True when we are inside array list
        zlib_compression = False
        for element in spectrum_xml.iter():  # Ignore tree structure
            if element.tag == 'cvParam' and array_list == False:
                name = element.attrib['name']  # Here, it tells us what is inside the params
                self.parameters[name] = element.attrib['value']
            elif element.tag == 'cvParam' and array_list == True:
                name = element.attrib['name']
                match = re.search("([0-9]+)-bit float", name)
                if match is not None:
                    encoding = match.group(1)
                elif name == 'intensity array':
                    array_type = 'intensity array'
                elif name == 'm/z array':
                    array_type = 'm/z array'
                elif name == 'zlib compression':
                    zlib_compression = True
            elif element.tag == 'binaryDataArrayList':
                self.parameters['binaryDataArrayList'] = element.attrib['count']
                amount_of_arrays = int(element.attrib['count'])
                array_list = True
            elif element.tag == 'binary':
                binary = element.text
                if encoding == '64':
                    decoded = base64.b64decode(binary)
                    dtype = 'float64'
                elif encoding == '32':
                    decoded = base64.b64decode(binary)
                    dtype = 'float32'
                if zlib_compression:
                    decoded = zlib.decompress(decoded)
                array = np.frombuffer(decoded, dtype=dtype)
                self.parameters[array_type] = array

    def modify_xml(self):
        # Set parameters, which will be fixed in cvParam
        self.parameters['lowest observed m/z'] = str(min(self.parameters['m/z array']))
        self.parameters['highest observed m/z'] = str(max(self.parameters['m/z array']))
        self.parameters['base peak intensity'] = "{:.8e}".format(max(self.parameters['intensity array'])).replace('+', '')
        self.parameters['base peak m/z'] = str(self.parameters['m/z array'][np.argmax(self.parameters['intensity array'])])
        self.parameters['total ion current'] = "{:.8e}".format(sum(self.parameters['intensity array'])).replace('+', '')
        self.parameters['scan window lower limit'] = str(int(5 * round(float(self.parameters['lowest observed m/z'])/5)))
        self.parameters['scan window upper limit'] = str(int(5 * round(float(self.parameters['highest observed m/z'])/5)))

        # header
        self.spectrum_xml.attrib['defaultArrayLength'] = str(self.parameters['intensity array'].shape[0])
        array_list = False
        zlib_compression = False
        encoded_lengths = []
        for element in self.spectrum_xml.iter():  # Ignore tree structure
            if element.tag == 'cvParam' and array_list == False:
                name = element.attrib['name']  # Here, it tells us what is inside the params
                element.attrib['value'] = self.parameters[name]
            elif element.tag == 'cvParam' and array_list == True:
                name = element.attrib['name']
                match = re.search("([0-9]+)-bit float", name)
                if match is not None:
                    encoding = match.group(1)
                elif name == 'intensity array':
                    array_type = 'intensity array'
                elif name == 'm/z array':
                    array_type = 'm/z array'
                elif name == 'zlib compression':
                    zlib_compression = True
            elif element.tag == 'binaryDataArrayList':
                amount_of_arrays = int(element.attrib['count'])
                array_list = True
            elif element.tag == 'binary':
                array = self.parameters[array_type]
                binary = array.tobytes()
                if zlib_compression:
                    binary = zlib.compress(binary)
                encoded = base64.b64encode(binary)
                encoded = encoded.decode("utf-8")
                element.text = encoded
                encoded_lengths.append(len(encoded))

        array_count = 0
        for element in self.spectrum_xml.iter():
            if element.tag == 'binaryDataArray':
                element.attrib['encodedLength'] = str(encoded_lengths[array_count])
                array_count += 1

    def change_xml_index(self, index):
        self.spectrum_xml.attrib['index'] = str(index)
        self.parameters['index'] = str(index)

    def change_precursor_spectrumRef(self, referenceSpectrum):  # Only ms2
        for element in self.spectrum_xml.iter():
            if element.tag == 'precursor':
                element.attrib['spectrumRef'] = referenceSpectrum.spectrum_xml.attrib['id']
                return


if __name__ == '__main__':
    freeze_support()  # Windows support
    main()
