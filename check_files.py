import argparse
import os


def get_cl_args():
    """
    Gets the command line arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--audio-folder', '-f', type=str, required=True,
       help='folder of audio files. Each file should have a ".lyrics"'
            'extension')

    cl_args = vars(parser.parse_args())

    audio_root = cl_args['audio_folder']

    return audio_root


def load_dict(filename, comment):
    """
    loads a pronounciation dictionary
    """
    D = dict()
    with open(filename, 'r') as f:
        for line in f:
            if comment and line.startswith(comment):
                continue

            stuff = line.split()

            # split into word and phones
            D[stuff[0]] = stuff[1:]

    return D


def get_filenames(root, ext):
    """
    searches through a directory recursively looking for files which
    end with ext
    """
    filenames = []
    for folder, subFolders, files in os.walk(root):
        # Holdout set is not done yet - comment/delete this
        # to see report for *all* files
        if 'Holdout' in folder:
            continue

        for filename in files:
            if filename.endswith(ext):
                filenames.append(os.path.join(folder, filename))

    return set(filenames)


def get_local_name(p):
    # gets jsut the name, without ext
    return os.path.splitext(os.path.split(l)[-1])[0]


def check_dictionary(pronounciations, phones):
    """
    looks through pronounciations and checks all phones are legit
    """
    for word, pron in pronounciations.items():
        for p in pron:
            if p not in phones:
                print '  WARNING:', word, 'has illegal phone', p


def load_phones(phones_file):
    """
    loads up a phone dictionary
    """
    phones = []
    with open(phones_file, 'r') as f:
        for line in f:
            phones.append(line.strip())

    return phones


def check_words(lyric_names, pronounciations):
    """
    Loads up the lyrics, and checks that every word has a pronounciation.
    Words need some processing
    """
    # we skip these chars. Maybe they should be removed from the data,
    # but they also seem like they could be useful for advanced alignment
    # etc, so keep them for now
    exclude = [',', '?', '!']

    # keep track of any bad words we see
    bad_words = []
    for lyrics_file in lyric_names:
        with open(lyrics_file, 'r') as f:
            for line in f:
                # structural segmentations are like [VERSE]
                if line.startswith('['):
                    continue

                # we kept empty lines for structural information too
                if len(line) == 0:
                    continue

                # keep only the good chars, strip newlines, and split into words
                line = ''.join(ch for ch in line if ch not in exclude)
                w = line.upper().strip().split()

                # check each word
                for ww in w:
                    if ww not in pronounciations and ww not in bad_words:
                        print '  WARNING:', ww, 'in', lyrics_file, 'has no pronounciation'
                        bad_words.append(ww)

    print '  a total of', len(bad_words), 'words with no pronounciation'


if __name__ == "__main__":

    # lyrics folder should be relative to where we are
    lyrics_root = '../lyrics/'

    # get audio folder
    audio_root = get_cl_args()

    # get files for each
    lyrics_names = get_filenames(lyrics_root, 'lyrics')
    audio_names = get_filenames(audio_root, 'wav')

    # check difference
    local_lyrics = set([get_local_name(l) for l in lyrics_names])
    local_audio = set([get_local_name(l) for l in audio_names])

    print ''
    print '  Checking for mismatch of files...'
    differences = local_lyrics.symmetric_difference(local_lyrics)
    for d in differences:
        if d not in lyrics_names:
            print '  WARNING:', d, 'has an audio file but no lyrics'
        else:
            print '  WARNING:', d, 'has a lyrics file but no audio'

    # get word pronounciations
    pronounciations = load_dict('./cmu.dict', ';;;')

    # load phones
    phones = load_phones('./phones')

    # check dictionary
    check_dictionary(pronounciations, phones)

    # load up words
    words = check_words(lyrics_names, pronounciations)

print ''
print '  Everything else looks peachy!'
print '  Done'
print ''
