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
            filenames.append(os.path.join(folder, filename))

    return set(filenames)


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
            to_write.append(' sp '.join(words))

    # add silence ({SL}) between phrases = lines
    to_write = ' {SL} '.join(to_write)

    # write to temp file
    temp_file = open('./temp', 'w')
    temp_file.write(to_write)
    temp_file.close()

    # return the temp filename
    return os.path.abspath("./temp")


def get_cl_args():
    """
    Gets the command line inputs
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--p2fa-dir', '-p', type=str, required=True,
       help='folder where the p2fa align library https://www.ling.upenn.edu/phonetics/old_website_2015/p2fa/ is found.')

    parser.add_argument('--audio-dir', '-a', type=str, required=True,
        help="folder where audio is stored. Note filenames must match")

    cl_args = vars(parser.parse_args())

    p2fa = cl_args['p2fa_dir']
    audio_dir = cl_args['audio_dir']

    return p2fa, audio_dir


def get_audio_filename(filename, audio_filenames):
    # gets a matching audio filename from a lyric filename
    local_name = os.path.splitext(os.path.split(filename)[-1])[0]

    # search through audio_filenames
    matches = [x for x in audio_filenames if local_name in x]

    # must be only 1 match
    assert len(matches) == 1
    return matches[0]


def do_alignment(lyric_file, audio_file, align_dir):
    # we'll do this via a sys call
    command = ['python', 'align.py', audio_file, lyric_file, 'temp_aligned']

    # do the alignment
    call(command)

    # return the filename of the output
    return os.path.join(align_dir, 'temp_aligned')


def format_alignment(raw_alignment):
    """
    Opens up a raw alignment, and formats it
    """

    # open the file lines, strip newlines
    lines = open(raw_alignment, 'r').readlines()
    lines = [l.strip() for l in lines]

    # hacky - put in a sep string so we can deal with
    # one large string
    lines = '***SEP***'.join(lines)

    # split this large string into header, phones, words

    # must be exactly 3
    x = lines.split("IntervalTier")
    assert len(x) == 3
    header, phones, words = x

    # split them again, skipping subheader (hacky!)
    phones = phones.split('***SEP***')
    phones = phones[5:]

    words = words.split('***SEP***')
    words = words[5:]

    # take every 3rd entry for the start, end, text
    start_phone, end_phone, phones = phones[::3], phones[1::3], phones[2::3]

    # blerg, some empty strings have crept in
    start_phone = [s for s in start_phone if s != '"']

    # remove quotes either side of word. hacky
    phones = [p[1:-1] for p in phones]

    # check everything is legit
    assert len(start_phone) == len(end_phone)
    assert len(end_phone) == len(phones)

    # zip them up
    return zip(phones, start_phone, end_phone)


def write_alignment(alignment, lyric_filename):
    """
    Writes an alignment in lab format
    """

    # we use the same subfolder structure (Train/Sing/file) etc. Need to get them
    path_bits = lyric_filename.split(os.sep)
    if path_bits[-3] == 'Train':
        output_filename = os.path.join(ALIGNED_DIR, 'Train')
    elif path_bits[-3] == 'Test':
        output_filename = os.path.join(ALIGNED_DIR, 'Test')
    elif path_bits[-4] == 'Holdout':
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
    output_filename = os.path.join(output_filename, local_name)

    # write
    with open(output_filename, 'w') as f:
        for line in alignment:
            x, start, end = line
            f.write(x + ' ')
            f.write(start + ' ')
            f.write(end + '\n')


if __name__ == "__main__":

    # add the align directory to the path
    align_dir, audio_dir = get_cl_args()

    if align_dir not in sys.path:
        sys.path.append(align_dir)

    current_path = os.getcwd()

    # re-format according to format on this blog:
    # http://linguisticmystic.com/2014/02/12/penn-forced-aligner-on-mac-os-x/
    lyric_filenames = get_filenames(LYRICS_DIR)
    audio_filenames = get_filenames(audio_dir)

    for lyric_filename in lyric_filenames:
        print lyric_filename
        # prep the file
        prepped_lyric_file = prep_filename(lyric_filename)

        # do the alignment. first cd into the dir
        os.chdir(align_dir)

        # now get the filename of the audio
        audio_filename = get_audio_filename(lyric_filename, audio_filenames)

        # now do the alignment
        raw_alignment = do_alignment(prepped_lyric_file, audio_filename, align_dir)

        # read and re-format
        formatted_output = format_alignment(raw_alignment)

        os.chdir(current_path)

        # write alignment
        write_alignment(formatted_output, lyric_filename)
