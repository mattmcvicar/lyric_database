import os
import argparse
import sys
from subprocess import call

# Globals
LYRICS_DIR = './lyrics'
ALIGNED_DIR = './aligned'
EXCLUDE = [',', '?', '!']


def get_filenames(root):
    # get all filenames
    filenames = []
    for folder, subFolders, files in os.walk(root):
        for filename in files:
            # Mac OSX BS
            if '.DS_Store' in filename:
                continue

            if "Holdout" in folder:
                continue

            filenames.append(os.path.join(folder, filename))

    return list(set(filenames))


def prep_filename(filename):
    # read in lines
    to_write = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # skipping blank lines and structural annotations
            if len(line) == 0 or line.startswith('['):
                continue

            # keep only good chars
            line = ''.join(ch for ch in line if ch not in EXCLUDE)
            words = line.upper().strip().split()

            # we insert "short pause" (sp) between words
            to_write.append(' '.join(words))

    # add silence ({SL}) between phrases = lines
    to_write = ' '.join(to_write)

    # write to temp file
    temp_file = open('./unaligned_file', 'w')
    temp_file.write(to_write)
    temp_file.close()


def get_cl_args():
    """
    Gets the command line inputs
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--audio-dir', '-a', type=str, required=True,
        help="folder where audio is stored. Note filenames must match")

    cl_args = vars(parser.parse_args())

    return cl_args['audio_dir']


def get_audio_filename(filename, audio_filenames):
    # gets a matching audio filename from a lyric filename
    local_name = os.path.splitext(os.path.split(filename)[-1])[0]

    # search through audio_filenames
    matches = [x for x in audio_filenames if local_name in x]

    # must be only 1 match
    assert len(matches) == 1
    return matches[0]


def do_alignment(audio_file):
    # we'll do this via a sys call
    command = ['python', 'align.py', audio_file, './unaligned_file', './aligned_file']

    # do the alignment
    call(command)


def format_alignment():
    """
    Opens up a raw alignment, and formats it
    """

    # open the file lines, strip newlines
    lines = open('./aligned_file', 'r').readlines()
    lines = [l.strip() for l in lines]

    # first line tells us how many phones
    n_phones = int(lines[0])
    phones = lines[:n_phones * 3]

    words = lines[n_phones * 3 + 1:-1]

    # take every 3rd entry for the start, end, text
    phone, start_phone, end_phone = phones[::3], phones[1::3], phones[2::3]
    word, start_word, end_word = words[::3], words[1::3], words[2::3]

    # zip them up
    return zip(phone, start_phone, end_phone), zip(word, start_word, end_word)


def write_alignment(alignment, lyric_filename, ext):
    """
    Writes an alignment in lab format
    """

    # we use the same subfolder structure (Train/Sing/file) etc. Need to get them
    path_bits = lyric_filename.split(os.sep)
    if path_bits[-3] == 'Train':
        output_filename = os.path.join(ALIGNED_DIR, 'Train')
    elif path_bits[-3] == 'Test':
        output_filename = os.path.join(ALIGNED_DIR, 'Test')
    elif path_bits[-3] == 'Holdout':
        output_filename = os.path.join(ALIGNED_DIR, 'Holdout')
    else:
        raise ValueError("Badly formed directory")

    if path_bits[-2] == 'Sing':
        output_filename = os.path.join(output_filename, "Sing")
    elif path_bits[-2] == 'Rap':
        output_filename = os.path.join(output_filename, "Rap")
    else:
        raise ValueError("Badly formed directory")

    # make dir if needed
    if not os.path.exists(output_filename):
        os.makedirs(output_filename)

    # add in name
    local_name = os.path.splitext(path_bits[-1])[0]
    output_filename = os.path.join(output_filename, local_name) + ext

    # write
    with open(output_filename, 'w') as f:
        for line in alignment:
            x, start, end = line
            f.write(x + ' ')
            f.write(start + ' ')
            f.write(end + '\n')


def tidy():
    os.system("rm unaligned_file")
    os.system("rm aligned_file")

if __name__ == "__main__":

    # add the align directory to the path
    audio_dir = get_cl_args()

    # re-format according to format on this blog:
    # http://linguisticmystic.com/2014/02/12/penn-forced-aligner-on-mac-os-x/
    lyric_filenames = get_filenames(LYRICS_DIR)
    audio_filenames = get_filenames(audio_dir)
    n_files = len(lyric_filenames)

    print ''
    for ifile, lyric_filename in enumerate(lyric_filenames):

        print '  working on file', ifile + 1, 'of', n_files, '-', lyric_filename

        try:
            # prep the file
            prep_filename(lyric_filename)

            # now get the filename of the audio
            audio_filename = get_audio_filename(lyric_filename, audio_filenames)

            # now do the alignment
            do_alignment(audio_filename)

            # read and re-format
            phones, words = format_alignment()

            # write alignment
            write_alignment(phones, lyric_filename, '.phones')
            write_alignment(words, lyric_filename, '.words')

            tidy()
        except:
            pass
